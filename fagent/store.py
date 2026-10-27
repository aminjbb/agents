"""Atomic snapshots and exclusive run ownership; no implicit stale-lock deletion."""
import json
import os
import tempfile
from pathlib import Path

from .protocol import require
from .registry import load_json


class Store:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.lock_path = self.path.with_name(self.path.name + ".lock")

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise ValueError("Run is locked; inspect its owner before removing a stale lock") from error
        os.write(self.lock_fd, str(os.getpid()).encode("ascii"))
        return self

    def __exit__(self, *_):
        os.close(self.lock_fd)
        self.lock_path.unlink()

    def read(self):
        return load_json(self.path)

    def create(self, state):
        require(not self.path.exists(), "State file already exists; use resume")
        self.save(state)

    def save(self, state):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".run-", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(state, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            Path(temporary).unlink(missing_ok=True)
