"""Real local Codex bridge. Scope declarations are not per-file OS isolation.

See https://learn.chatgpt.com/docs/app-server. API-key auth uses a disposable
CODEX_HOME; CLI auth is reused only when no key is supplied. probe is not an
inference/entitlement check. Workspace sandboxing still permits the entire cwd;
use an isolated checkout for untrusted tasks and inspect actual side effects.
"""
import asyncio
import json
import os
import tempfile
from pathlib import Path

from .codex_rpc import CodexRPC
from .codex_setup import CodexSetupError, executable_command, existing_home
from .codex_errors import CodexOperationError, turn_error
from .codex_response import AgentResponse
from .paths import scope_keys
from .protocol import ProtocolError, require


class CodexAdapter:
    simulation = False

    def __init__(self, api_key=None, model=None, command=None):
        self.api_key, self.model = api_key or None, model or None
        self.command = command or [*executable_command(), "app-server", "--listen", "stdio://"]
        self.timeout = 300

    async def _session(self, callback, cwd):
        with tempfile.TemporaryDirectory(prefix="fagent-codex-") as temporary:
            env = os.environ.copy()
            if not self.api_key:
                env["CODEX_HOME"] = existing_home(env)
            if self.api_key:
                env["CODEX_HOME"] = temporary
                # Avoid exposing keys to child tool environments or local auth stores.
                env.pop("OPENAI_API_KEY", None)
                env.pop("CODEX_API_KEY", None)
                Path(temporary, "config.toml").write_text(
                    'cli_auth_credentials_store = "file"\n'
                    '[shell_environment_policy]\ninherit = "core"\n'
                    'exclude = ["OPENAI_API_KEY", "CODEX_API_KEY"]\n', encoding="utf-8")
            async with CodexRPC(self.command, cwd, env) as rpc:
                await rpc.call("initialize", {"clientInfo": {
                    "name": "fagent_studio", "title": "FAgent Studio", "version": "0.1.0"}})
                await rpc.send({"method": "initialized", "params": {}})
                if self.api_key:
                    await rpc.call("account/login/start", {"type": "apiKey", "apiKey": self.api_key})
                return await callback(rpc)

    async def _bounded(self, callback, cwd):
        try:
            return await asyncio.wait_for(self._session(callback, cwd), self.timeout)
        except asyncio.TimeoutError:
            raise ProtocolError("Codex timed out; inspect side effects before retry") from None
        except asyncio.CancelledError:
            raise
        except (CodexSetupError, CodexOperationError):
            raise
        except FileNotFoundError:
            raise CodexSetupError("Codex could not start. Check FAGENT_CODEX_BIN and restart the server.") from None
        except PermissionError:
            raise CodexSetupError("Codex access was denied. Check access to the CLI and CODEX_HOME.") from None
        except Exception:
            # Never forward subprocess/provider exception text or credential-bearing data.
            raise ProtocolError("Codex operation failed; check CLI, authentication and sandbox setup") from None

    async def probe(self):
        """Return connection/auth metadata without making a paid model request."""
        async def inspect(rpc):
            account = await rpc.call("account/read", {"refreshToken": False})
            identity = account.get("account")
            return {"connected": True, "authenticated": bool(identity) or
                    account.get("requiresOpenaiAuth") is False,
                    "auth_type": identity.get("type") if isinstance(identity, dict) else None}
        return await self._bounded(inspect, str(Path.cwd()))

    async def invoke(self, packet):
        root = str(Path(packet["request"]["project_root"]).resolve())
        scopes = packet.get("allowed_write_scope", [])
        scope_keys(root, scopes)
        writable = (packet.get("operation") == "execute_task" and
                    packet["request"].get("mode") == "execute" and bool(scopes))
        require(not scopes or writable, "Codex review/planning operations must be read-only")

        async def execute(rpc):
            thread = await rpc.call("thread/start", {
                "cwd": root, "model": self.model, "ephemeral": True,
                "approvalPolicy": "never", "sandbox": "workspace-write" if writable else "read-only",
                "developerInstructions": "Act as the supplied agent. Follow its complete instruction and "
                "skill definitions. Enforce allowed_write_scope; report blockers rather than escaping "
                "the sandbox. Return exactly one JSON object matching response_contract. "
                "Never fabricate evidence or test results. No releases or external mutations."})
            thread_id = thread["thread"]["id"]
            policy = {"type": "workspaceWrite", "writableRoots": [root],
                      "networkAccess": False, "excludeSlashTmp": True,
                      "excludeTmpdirEnvVar": True} if writable else {"type": "readOnly"}
            started = await rpc.call("turn/start", {
                "threadId": thread_id, "cwd": root, "approvalPolicy": "never",
                "sandboxPolicy": policy,
                "input": [{"type": "text", "text": json.dumps(packet, ensure_ascii=False)}]})
            turn_id, response = started["turn"]["id"], AgentResponse()
            while True:
                event = await rpc.notification()
                params = event.get("params", {})
                if params.get("threadId") != thread_id:
                    continue
                if params.get("turnId") == turn_id:
                    response.observe(event)
                if event["method"] == "turn/completed" and params.get("turn", {}).get("id") == turn_id:
                    if params["turn"].get("status") != "completed":
                        raise turn_error(params["turn"].get("error"))
                    return response.decode(self.api_key, operation=packet.get("operation"))
        for attempt in range(3):
            try:
                return await self._bounded(execute, root)
            except CodexOperationError as error:
                # A failed writable turn may already have changed files. Only
                # read-only operations are safe to replay at this transport layer.
                if writable or not error.retryable or attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
