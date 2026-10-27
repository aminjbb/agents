import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.store import Store
from helpers import ScriptedAdapter, evidence, task


class DeliveryReworkTests(unittest.IsolatedAsyncioTestCase):
    async def run_case(self, handler):
        adapter = ScriptedAdapter([task("A"), task("CONSUMER", deps=["A"]), task("OTHER")], handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(adapter, store).start(
                {"project_root": directory, "text": "Build", "mode": "execute", "max_attempts": 2})
        return state, adapter

    async def test_incomplete_audit_can_schedule_evidence_work_then_require_fresh_pass(self):
        rounds = 0

        async def handler(packet):
            nonlocal rounds
            if packet["operation"] == "review_delivery":
                rounds += 1
                return evidence(verdict="INCOMPLETE" if rounds == 1 else "PASS")
            if packet["operation"] == "accept_delivery" and rounds == 1:
                result = evidence(status="changes_required", retry_tasks=["A"])
                result["checks"][0]["status"] = "NOT_RUN"
                return result
        state, _ = await self.run_case(handler)
        self.assertEqual(state["status"], "simulated")
        self.assertEqual(rounds, 2)
        self.assertEqual({item["id"]: item["attempts"] for item in state["plan"]["tasks"]},
                         {"A": 2, "CONSUMER": 2, "OTHER": 1})
        self.assertEqual(state["delivery_history"][0]["audit"]["verdict"], "INCOMPLETE")
        self.assertEqual(state["audit"]["verdict"], "PASS")

    async def test_repeated_incomplete_audit_never_delivers_or_resets_attempt_budget(self):
        async def handler(packet):
            if packet["operation"] == "review_delivery":
                return evidence(verdict="INCOMPLETE")
            if packet["operation"] == "accept_delivery":
                return evidence(status="changes_required", retry_tasks=["A"])
        state, adapter = await self.run_case(handler)
        self.assertEqual(state["status"], "blocked")
        executions = [p for p in adapter.calls if p["operation"] == "execute_task" and
                      p["context"]["task"]["id"] == "A"]
        self.assertEqual(len(executions), 2)
        self.assertFalse(any(event["event"] == "delivery_finished" for event in state["events"]))

    async def test_explicit_architect_block_does_not_schedule_retry(self):
        async def handler(packet):
            if packet["operation"] == "review_delivery":
                return evidence(verdict="INCOMPLETE")
            if packet["operation"] == "accept_delivery":
                return evidence(status="blocked", retry_tasks=["A"])
        state, _ = await self.run_case(handler)
        self.assertEqual(state["status"], "blocked")
        self.assertTrue(all(item["attempts"] == 1 for item in state["plan"]["tasks"]))

    async def test_unknown_retry_ids_do_not_mutate_the_graph(self):
        async def handler(packet):
            if packet["operation"] == "review_delivery":
                return evidence(verdict="INCOMPLETE")
            if packet["operation"] == "accept_delivery":
                return evidence(status="changes_required", retry_tasks=["UNKNOWN"])
        state, _ = await self.run_case(handler)
        self.assertEqual(state["status"], "blocked")
        self.assertIn("Unknown/empty retry tasks", state["error"])
        self.assertTrue(all(item["status"] == "done" for item in state["plan"]["tasks"]))
