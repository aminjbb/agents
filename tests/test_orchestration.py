import asyncio
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.store import Store
from helpers import ScriptedAdapter, evidence, task


class OrchestrationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    async def run_request(self, adapter, **options):
        with Store(self.root / "run.json") as store:
            return await Orchestrator(adapter, store).start(
                {"project_root": str(self.root), "text": "@state-master implement the UI request",
                 "mode": "execute", **options})

    async def test_intake_always_architect_and_plan_never_executes(self):
        adapter = ScriptedAdapter()
        state = await self.run_request(adapter, mode="plan")
        self.assertEqual(state["status"], "planned")
        self.assertEqual([(p["agent"], p["operation"]) for p in adapter.calls], [("@architect", "plan")])
        self.assertEqual(adapter.calls[0]["allowed_write_scope"], [])
        self.assertTrue(adapter.calls[0]["definition"]["instruction"])

    async def test_independent_tasks_actually_overlap(self):
        started, peak, active = 0, 0, 0
        barrier = asyncio.Event()

        async def handler(packet):
            nonlocal started, peak, active
            if packet["operation"] == "execute_task":
                started += 1
                active += 1
                peak = max(peak, active)
                if started == 2:
                    barrier.set()
                await asyncio.wait_for(barrier.wait(), 2)
                active -= 1
                return evidence(status="completed", changed_files=[])
        adapter = ScriptedAdapter([task("A", scopes=["src/a/"]), task("B", scopes=["src/b/"])], handler)
        state = await self.run_request(adapter, max_parallel=2)
        self.assertEqual(peak, 2)
        self.assertEqual(state["status"], "simulated")

    async def test_overlapping_writers_are_serialized(self):
        active, peak = 0, 0

        async def handler(packet):
            nonlocal active, peak
            if packet["operation"] == "execute_task":
                active += 1
                peak = max(peak, active)
                await asyncio.sleep(0.02)
                active -= 1
        adapter = ScriptedAdapter([task("A", scopes=["src/UI/"]),
                                   task("B", scopes=["src/ui/button.tsx"])], handler)
        state = await self.run_request(adapter)
        self.assertEqual(peak, 1)
        self.assertEqual(state["status"], "simulated")
        self.assertEqual(state["plan_validation"]["serialized_write_conflicts"], [["A", "B"]])

    async def test_dependency_waits_for_actual_architect_approval(self):
        adapter = ScriptedAdapter([task("B", deps=["A"]), task("A")])
        state = await self.run_request(adapter)
        events = state["events"]
        done = next(e["sequence"] for e in events if e["event"] == "task_result" and e["task_id"] == "A")
        running = next(e["sequence"] for e in events if e["event"] == "task_running" and e["task_id"] == "B")
        self.assertLess(done, running)
        self.assertEqual(state["status"], "simulated")

    async def test_failed_branch_blocks_consumers_but_independent_finishes(self):
        async def handler(packet):
            if packet["operation"] == "execute_task" and packet["context"]["task"]["id"] == "A":
                return {"status": "blocked", "summary": "Missing API contract"}
        state = await self.run_request(ScriptedAdapter(
            [task("C", deps=["B"]), task("B", deps=["A"]), task("A"), task("D")], handler))
        statuses = {t["id"]: t["status"] for t in state["plan"]["tasks"]}
        self.assertEqual(statuses, {"A": "blocked", "B": "blocked", "C": "blocked", "D": "done"})
        self.assertEqual(state["status"], "blocked")

    async def test_failed_required_checks_cannot_be_approved(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                value = evidence(status="completed", changed_files=[])
                value["checks"][0]["status"] = "NOT_RUN"
                return value
        adapter = ScriptedAdapter(handler=handler)
        state = await self.run_request(adapter)
        self.assertEqual(state["status"], "blocked")
        self.assertNotIn("review_task", [p["operation"] for p in adapter.calls])

    async def test_auditor_failure_cannot_be_overridden(self):
        async def handler(packet):
            if packet["operation"] == "review_delivery":
                return evidence(verdict="FAIL")
        state = await self.run_request(ScriptedAdapter(handler=handler))
        self.assertEqual(state["status"], "changes_required")
        self.assertEqual(state["acceptance"]["status"], "approved")

    async def test_out_of_scope_report_is_blocked(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                return evidence(status="completed", changed_files=["src/private.ts"])
        state = await self.run_request(ScriptedAdapter([task(scopes=["src/ui/"])], handler))
        self.assertEqual(state["status"], "blocked")
        self.assertIn("outside declared scope", state["plan"]["tasks"][0]["error"])

    async def test_cycles_rejected_before_worker_dispatch(self):
        adapter = ScriptedAdapter([task("A", deps=["B"]), task("B", deps=["A"])])
        state = await self.run_request(adapter)
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(len(adapter.calls), 1)
