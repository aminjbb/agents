import asyncio
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.store import Store
from helpers import ScriptedAdapter, task
from recovery_helpers import failure, repair, verified


class RecoveryConflictTests(unittest.IsolatedAsyncioTestCase):
    async def test_two_repairs_of_same_file_do_not_reapply_each_others_fixes(self):
        fixed = set()

        async def handler(packet):
            operation, context = packet["operation"], packet["context"]
            if operation == "execute_task":
                current = context["task"]
                if current.get("recovery"):
                    fixed.add(current["recovery"]["parent_id"])
                    return verified(status="completed", changed_files=[])
                if current["id"] not in fixed:
                    return failure()
            if operation == "review_task":
                return repair() if context.get("failure") else verified(status="approved")
        adapter = ScriptedAdapter([task("A"), task("B")], handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await asyncio.wait_for(Orchestrator(adapter, store).start(
                {"project_root": directory, "text": "Build", "mode": "execute", "max_attempts": 1}), 3)
            self.assertEqual(state["status"], "simulated")
            repairs = [item for item in state["plan"]["tasks"] if item.get("recovery")]
            self.assertEqual(len(repairs), 2)
            self.assertTrue(all(item["attempts"] == 1 for item in repairs))
            # A's acceptance was rerun after B's overlapping repair.
            self.assertEqual(state["plan"]["tasks"][0]["attempts"], 3)

    async def test_affected_running_consumer_is_drained_before_invalidation(self):
        consuming, fixed = False, False
        entered = asyncio.Event()

        async def handler(packet):
            nonlocal consuming, fixed
            operation, context = packet["operation"], packet["context"]
            if operation == "execute_task":
                current = context["task"]
                if current["id"] == "CONSUMER":
                    self.assertFalse(consuming)
                    consuming = True
                    entered.set()
                    await asyncio.sleep(0.02)
                    consuming = False
                if current["id"] == "FORM" and not fixed:
                    await asyncio.wait_for(entered.wait(), 2)
                    return failure()
                if current.get("recovery"):
                    self.assertFalse(consuming)
                    fixed = True
                    return verified(status="completed", changed_files=[])
            if operation == "review_task":
                return repair(write_scope=["src/provider/"]) if context.get("failure") else verified(status="approved")
        tasks = [task("PROVIDER", scopes=["src/provider/"]),
                 task("CONSUMER", deps=["PROVIDER"]), task("FORM")]
        adapter = ScriptedAdapter(tasks, handler)
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await asyncio.wait_for(Orchestrator(adapter, store).start(
                {"project_root": directory, "text": "Build", "mode": "execute", "max_attempts": 1}), 3)
            self.assertEqual(state["status"], "simulated")
            self.assertEqual(state["plan"]["tasks"][1]["attempts"], 2)
