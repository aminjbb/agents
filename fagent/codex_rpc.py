"""Bounded newline JSON-RPC transport for a local Codex app-server child."""
import asyncio
import json
import os
import signal
import sys
from collections import deque

from .protocol import ProtocolError, require
from .registry import unique_keys
from .codex_errors import CodexOperationError, rpc_error


class CodexRPC:
    def __init__(self, command, cwd, env):
        self.command, self.cwd, self.env = command, cwd, env
        self.process = None
        self.serial, self.size = 0, 0
        self.pending = deque()

    async def __aenter__(self):
        self.process = await asyncio.create_subprocess_exec(
            *self.command, cwd=self.cwd, env=self.env,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE, limit=1048577,
            creationflags=0x08000000 if sys.platform == "win32" else 0,
            start_new_session=sys.platform != "win32")
        self.diagnostics = asyncio.create_task(self.discard_stderr())
        return self

    async def discard_stderr(self):
        # Drain without retaining diagnostics: provider errors can contain secrets.
        while await self.process.stderr.read(65536):
            pass

    async def send(self, message):
        self.process.stdin.write((json.dumps(message, ensure_ascii=False) + "\n").encode())
        await self.process.stdin.drain()

    async def read(self):
        try:
            line = await self.process.stdout.readline()
            self.size += len(line)
            require(self.size <= 16 * 1048576, "Codex output limit exceeded")
            require(bool(line), "Codex app-server closed unexpectedly")
            message = json.loads(line, object_pairs_hook=unique_keys)
            require(isinstance(message, dict), "Invalid Codex RPC envelope")
            return message
        except (ValueError, UnicodeError):
            raise CodexOperationError("Codex app-server closed or returned an invalid protocol message.") from None

    async def server_request(self, message):
        method = message.get("method", "")
        if method in ("item/commandExecution/requestApproval", "item/fileChange/requestApproval"):
            response = {"result": {"decision": "decline"}}
        elif method == "item/permissions/requestApproval":
            response = {"result": {"permissions": {}, "scope": "turn"}}
        else:
            response = {"error": {"code": -32601, "message": "Interactive requests unavailable"}}
        await self.send({"id": message["id"], **response})

    async def call(self, method, params):
        self.serial += 1
        identity = self.serial
        await self.send({"id": identity, "method": method, "params": params})
        while True:
            message = await self.read()
            if "method" in message and "id" in message:
                await self.server_request(message)
            elif message.get("id") == identity:
                if "error" in message:
                    raise rpc_error(method, message["error"])
                require(isinstance(message.get("result"), dict), "Missing Codex RPC result")
                return message["result"]
            elif "method" in message:
                self.pending.append(message)

    async def notification(self):
        while True:
            message = self.pending.popleft() if self.pending else await self.read()
            if "id" in message and "method" in message:
                await self.server_request(message)
            elif "method" in message:
                return message

    async def __aexit__(self, *_):
        if sys.platform == "win32" and self.process.returncode is None:
            killer = await asyncio.create_subprocess_exec(
                "taskkill", "/PID", str(self.process.pid), "/T", "/F",
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
                creationflags=0x08000000)
            await killer.wait()
        elif sys.platform != "win32":
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if self.process.returncode is None:
            self.process.kill()
        await self.process.wait()
        self.diagnostics.cancel()
        await asyncio.gather(self.diagnostics, return_exceptions=True)
