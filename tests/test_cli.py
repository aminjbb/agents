import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRIDGE = Path(__file__).parent / "fixtures/stdio_bridge.py"


class CliTests(unittest.TestCase):
    def invoke(self, *args):
        result = subprocess.run([sys.executable, "-m", "fagent", *map(str, args)], cwd=ROOT,
                                text=True, encoding="utf-8", capture_output=True, timeout=15)
        return result.returncode, json.loads(result.stdout)

    def config(self, directory):
        path = Path(directory) / "adapter.json"
        path.write_text(json.dumps({"command": [sys.executable, str(BRIDGE.resolve())],
                                    "simulation": True}), encoding="utf-8")
        return path

    def test_real_cli_plan_then_explicit_execute_and_status(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self.config(directory)
            state = Path(directory) / "state.json"
            code, result = self.invoke("start", "--project-root", directory, "--text", "fixture",
                                       "--state", state, "--adapter-config", config)
            self.assertEqual((code, result["status"]), (0, "planned"))
            self.assertFalse((Path(directory) / "src/result.txt").exists())
            code, result = self.invoke("resume", "--state", state, "--adapter-config", config, "--execute")
            self.assertEqual((code, result["status"]), (0, "simulated"))
            self.assertTrue(result["simulation"])
            self.assertEqual((Path(directory) / "src/result.txt").read_text(), "fixture output")
            code, saved = self.invoke("status", "--state", state, "--full")
            self.assertEqual(code, 0)
            starts = [event for event in saved["events"] if event["event"] == "agent_started"]
            self.assertEqual(starts[0]["agent"], "@architect")
            self.assertEqual([e["operation"] for e in starts],
                             ["plan", "execute_task", "review_task", "review_delivery", "accept_delivery"])

    def test_cli_question_exit_and_resume_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self.config(directory)
            state = Path(directory) / "state.json"
            code, result = self.invoke("start", "--project-root", directory, "--text", "ask",
                                       "--state", state, "--adapter-config", config)
            self.assertEqual((code, result["status"]), (2, "needs_input"))
            answers = Path(directory) / "answers.json"
            answers.write_text(json.dumps({"goal": "Create the fixture"}), encoding="utf-8")
            code, result = self.invoke("resume", "--state", state, "--adapter-config", config,
                                       "--answers", answers)
            self.assertEqual((code, result["status"]), (0, "planned"))

    def test_missing_adapter_does_not_silently_use_a_mock(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            code, result = self.invoke("start", "--project-root", directory, "--text", "work",
                                       "--state", state, "--adapter-config", Path(directory) / "missing.json")
            self.assertEqual((code, result["status"]), (1, "error"))
            self.assertFalse(state.exists())
