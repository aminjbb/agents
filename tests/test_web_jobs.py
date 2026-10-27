import asyncio
import tempfile
import threading
import time
import unittest
from pathlib import Path

from fagent.web_jobs import Jobs
from fagent.codex_setup import CodexSetupError
from helpers import ScriptedAdapter


class ConnectedAdapter(ScriptedAdapter):
    async def probe(self):
        return {"authenticated": True}


class WebJobsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.adapters = []

        def factory(**kwargs):
            adapter = ConnectedAdapter()
            self.adapters.append(adapter)
            return adapter
        self.jobs = Jobs(self.root / "runs", factory)
        self.addCleanup(self.jobs.close)

    def wait(self, run_id):
        until = time.monotonic() + 5
        while self.jobs.read(run_id)["busy"] and time.monotonic() < until:
            time.sleep(0.01)
        self.assertFalse(self.jobs.read(run_id)["busy"])
        return self.jobs.read(run_id)

    def test_plan_then_explicit_execution_and_no_secret_in_state(self):
        key = "sk-local-unit-test-secret"
        self.jobs.connect({"api_key": key})
        run_id = self.jobs.start({"text": "Create form", "project_root": str(self.root)})["id"]
        result = self.wait(run_id)
        self.assertEqual(result["state"]["status"], "planned")
        self.assertTrue(all(p["operation"] == "plan" for p in self.adapters[-1].calls))
        self.assertNotIn(key, self.jobs.path(run_id).read_text(encoding="utf-8"))
        self.jobs.resume(run_id, {"execute": True})
        result = self.wait(run_id)
        self.assertEqual(result["state"]["status"], "simulated", result)
        self.assertEqual(self.jobs.summaries()[0]["id"], run_id)
        self.assertEqual(self.jobs.disconnect(), {"configured": False, "model": None})

    def test_reject_missing_connection_and_traversal(self):
        with self.assertRaisesRegex(ValueError, "Connect"):
            self.jobs.start({"text": "Create form", "project_root": str(self.root)})
        with self.assertRaisesRegex(ValueError, "Invalid run ID"):
            self.jobs.read("../private")

    def test_restart_keeps_history_but_forgets_credentials(self):
        self.jobs.connect({"api_key": "secret"})
        run_id = self.jobs.start({"text": "Create form", "project_root": str(self.root)})["id"]
        self.wait(run_id)
        other = Jobs(self.root / "runs", lambda **_: ConnectedAdapter())
        try:
            self.assertFalse(other.connection()["configured"])
            self.assertEqual(other.read(run_id)["state"]["status"], "planned")
        finally:
            other.close()

    def test_unauthenticated_probe_does_not_mark_connected(self):
        class NoAuth(ConnectedAdapter):
            async def probe(self):
                return {"authenticated": False}
        self.jobs.adapter_factory = lambda **_: NoAuth()
        with self.assertRaisesRegex(ValueError, "not signed in"):
            self.jobs.connect({"api_key": "invalid"})
        self.assertFalse(self.jobs.connection()["configured"])

    def test_safe_installation_guidance_is_not_replaced_with_generic_error(self):
        def missing(**_):
            raise CodexSetupError("Codex CLI was not found. Install it and restart the server.")
        self.jobs.adapter_factory = missing
        with self.assertRaisesRegex(CodexSetupError, "CLI was not found"):
            self.jobs.connect({})
        self.assertFalse(self.jobs.connection()["configured"])

    def test_busy_run_rejects_duplicate_and_shutdown_persists_interruption(self):
        started = threading.Event()

        class Waiting(ConnectedAdapter):
            async def invoke(self, packet):
                started.set()
                await asyncio.Event().wait()
        self.jobs.adapter_factory = lambda **_: Waiting()
        self.jobs.connect({})
        run_id = self.jobs.start({"text": "Create form", "project_root": str(self.root)})["id"]
        self.assertTrue(started.wait(timeout=5))
        with self.assertRaisesRegex(ValueError, "existing plan"):
            self.jobs.resume(run_id, {"execute": True})
        with self.assertRaisesRegex(ValueError, "already active"):
            self.jobs.resume(run_id, {})
        with self.assertRaisesRegex(ValueError, "active work"):
            self.jobs.disconnect()
        self.jobs.close()
        result = self.jobs.read(run_id)
        self.assertFalse(result["busy"])
        self.assertEqual(result["state"]["status"], "blocked")
        names = [event["event"] for event in result["state"]["events"]]
        self.assertEqual(names.count("agent_started"), names.count("agent_finished"))
        self.assertFalse(self.jobs.path(run_id).with_suffix(".json.lock").exists())
