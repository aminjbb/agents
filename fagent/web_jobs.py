"""Background orchestration with durable snapshots and memory-only credentials."""
import asyncio
import re
import threading
import uuid
from pathlib import Path

from .orchestrator import Orchestrator
from .protocol import ProtocolError, request, require
from .registry import Registry
from .store import Store
from .codex_setup import CodexSetupError
from .codex_errors import CodexOperationError


class SnapshotStore(Store):
    def __init__(self, path, lock):
        super().__init__(path)
        self.snapshot_lock = lock

    def save(self, state):
        # Windows denies atomic replacement while a polling reader holds the file.
        with self.snapshot_lock:
            super().save(state)


class Jobs:
    def __init__(self, directory, adapter_factory):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.adapter_factory = adapter_factory
        self.registry = Registry()
        self.lock = threading.RLock()
        self.active, self.errors = {}, {}
        self.credentials = None
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def connection(self):
        with self.lock:
            return {"configured": self.credentials is not None,
                    "model": self.credentials.get("model") if self.credentials else None}

    def connect(self, data):
        key, model = data.get("api_key", ""), data.get("model") or None
        require(isinstance(key, str) and len(key) <= 1024, "Invalid API key")
        require(model is None or isinstance(model, str) and len(model) <= 150, "Invalid model")
        credentials = {"api_key": key.strip() or None, "model": model}
        try:
            probe = asyncio.run(self.adapter_factory(**credentials).probe())
        except (CodexSetupError, CodexOperationError):
            raise
        except Exception:
            raise ProtocolError("Codex connection failed. Check CLI installation and authentication.") from None
        require(probe.get("authenticated"), "Codex is not signed in. Run codex login, then reconnect with the key blank.")
        with self.lock:
            self.credentials = credentials
        return self.connection()

    def disconnect(self):
        with self.lock:
            require(not any(self.active.values()), "Wait for active work before disconnecting")
            self.credentials = None
        return self.connection()

    def path(self, run_id):
        require(isinstance(run_id, str) and re.fullmatch(r"[a-f0-9]{32}", run_id), "Invalid run ID")
        target = (self.directory / (run_id + ".json")).resolve()
        require(target.parent == self.directory, "Run path escapes storage")
        return target

    def read(self, run_id):
        with self.lock:
            path = self.path(run_id)
            require(path.exists() or run_id in self.active, "Run not found")
            return {"id": run_id, "busy": self.active.get(run_id, False),
                    "error": self.errors.get(run_id),
                    "state": Store(path).read() if path.exists() else None}

    def summaries(self):
        output = []
        with self.lock:
            for path in sorted(self.directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
                try:
                    state = self.read(path.stem)["state"]
                    output.append({"id": path.stem, "status": state["status"],
                                   "text": state["request"]["text"],
                                   "project_root": state["request"]["project_root"],
                                   "updated_at": state.get("events", [{}])[-1].get("at")})
                except (ValueError, OSError, KeyError, IndexError):
                    continue
        return output

    def start(self, data):
        payload = {**data, "mode": "plan"}
        request(payload)
        run_id = uuid.uuid4().hex
        return self.submit(run_id, payload, starting=True)

    def resume(self, run_id, data):
        saved = self.read(run_id)
        require(type(data.get("execute", False)) is bool, "execute must be boolean")
        require(not data.get("execute") or bool((saved["state"] or {}).get("plan")),
                "Review an existing plan before authorizing execution")
        retries = data.get("retry_tasks", [])
        require(isinstance(retries, list) and all(isinstance(x, str) for x in retries), "Invalid retries")
        require(data.get("answers") is None or isinstance(data["answers"], dict), "Invalid answers")
        return self.submit(run_id, data)

    def submit(self, run_id, data, starting=False):
        with self.lock:
            require(self.credentials is not None, "Connect to Codex first")
            require(not self.active.get(run_id), "Run is already active")
            adapter = self.adapter_factory(**self.credentials)
            self.active[run_id] = True
            self.errors.pop(run_id, None)
            asyncio.run_coroutine_threadsafe(self.drive(run_id, data, adapter, starting), self.loop)
        return {"id": run_id}

    async def drive(self, run_id, data, adapter, starting):
        try:
            with SnapshotStore(self.path(run_id), self.lock) as store:
                # Keep the same bounded retry policy in the web control room;
                # an unsuccessful agent must surface to Tech Lead instead of
                # looping forever while returning the same result.
                runner = Orchestrator(adapter, store, self.registry, unlimited_attempts=False)
                if starting:
                    await runner.start(data)
                else:
                    await runner.resume(data.get("answers"), data.get("retry_tasks"), data.get("execute", False))
        except ProtocolError as error:
            self.errors[run_id] = str(error)
        except Exception:
            self.errors[run_id] = "Operation failed. Inspect the saved run and local CLI setup before retrying."
        finally:
            with self.lock:
                self.active[run_id] = False

    def close(self):
        if self.loop.is_closed():
            return
        async def cancel():
            tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        asyncio.run_coroutine_threadsafe(cancel(), self.loop).result(timeout=15)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=5)
        if not self.thread.is_alive():
            self.loop.close()
