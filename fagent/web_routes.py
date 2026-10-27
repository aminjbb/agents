"""Local API routes; no provider keys are serialized in responses."""
from pathlib import Path

from .protocol import require


def route(jobs, method, path, data):
    if method == "GET" and path == "/api/bootstrap":
        return {"agents": [manifest["metadata"] for manifest in jobs.registry.agents.values()],
                "connection": jobs.connection(), "runs": jobs.summaries(), "project_root": str(Path.cwd())}
    if path == "/api/connection":
        if method == "POST":
            return jobs.connect(data)
        if method == "DELETE":
            return jobs.disconnect()
    if method == "POST" and path == "/api/runs":
        return jobs.start(data)
    parts = path.strip("/").split("/")
    require(len(parts) in (3, 4) and parts[:2] == ["api", "runs"], "Unknown API route")
    if method == "GET" and len(parts) == 3:
        return jobs.read(parts[2])
    if method == "POST" and len(parts) == 4 and parts[3] == "resume":
        return jobs.resume(parts[2], data)
    raise ValueError("Unknown API route")
