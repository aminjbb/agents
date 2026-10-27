"""Exercise verdict-only audit responses through an actual local RPC child process."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fagent.codex_adapter import CodexAdapter
from fagent.outcomes import audit
from helpers import evidence
from test_codex_adapter import SERVER


class CodexAuditTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_rpc_transport_preserves_verdict_and_named_checks(self):
        expected = evidence(verdict="PASS")
        server = SERVER.replace('{"status":"planned","plan":{"tasks":[]}}', json.dumps(expected))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.dict(os.environ, {"CODEX_HOME": directory}):
                adapter = CodexAdapter(command=[sys.executable, "-u", "-c", server,
                                                "ok", str(root / "record.jsonl")])
                result = await adapter.invoke({
                    "request": {"project_root": directory, "mode": "execute"},
                    "agent": "@auditor", "operation": "review_delivery",
                    "allowed_write_scope": [], "response_contract": {"verdict": "PASS | FAIL | INCOMPLETE"}})
        self.assertEqual(result, expected)
        self.assertEqual(audit(result), "PASS")
