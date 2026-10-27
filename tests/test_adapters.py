import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path

from fagent.adapters import CommandAdapter
from fagent.protocol import ProtocolError


class CommandAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, source, timeout=3):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bridge.py"
            path.write_text(source, encoding="utf-8")
            adapter = CommandAdapter({"command": [sys.executable, str(path)], "timeout_seconds": timeout})
            return await adapter.invoke({"request": {"project_root": directory}, "agent": "@architect"})

    async def test_real_stdio_process_and_no_shell_interpolation(self):
        result = await self.invoke("import json,sys\np=json.load(sys.stdin)\nprint(json.dumps({'agent':p['agent']}))")
        self.assertEqual(result, {"agent": "@architect"})

    async def test_malformed_or_duplicate_json_is_rejected(self):
        for output in ('not JSON', '{"status":1,"status":2}', '[]'):
            with self.subTest(output=output), self.assertRaises(ValueError):
                await self.invoke(f"import sys\nsys.stdin.read()\nprint({output!r})")

    async def test_timeout_is_bounded_and_explained(self):
        with self.assertRaisesRegex(ProtocolError, "timed out"):
            await self.invoke("import time\ntime.sleep(30)", timeout=0.15)

    async def test_nonzero_exit_and_output_limit(self):
        with self.assertRaisesRegex(ProtocolError, "exited with code"):
            await self.invoke("import sys\nsys.stdin.read()\nsys.exit(7)")
        with self.assertRaisesRegex(ProtocolError, "stream limit"):
            await self.invoke("import sys\nsys.stdin.read()\nprint('x' * 1048577)")

    async def test_cancellation_terminates_adapter_call(self):
        future = asyncio.create_task(self.invoke("import time\ntime.sleep(30)"))
        await asyncio.sleep(0.1)
        future.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(future, 2)
