import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.protocol import ProtocolError
from fagent.store import Store
from helpers import ScriptedAdapter, evidence, task


class ResumeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def data(self, **options):
        return {"project_root": str(self.root), "text": "Build the requested feature", **options}

    async def test_architect_questions_resume_with_history_and_no_premature_workers(self):
        count = 0

        async def handler(packet):
            nonlocal count
            if packet["operation"] == "plan":
                count += 1
                if count == 1:
                    return {"status": "needs_input", "questions": [{"id": "destination", "question": "Where next?"}]}
                self.assertEqual(packet["request"]["answers"], {"destination": "Stay here"})
                self.assertEqual(packet["request"]["clarifications"][0]["questions"][0]["question"], "Where next?")
        adapter = ScriptedAdapter(handler=handler)
        with Store(self.root / "run.json") as store:
            runner = Orchestrator(adapter, store)
            state = await runner.start(self.data())
            self.assertEqual(state["status"], "needs_input")
            with self.assertRaises(ProtocolError):
                await runner.resume({"wrong": "value"})
            state = await runner.resume({"destination": "Stay here"})
            self.assertEqual(state["status"], "planned")
            self.assertNotIn("execute_task", [p["operation"] for p in adapter.calls])

    async def test_planned_execution_requires_explicit_authorization(self):
        adapter = ScriptedAdapter()
        with Store(self.root / "run.json") as store:
            runner = Orchestrator(adapter, store)
            state = await runner.start(self.data())
            self.assertEqual(state["status"], "planned")
            state = await runner.resume(authorize_execute=True)
            self.assertEqual(state["status"], "simulated")
            with self.assertRaises(ProtocolError):
                await runner.resume()

    async def test_task_clarifications_preserve_independent_progress_and_retry_budget(self):
        asked = False

        async def handler(packet):
            nonlocal asked
            if packet["operation"] == "execute_task" and packet["context"]["task"]["id"] == "A" and not asked:
                asked = True
                return {"status": "needs_input", "summary": "Need a destination",
                        "questions": [{"id": "next", "question": "Stay or navigate?"}]}
        adapter = ScriptedAdapter([task("A"), task("B")], handler)
        with Store(self.root / "run.json") as store:
            runner = Orchestrator(adapter, store)
            state = await runner.start(self.data(mode="execute", max_attempts=1))
            self.assertEqual(state["status"], "needs_input")
            self.assertEqual(state["questions"][0]["id"], "A.next")
            state = await runner.resume({"A.next": "Stay"})
            self.assertEqual(state["status"], "simulated")
            executions = [p["context"]["task"]["id"] for p in adapter.calls if p["operation"] == "execute_task"]
            self.assertEqual(executions.count("B"), 1)

    async def test_task_review_rework_is_bounded(self):
        async def handler(packet):
            if packet["operation"] == "review_task":
                return evidence(status="changes_required")
        adapter = ScriptedAdapter(handler=handler)
        with Store(self.root / "run.json") as store:
            state = await Orchestrator(adapter, store).start(self.data(mode="execute", max_attempts=2))
            self.assertEqual(state["status"], "blocked")
            self.assertEqual(state["plan"]["tasks"][0]["attempts"], 2)
            self.assertEqual(len(state["plan"]["tasks"][0]["history"]), 1)

    async def test_final_rework_invalidates_consumers_but_keeps_unrelated_results(self):
        rounds = 0

        async def handler(packet):
            nonlocal rounds
            if packet["operation"] == "review_delivery":
                rounds += 1
                return evidence(verdict="FAIL" if rounds == 1 else "PASS")
            if packet["operation"] == "accept_delivery" and rounds == 1:
                return evidence(status="changes_required", retry_tasks=["A"])
        adapter = ScriptedAdapter([task("A"), task("B", deps=["A"]), task("C")], handler)
        with Store(self.root / "run.json") as store:
            state = await Orchestrator(adapter, store).start(self.data(mode="execute"))
            self.assertEqual(state["status"], "simulated")
            attempts = {t["id"]: t["attempts"] for t in state["plan"]["tasks"]}
            self.assertEqual(attempts, {"A": 2, "B": 2, "C": 1})
            self.assertEqual(state["delivery_history"][0]["audit"]["verdict"], "FAIL")
            self.assertEqual(len(state["plan"]["tasks"][0]["history"]), 1)

    async def test_required_incomplete_audit_stays_blocked(self):
        async def handler(packet):
            if packet["operation"] == "review_delivery":
                return evidence(verdict="INCOMPLETE")
        with Store(self.root / "run.json") as store:
            state = await Orchestrator(ScriptedAdapter(handler=handler), store).start(self.data(mode="execute"))
            self.assertEqual(state["status"], "blocked")
