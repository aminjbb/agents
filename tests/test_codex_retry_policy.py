"""Retry policy tests simulate a transport failure after an actual temporary-file write."""
import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fagent.codex_adapter import CodexAdapter
from fagent.codex_errors import CodexOperationError


class CodexRetryPolicyTests(unittest.IsolatedAsyncioTestCase):
    def packet(self, root, writable=False):
        return {"request": {"project_root": root, "mode": "execute" if writable else "plan"},
                "operation": "execute_task" if writable else "plan",
                "allowed_write_scope": ["output.txt"] if writable else []}

    async def test_failure_after_write_is_not_automatically_replayed(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.txt"
            adapter = CodexAdapter(command=["unused"])
            attempts = 0

            async def disconnected(callback, root):
                nonlocal attempts
                attempts += 1
                with output.open("a", encoding="utf-8") as stream:
                    stream.write("X")
                raise CodexOperationError("Stream interrupted after changing a file", retryable=True)

            adapter._bounded = disconnected
            with patch("fagent.codex_adapter.asyncio.sleep", new_callable=AsyncMock) as sleep:
                with self.assertRaises(CodexOperationError):
                    await adapter.invoke(self.packet(directory, writable=True))
                sleep.assert_not_awaited()
            self.assertEqual(attempts, 1)
            self.assertEqual(output.read_text(), "X")

    async def test_read_only_transient_retry_is_bounded_with_backoff(self):
        adapter = CodexAdapter(command=["unused"])
        adapter._bounded = AsyncMock(side_effect=[CodexOperationError("Busy", retryable=True)] * 3)
        with tempfile.TemporaryDirectory() as directory:
            with patch("fagent.codex_adapter.asyncio.sleep", new_callable=AsyncMock) as sleep:
                with self.assertRaises(CodexOperationError):
                    await adapter.invoke(self.packet(directory))
                self.assertEqual(adapter._bounded.await_count, 3)
                self.assertEqual([call.args for call in sleep.await_args_list], [(1,), (2,)])

    async def test_read_only_retry_can_succeed(self):
        adapter = CodexAdapter(command=["unused"])
        adapter._bounded = AsyncMock(side_effect=[CodexOperationError("Busy", retryable=True), {"status": "planned"}])
        with tempfile.TemporaryDirectory() as directory:
            with patch("fagent.codex_adapter.asyncio.sleep", new_callable=AsyncMock):
                result = await adapter.invoke(self.packet(directory))
            self.assertEqual(result["status"], "planned")
            self.assertEqual(adapter._bounded.await_count, 2)

    async def test_nonretryable_error_and_cancellation_do_not_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            for error in (CodexOperationError("Access denied"), asyncio.CancelledError()):
                adapter = CodexAdapter(command=["unused"])
                adapter._bounded = AsyncMock(side_effect=error)
                with self.subTest(error=type(error).__name__), self.assertRaises(type(error)):
                    await adapter.invoke(self.packet(directory))
                self.assertEqual(adapter._bounded.await_count, 1)
