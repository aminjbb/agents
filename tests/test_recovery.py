import json
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.store import Store
from helpers import ScriptedAdapter, task
from recovery_helpers import failure, repair, verified


class RecoveryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    async def run_case(self, handler, tasks=None, attempts=2, unlimited=False):
        adapter = ScriptedAdapter(tasks or [task("FORM", owner="@form-wizard")], handler)
        with Store(self.root / "run.json") as store:
            state = await Orchestrator(adapter, store, unlimited_attempts=unlimited).start(
                {"project_root": str(self.root), "text": "Build registration", "mode": "execute",
                 "max_attempts": attempts})
        return state, adapter

    async def test_real_fixture_repaired_then_original_and_consumer_resume(self):
        original = task("FORM", owner="@form-wizard")

        async def handler(packet):
            context, operation = packet["context"], packet["operation"]
            current = context.get("task", {})
            if operation == "execute_task":
                if current.get("recovery"):
                    (self.root / "session.json").write_text('{"authenticated":true}', encoding="utf-8")
                    return verified(status="completed", changed_files=["session.json"])
                if current["id"] == "FORM" and not (self.root / "session.json").exists():
                    return failure()
            if operation == "review_task" and context.get("failure"):
                return repair()
            if operation == "review_task" and context.get("recovery_verification"):
                self.assertEqual(packet["allowed_write_scope"], [])
                self.assertIs(json.loads((self.root / "session.json").read_text())["authenticated"], True)
                return verified(status="approved")
        state, adapter = await self.run_case(handler, [original, task("NEXT", deps=["FORM"])], attempts=1)
        self.assertEqual(state["status"], "simulated")
        main, consumer, fix = state["plan"]["tasks"]
        for key in ("owner", "objective", "acceptance_criteria", "write_scope"):
            self.assertEqual(main[key], original[key])
        self.assertEqual(main["attempts"], 2)
        self.assertEqual(main["blockers"][0]["status"], "verified")
        self.assertEqual(consumer["status"], fix["status"])
        executions = [p["context"]["task"]["id"] for p in adapter.calls if p["operation"] == "execute_task"]
        self.assertEqual(executions, ["FORM", "FORM-repair-1", "FORM", "NEXT"])
        resumed = next(p for p in adapter.calls if p["operation"] == "execute_task" and
                       p["context"]["task"]["id"] == "FORM" and p["context"]["task"]["attempts"] == 2)
        self.assertIn("FORM-repair-1", resumed["context"]["prerequisite_results"])

    async def test_same_failure_stops_even_with_legacy_unlimited_flag(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                if packet["context"]["task"].get("recovery"):
                    return verified(status="completed", changed_files=[])
                return failure()
            if packet["operation"] == "review_task":
                return repair() if packet["context"].get("failure") else verified(status="approved")
        state, _ = await self.run_case(handler, attempts=5, unlimited=True)
        main = state["plan"]["tasks"][0]
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(main["attempts"], 2)
        self.assertEqual(len(state["plan"]["tasks"]), 2)
        self.assertTrue(main["blockers"][-1]["repeated"])

    async def test_failed_repair_never_resumes_or_spawns_recursive_repairs(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                return failure()
            if packet["operation"] == "review_task":
                return repair()
        state, _ = await self.run_case(handler)
        main, fix = state["plan"]["tasks"]
        self.assertEqual(main["attempts"], 1)
        self.assertEqual(main["block_reason"], "repair_failed")
        self.assertEqual(fix["status"], "blocked")

    async def test_approval_without_original_verification_cannot_resume(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                return verified(status="completed", changed_files=[]) if packet["context"]["task"].get("recovery") else failure()
            if packet["operation"] == "review_task" and packet["context"].get("failure"):
                return repair()
            # Default fixture approval has a different check name.
        state, _ = await self.run_case(handler)
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["plan"]["tasks"][0]["attempts"], 1)

    async def test_inconclusive_repair_cannot_resume(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                result = failure()
                if packet["context"]["task"].get("recovery"):
                    result.update(status="completed", changed_files=[])
                    result["checks"][0]["status"] = "INCONCLUSIVE"
                return result
            if packet["operation"] == "review_task":
                return repair()
        state, _ = await self.run_case(handler)
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["plan"]["tasks"][0]["attempts"], 1)
