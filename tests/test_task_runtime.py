"""Planner output supplies contracts, never scheduler-owned execution state."""
from copy import deepcopy
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.plans import prepare
from helpers import ScriptedAdapter, evidence, task
from fagent.store import Store


class TaskRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_planner_cannot_increase_attempt_budget(self):
        async def handler(packet):
            if packet["operation"] == "review_task":
                return evidence(status="changes_required")
        planned = {**task("A"), "resume_allowance": 2, "revalidation_allowance": 50}
        adapter = ScriptedAdapter([planned], handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(adapter, store).start(
                {"project_root": directory, "text": "Build", "mode": "execute", "max_attempts": 1})
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["plan"]["tasks"][0]["attempts"], 1)
        executions = [p for p in adapter.calls if p["operation"] == "execute_task"]
        self.assertEqual(len(executions), 1)

    async def test_copied_recovery_bookkeeping_does_not_turn_a_task_into_a_repair(self):
        planned = {**task("A"), "recovery": {"parent_id": "NONEXISTENT"},
                   "active_repair": "UNKNOWN", "blockers": [{"fingerprint": "stale"}],
                   "diagnosis_in_progress": True, "invalidation_applied": True}
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(ScriptedAdapter([planned]), store).start(
                {"project_root": directory, "text": "Build", "mode": "execute"})
        self.assertEqual(state["status"], "simulated")
        current = state["plan"]["tasks"][0]
        for key in ("recovery", "active_repair", "blockers", "diagnosis_in_progress", "invalidation_applied"):
            self.assertNotIn(key, current)

    async def test_prepare_keeps_declarative_context_without_accepting_runtime_extensions(self):
        planned = {**task("A"), "contracts": {"save": "accepted payload"},
                   "checks": ["Check the accepted interaction"], "metadata": {"brief": "Accepted"},
                   "resume_allowance": "invalid", "revalidation_allowance": -5,
                   "recovery_epoch": 100, "recovery_error": "stale", "error": "stale",
                   "future_execution_override": True, "attempts": 99, "history": [{"forged": True}]}
        original = deepcopy(planned)
        with tempfile.TemporaryDirectory() as directory:
            result, _ = prepare({"tasks": [planned], "contracts": {"session": "accepted"}},
                                {"project_root": directory, "mode": "execute"})
        current = result["tasks"][0]
        self.assertEqual(planned, original)
        for key in ("contracts", "checks", "metadata"):
            self.assertEqual(current[key], planned[key])
        self.assertEqual(result["contracts"], {"session": "accepted"})
        for key in ("resume_allowance", "revalidation_allowance", "recovery_epoch", "recovery_error",
                    "error", "future_execution_override"):
            self.assertNotIn(key, current)
        self.assertEqual(current["attempts"], 0)
        self.assertEqual(current["history"], [])
