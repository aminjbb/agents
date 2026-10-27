"""Current attempts must not display errors that belong to archived failures."""
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.plans import prepare, reset_tasks
from fagent.store import Store
from helpers import ScriptedAdapter, task
from recovery_helpers import failure, repair


class AttemptErrorTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_retry_clears_recovery_error_and_archives_it(self):
        failing = True

        async def handler(packet):
            if failing and packet["operation"] == "execute_task":
                return failure()
            if failing and packet["operation"] == "review_task":
                response = repair()
                del response["rework"]["verification"]
                return response
            if not failing and packet["operation"] == "execute_task":
                self.assertNotIn("recovery_error", packet["context"]["task"])
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            adapter = ScriptedAdapter([task("A")], handler)
            runner = Orchestrator(adapter, store)
            state = await runner.start({"project_root": directory, "text": "Build", "mode": "execute"})
            self.assertEqual(state["status"], "blocked")
            old_error = state["plan"]["tasks"][0]["recovery_error"]
            failing = False
            state = await Orchestrator(adapter, store).resume(retry_tasks=["A"])
            current = state["plan"]["tasks"][0]
            self.assertEqual(state["status"], "simulated")
            self.assertNotIn("recovery_error", current)
            self.assertEqual(current["history"][0]["recovery_error"], old_error)
            self.assertEqual(current["blockers"][0]["error"], old_error)
            self.assertNotIn("recovery_error", store.read()["plan"]["tasks"][0])

    async def test_reset_archives_an_error_only_attempt_and_clears_consumers(self):
        with tempfile.TemporaryDirectory() as directory:
            plan, _ = prepare({"tasks": [task("A"), task("B", deps=["A"])]},
                              {"project_root": directory, "mode": "execute"})
            for current in plan["tasks"]:
                current.update(status="blocked", recovery_error="Old recovery error")
            reset_tasks({"plan": plan, "questions": []}, ["A"], fresh_attempt_window=True)
            for current in plan["tasks"]:
                self.assertNotIn("recovery_error", current)
                self.assertEqual(current["history"][0]["recovery_error"], "Old recovery error")

    async def test_starting_a_persisted_pending_attempt_also_clears_old_errors(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                self.assertNotIn("recovery_error", packet["context"]["task"])
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            runner = Orchestrator(ScriptedAdapter([task("A")], handler), store)
            state = await runner.start({"project_root": directory, "text": "Build", "mode": "plan"})
            state["plan"]["tasks"][0]["recovery_error"] = "Old persisted error"
            store.save(state)
            state = await runner.resume(authorize_execute=True)
            current = state["plan"]["tasks"][0]
            self.assertEqual(state["status"], "simulated")
            self.assertNotIn("recovery_error", current)
            self.assertEqual(current["history"][0]["recovery_error"], "Old persisted error")
