"""Protocol tests use a fake local child, never model inference or real auth."""
import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from fagent.codex_adapter import CodexAdapter
from fagent.protocol import ProtocolError


SERVER = r'''
import json, os, sys, time
mode, recording = sys.argv[1:]
def emit(value):
    print(json.dumps(value), flush=True)
for line in sys.stdin:
    message = json.loads(line)
    with open(recording, "a", encoding="utf8") as log:
        log.write(json.dumps({"message": message, "home": os.getenv("CODEX_HOME"), "pid": os.getpid()})+"\n")
    method = message.get("method")
    if method == "initialize":
        emit({"id": message["id"], "result": {}})
    elif method == "account/login/start":
        if mode == "autherror":
            emit({"id": message["id"], "error": {"message": message["params"]["apiKey"]}})
        else:
            emit({"id": message["id"], "result": {"type": "apiKey"}})
    elif method == "account/read":
        emit({"id": message["id"], "result": {"account": {"type": "apiKey"}, "requiresOpenaiAuth": True}})
    elif method == "thread/start":
        emit({"id": message["id"], "result": {"thread": {"id": "thread1"}}})
    elif method == "turn/start":
        if mode == "hang":
            time.sleep(60)
        if mode == "malformed":
            print("not json", flush=True)
            continue
        # A notification can arrive before the turn/start response.
        emit({"id": 900, "method": "item/commandExecution/requestApproval", "params": {}})
        emit({"method": "item/completed", "params": {"threadId": "thread1", "turnId": "turn1",
              "item": {"type": "agentMessage", "text": '{"status":"planned","plan":{"tasks":[]}}'}}})
        emit({"id": message["id"], "result": {"turn": {"id": "turn1"}}})
        emit({"method": "turn/completed", "params": {"threadId": "thread1", "turn": {
              "id": "turn1", "status": "failed" if mode == "failed" else "completed"}}})
'''


class CodexAdapterTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.recording = self.root / "record.jsonl"
        environment = patch.dict(os.environ, {"CODEX_HOME": str(self.root)})
        environment.start()
        self.addCleanup(environment.stop)
        self.addCleanup(self.temporary.cleanup)

    def adapter(self, mode="ok", key="test-secret-key"):
        return CodexAdapter(api_key=key, command=[sys.executable, "-u", "-c", SERVER,
                                                mode, str(self.recording)])

    def packet(self, writable=False):
        return {"request": {"project_root": str(self.root), "mode": "execute" if writable else "plan"},
                "agent": "@architect", "operation": "execute_task" if writable else "plan",
                "allowed_write_scope": ["src/"] if writable else [], "response_contract": {}}

    def records(self):
        return [json.loads(line) for line in self.recording.read_text().splitlines()]

    async def test_handshake_queue_approval_and_disposable_auth(self):
        result = await self.adapter().invoke(self.packet())
        self.assertEqual(result["status"], "planned")
        records = self.records()
        methods = [item["message"].get("method") for item in records]
        self.assertEqual(methods[:3], ["initialize", "initialized", "account/login/start"])
        self.assertTrue(any(item["message"].get("result") == {"decision": "decline"} for item in records))
        self.assertFalse(Path(records[0]["home"]).exists())
        thread = next(item["message"]["params"] for item in records
                      if item["message"].get("method") == "thread/start")
        self.assertTrue(thread["ephemeral"])
        self.assertEqual(thread["sandbox"], "read-only")
        turn = next(item["message"]["params"] for item in records
                    if item["message"].get("method") == "turn/start")
        self.assertEqual(turn["sandboxPolicy"], {"type": "readOnly"})
        self.assertNotIn("test-secret-key", turn["input"][0]["text"])

    async def test_workspace_sandbox_no_network(self):
        await self.adapter().invoke(self.packet(True))
        turn = next(item["message"]["params"] for item in self.records()
                    if item["message"].get("method") == "turn/start")
        self.assertEqual(turn["sandboxPolicy"]["writableRoots"], [str(self.root.resolve())])
        self.assertFalse(turn["sandboxPolicy"]["networkAccess"])
        self.assertEqual(turn["approvalPolicy"], "never")

    async def test_probe_no_inference(self):
        result = await self.adapter().probe()
        self.assertTrue(result["authenticated"])
        self.assertFalse(any(item["message"].get("method") == "turn/start" for item in self.records()))

    async def test_existing_cli_auth_does_not_log_in(self):
        await self.adapter(key=None).probe()
        self.assertFalse(any(item["message"].get("method") == "account/login/start"
                             for item in self.records()))

    async def test_errors_do_not_disclose_key(self):
        for mode in ("autherror", "malformed", "failed"):
            with self.subTest(mode=mode), self.assertRaises(ProtocolError) as caught:
                await self.adapter(mode).invoke(self.packet())
            self.assertNotIn("test-secret-key", str(caught.exception))

    async def test_timeout_cleans_process_and_auth(self):
        adapter = self.adapter("hang")
        adapter.timeout = .5
        with self.assertRaisesRegex(ProtocolError, "timed out"):
            await adapter.invoke(self.packet())
        records = self.records()
        self.assertFalse(Path(records[0]["home"]).exists())
        if sys.platform != "win32":
            with self.assertRaises(ProcessLookupError):
                os.kill(records[0]["pid"], 0)

    async def test_cancel_cleans_auth(self):
        task = asyncio.create_task(self.adapter("hang").invoke(self.packet()))
        for _ in range(100):
            if self.recording.exists() and 'turn/start' in self.recording.read_text():
                break
            await asyncio.sleep(.02)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertFalse(Path(self.records()[0]["home"]).exists())

    async def test_review_rejects_write_scope(self):
        packet = self.packet(True)
        packet["operation"] = "review_task"
        with self.assertRaises(ProtocolError):
            await self.adapter().invoke(packet)
