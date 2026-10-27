import asyncio
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.store import Store
from helpers import ScriptedAdapter, task
from recovery_helpers import failure, repair, verified


class RecoverySchedulingTests(unittest.IsolatedAsyncioTestCase):
    async def run_case(self, tasks, handler, attempts=2):
        adapter = ScriptedAdapter(tasks, handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(adapter, store).start(
                {"project_root": directory, "text": "Build feature", "mode": "execute",
                 "max_attempts": attempts, "max_parallel": 3})
        return state, adapter

    async def test_diagnosis_does_not_prematurely_block_consumers(self):
        diagnosed = asyncio.Event()

        async def handler(packet):
            operation, context = packet["operation"], packet["context"]
            current = context.get("task", {})
            if operation == "execute_task":
                if current["id"] == "A" and current["attempts"] == 1:
                    return failure()
                if current["id"] == "INDEPENDENT":
                    await asyncio.wait_for(diagnosed.wait(), 2)
                if current.get("recovery"):
                    return verified(status="completed", changed_files=[])
            if operation == "review_task":
                if context.get("failure"):
                    diagnosed.set()
                    await asyncio.sleep(0.02)
                    return repair()
                return verified(status="approved")
        state, _ = await self.run_case([task("A"), task("B", deps=["A"]), task("INDEPENDENT")], handler)
        self.assertEqual(state["status"], "simulated")
        self.assertTrue(all(item["status"] == "done" for item in state["plan"]["tasks"]))

    async def test_new_scope_locks_and_invalidates_completed_writers(self):
        other_active, peak, active, repaired = False, 0, 0, False
        other_started = asyncio.Event()

        async def handler(packet):
            nonlocal other_active, peak, active, repaired
            operation, context = packet["operation"], packet["context"]
            current = context.get("task", {})
            if operation == "execute_task":
                if current["id"] == "A" and not repaired:
                    await asyncio.wait_for(other_started.wait(), 2)
                    return failure()
                if current["id"] == "B" or current.get("recovery"):
                    active += 1
                    peak = max(peak, active)
                    if current["id"] == "B":
                        other_active = True
                        other_started.set()
                        await asyncio.sleep(0.02)
                        other_active = False
                    else:
                        self.assertFalse(other_active)
                        repaired = True
                    active -= 1
                    return verified(status="completed", changed_files=[])
            if operation == "review_task":
                return repair(write_scope=["src/shared/"]) if context.get("failure") else verified(status="approved")
        tasks = [task("A", scopes=["src/features/form/"]), task("B", scopes=["src/shared/session.ts"]),
                 task("UNCHANGED", scopes=["src/other/"])]
        state, _ = await self.run_case(tasks, handler, attempts=1)
        self.assertEqual(state["status"], "simulated")
        self.assertEqual(peak, 1)
        counts = {item["id"]: item["attempts"] for item in state["plan"]["tasks"]}
        self.assertEqual(counts["B"], 2)
        self.assertEqual(counts["UNCHANGED"], 1)

    async def test_cycles_and_invalid_repair_scope_are_rejected_atomically(self):
        for change in ({"depends_on": ["B"]}, {"write_scope": ["../escape/"]},
                       {"verification": {"reproduce": "Check it", "checks": ["unrelated check"]}}):
            with self.subTest(change=change):
                async def handler(packet):
                    if packet["operation"] == "execute_task" and packet["context"]["task"]["id"] == "A":
                        return failure()
                    if packet["operation"] == "review_task" and packet["context"].get("failure"):
                        return repair(**change)
                state, _ = await self.run_case([task("A"), task("B", deps=["A"])], handler)
                self.assertEqual(state["status"], "blocked")
                self.assertEqual(len(state["plan"]["tasks"]), 2)
                self.assertEqual(state["plan"]["tasks"][0]["depends_on"], [])
                self.assertIn("recovery_error", state["plan"]["tasks"][0])

    async def test_unavailable_tool_does_not_trigger_keyword_reassignment(self):
        async def handler(packet):
            if packet["operation"] == "execute_task" and packet["context"]["task"]["id"] == "A":
                return {"status": "blocked", "summary": "Browser/viewport unavailable; missing tool"}
        state, adapter = await self.run_case([task("A"), task("B")], handler)
        self.assertEqual(len(state["plan"]["tasks"]), 2)
        self.assertEqual(state["plan"]["tasks"][1]["status"], "done")
        self.assertFalse(any(p["agent"] == "@auditor" for p in adapter.calls))

    async def test_worker_exception_is_sent_to_lead_and_repaired(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                current = packet["context"]["task"]
                if current["id"] == "A" and current["attempts"] == 1:
                    raise RuntimeError("Contract parser crashed")
                if current.get("recovery"):
                    return verified(status="completed", changed_files=[])
            if packet["operation"] == "review_task":
                return repair() if packet["context"].get("failure") else verified(status="approved")
        state, _ = await self.run_case([task("A")], handler)
        self.assertEqual(state["status"], "simulated")
        self.assertEqual(state["plan"]["tasks"][0]["history"][0]["error"], "Contract parser crashed")
