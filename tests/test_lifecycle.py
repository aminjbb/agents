import asyncio
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.store import Store
from helpers import ScriptedAdapter, evidence, task


class LifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_capacity_one_and_read_only_review_scope(self):
        active, peak = 0, 0

        async def handler(packet):
            nonlocal active, peak
            if packet["operation"] == "execute_task":
                active += 1
                peak = max(active, peak)
                await asyncio.sleep(0.01)
                active -= 1
            else:
                self.assertEqual(packet["allowed_write_scope"], [])
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(ScriptedAdapter([task("A"), task("B")], handler), store).start(
                {"project_root": directory, "text": "Work", "mode": "execute", "max_parallel": 1})
            self.assertEqual(peak, 1)
            self.assertEqual(state["status"], "simulated")

    async def test_cancellation_preserves_interrupted_tasks_and_releases_project_lease(self):
        entered = asyncio.Event()

        async def handler(packet):
            if packet["operation"] == "execute_task":
                entered.set()
                await asyncio.Event().wait()
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            runner = Orchestrator(ScriptedAdapter(handler=handler), store)
            future = asyncio.create_task(runner.start(
                {"project_root": directory, "text": "Work", "mode": "execute"}))
            await asyncio.wait_for(entered.wait(), 2)
            future.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await future
            saved = store.read()
            self.assertEqual(saved["status"], "blocked")
            self.assertEqual(saved["plan"]["tasks"][0]["block_reason"], "interrupted")
            self.assertFalse((Path(directory) / ".fagent/workspace.lock").exists())

    async def test_read_only_review_cannot_report_source_changes(self):
        async def handler(packet):
            if packet["operation"] == "review_task":
                return evidence(status="approved", changed_files=["src/file.ts"])
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(ScriptedAdapter(handler=handler), store).start(
                {"project_root": directory, "text": "Work", "mode": "execute"})
            self.assertEqual(state["status"], "blocked")

    async def test_planner_cannot_forge_completed_prerequisites(self):
        forged = task()
        forged["status"] = "done"
        adapter = ScriptedAdapter([forged])
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(adapter, store).start(
                {"project_root": directory, "text": "Work", "mode": "execute"})
            self.assertEqual(state["status"], "blocked")
            self.assertEqual(len(adapter.calls), 1)

    async def test_shared_architecture_context_reaches_the_specialist(self):
        async def handler(packet):
            if packet["operation"] == "plan":
                return {"status": "planned", "brief": "Accepted product behavior",
                        "plan": {"contracts": {"save": "approved mutation"}, "tasks": [task()]}}
            if packet["operation"] == "execute_task":
                self.assertEqual(packet["context"]["architecture_context"]["brief"], "Accepted product behavior")
                self.assertEqual(packet["context"]["plan_contracts"]["contracts"]["save"], "approved mutation")
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(ScriptedAdapter(handler=handler), store).start(
                {"project_root": directory, "text": "Work", "mode": "execute"})
            self.assertEqual(state["planning"]["brief"], "Accepted product behavior")
            self.assertEqual(state["status"], "simulated")

    async def test_response_simulation_flag_prevents_real_delivery_label(self):
        async def handler(packet):
            if packet["operation"] == "execute_task":
                return evidence(status="completed", changed_files=[], simulation=True)
        adapter = ScriptedAdapter(handler=handler)
        adapter.simulation = False
        with tempfile.TemporaryDirectory() as directory, Store(Path(directory) / "run.json") as store:
            state = await Orchestrator(adapter, store).start(
                {"project_root": directory, "text": "Work", "mode": "execute"})
            self.assertEqual(state["status"], "simulated")
