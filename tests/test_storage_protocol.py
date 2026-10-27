import asyncio
import tempfile
import unittest
from pathlib import Path

from fagent.orchestrator import Orchestrator
from fagent.paths import canonical, changed_files, conflicting
from fagent.protocol import ProtocolError, checks, normalize_agent_response, request
from fagent.store import Store
from helpers import ScriptedAdapter


class StorageProtocolTests(unittest.TestCase):
    def test_exclusive_state_lock_and_atomic_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            with Store(path) as store:
                store.create({"text": "\u062f\u0631\u062e\u0648\u0627\u0633\u062a"})
                self.assertEqual(store.read()["text"], "\u062f\u0631\u062e\u0648\u0627\u0633\u062a")
                with self.assertRaises(ValueError):
                    with Store(path):
                        pass
                with self.assertRaises(ProtocolError):
                    store.create({})
            self.assertFalse(Path(str(path) + ".lock").exists())
            self.assertEqual(list(path.parent.glob(".run-*")), [])

    def test_request_validation_and_safe_default(self):
        with tempfile.TemporaryDirectory() as directory:
            value = {"project_root": directory, "text": "Implement this feature"}
            self.assertEqual(request(value)["mode"], "plan")
            for patch in ({"max_parallel": True}, {"max_parallel": 0}, {"max_attempts": 6},
                          {"text": ""}, {"mode": "auto"}):
                with self.subTest(patch=patch), self.assertRaises(ProtocolError):
                    request({**value, **patch})

    def test_real_scope_containment_aliases_and_reported_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for invalid in ("../escape", "/absolute", "C:/absolute", ".git/config", ".fagent/state", "src/*"):
                with self.subTest(path=invalid), self.assertRaises(ProtocolError):
                    canonical(root, invalid)
            self.assertTrue(conflicting([canonical(root, "src/UI/")],
                                        [canonical(root, "src/ui/button.tsx")]))
            changed_files(root, ["src/ui/"], ["src/ui/Button.tsx"])
            with self.assertRaises(ProtocolError):
                changed_files(root, ["src/ui/Button.tsx"], ["src/ui/Button.tsx/nested"])
            with self.assertRaises(ProtocolError):
                changed_files(root, ["src/ui/"], ["src/ui/"])

    def test_symlink_escape_is_rejected_when_platform_supports_links(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as other:
            try:
                (Path(root) / "escape").symlink_to(other, target_is_directory=True)
            except OSError:
                self.skipTest("Creating symlinks is unavailable in this Windows session")
            with self.assertRaises(ProtocolError):
                canonical(root, "escape/file.ts")

    def test_required_check_evidence_and_unavailable_coverage(self):
        value = [{"name": "typecheck", "required": True, "status": "NOT_RUN", "evidence": "Tool missing"}]
        self.assertFalse(checks(value))
        with self.assertRaises(ProtocolError):
            checks([{**value[0], "status": "N/A"}])
        with self.assertRaises(ProtocolError):
            checks([])

    def test_check_status_aliases_are_normalized(self):
        value = [{"name": "typecheck", "required": True, "status": "passed_with_open_decisions",
                  "evidence": "Verified by the task agent"}]
        self.assertFalse(checks(value))
        self.assertEqual(value[0]["status"], "INCONCLUSIVE")

    def test_nested_completed_response_is_flattened(self):
        value = normalize_agent_response({"status": "completed", "completed": {
            "summary": "Inspected", "evidence": [], "changed_files": []}})
        self.assertEqual(value["status"], "completed")
        self.assertEqual(value["summary"], "Inspected")
        self.assertNotIn("completed", value)


class ProjectLeaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_distinct_run_files_cannot_execute_one_project_concurrently(self):
        with tempfile.TemporaryDirectory() as directory:
            entered, release = asyncio.Event(), asyncio.Event()

            async def handler(packet):
                if packet["operation"] == "execute_task":
                    entered.set()
                    await release.wait()
            data = {"project_root": directory, "text": "Bounded work", "mode": "execute"}
            with Store(Path(directory) / "one.json") as first, Store(Path(directory) / "two.json") as second:
                active = asyncio.create_task(Orchestrator(ScriptedAdapter(handler=handler), first).start(data))
                await asyncio.wait_for(entered.wait(), 2)
                other = await Orchestrator(ScriptedAdapter(), second).start(data)
                self.assertEqual(other["status"], "blocked")
                self.assertIn("locked", other["error"])
                release.set()
                self.assertEqual((await active)["status"], "simulated")
