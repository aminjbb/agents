import asyncio
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.store import Store
from helpers import ScriptedAdapter, task
from recovery_helpers import failure, repair, verified


class RecoveryResumeTests(unittest.IsolatedAsyncioTestCase):
    async def test_explicit_parent_retry_includes_failed_repair_and_preserves_history(self):
        fixed, allow_repair = False, False

        async def handler(packet):
            nonlocal fixed
            operation, context = packet["operation"], packet["context"]
            if operation == "execute_task":
                current = context["task"]
                if current.get("recovery"):
                    if not allow_repair:
                        return failure()
                    fixed = True
                    return verified(status="completed", changed_files=[])
                if current["id"] == "A" and not fixed:
                    return failure()
            if operation == "review_task":
                return repair() if context.get("failure") else verified(status="approved")
        adapter = ScriptedAdapter([task("A"), task("OTHER")], handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(adapter, store).start(
                {"project_root": directory, "text": "Work", "mode": "execute", "max_attempts": 1})
            self.assertEqual(state["status"], "blocked")
            allow_repair = True
            state = await Orchestrator(adapter, store).resume(retry_tasks=["A"])
            self.assertEqual(state["status"], "simulated")
            self.assertEqual(len(state["plan"]["tasks"]), 3)
            self.assertEqual(state["plan"]["tasks"][0]["blockers"][0]["status"], "verified")
            self.assertEqual(state["plan"]["tasks"][1]["attempts"], 1)
            self.assertTrue(state["plan"]["tasks"][2]["history"])

    async def test_external_question_is_preserved_and_answer_resumes(self):
        async def handler(packet):
            operation, context = packet["operation"], packet["context"]
            if operation == "execute_task" and context["task"]["id"] == "A" and not packet["request"]["answers"]:
                return {"status": "blocked", "summary": "Need authorized test environment",
                        "blocker": {"category": "access", "code": "MISSING_TEST_ENV"}}
            if operation == "review_task" and context.get("failure"):
                return verified(status="blocked", questions=[{"id": "environment", "question": "Which test environment?"}])
        adapter = ScriptedAdapter([task("A"), task("B")], handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            runner = Orchestrator(adapter, store)
            state = await runner.start({"project_root": directory, "text": "Work", "mode": "execute"})
            self.assertEqual(state["status"], "needs_input")
            self.assertEqual(state["questions"][0]["id"], "A.environment")
            self.assertEqual(state["plan"]["tasks"][1]["status"], "done")
            state = await runner.resume(answers={"A.environment": "Local fixture"})
            self.assertEqual(state["status"], "simulated")

    async def test_cancelled_repair_is_persisted_and_resumed_explicitly(self):
        entered = asyncio.Event()
        allow_repair, fixed = False, False

        async def handler(packet):
            nonlocal fixed
            operation, context = packet["operation"], packet["context"]
            if operation == "execute_task":
                if context["task"].get("recovery"):
                    if not allow_repair:
                        entered.set()
                        await asyncio.Event().wait()
                    fixed = True
                    return verified(status="completed", changed_files=[])
                if not fixed:
                    return failure()
            if operation == "review_task":
                return repair() if context.get("failure") else verified(status="approved")
        adapter = ScriptedAdapter([task("A")], handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            runner = Orchestrator(adapter, store)
            future = asyncio.create_task(runner.start({"project_root": directory, "text": "Work", "mode": "execute"}))
            await asyncio.wait_for(entered.wait(), 2)
            future.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await future
            saved = store.read()
            self.assertEqual(saved["plan"]["tasks"][1]["block_reason"], "interrupted")
            self.assertEqual(saved["plan"]["tasks"][0]["block_reason"], "repair_failed")
            allow_repair = True
            state = await Orchestrator(adapter, store).resume(retry_tasks=["A"])
            self.assertEqual(state["status"], "simulated")

    async def test_repair_can_retry_with_concrete_strategy_inside_its_scope(self):
        fixed, tried = False, False

        async def handler(packet):
            nonlocal fixed, tried
            operation, context = packet["operation"], packet["context"]
            if operation == "execute_task":
                if context["task"].get("recovery"):
                    if not tried:
                        tried = True
                        return failure()
                    fixed = True
                    return verified(status="completed", changed_files=[])
                if not fixed:
                    return failure()
            if operation == "review_task":
                if context.get("failure"):
                    if context["task"].get("recovery"):
                        return verified(status="changes_required", retry_strategy="Normalize the boolean before serializing session.json")
                    return repair()
                return verified(status="approved")
        adapter = ScriptedAdapter([task("A")], handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(adapter, store).start({"project_root": directory, "text": "Work", "mode": "execute"})
            self.assertEqual(state["status"], "simulated")
            self.assertEqual(state["plan"]["tasks"][1]["attempts"], 2)
