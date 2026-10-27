"""Runtime protocol validation, independent of any LLM/provider SDK."""
import uuid
from pathlib import Path


class ProtocolError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ProtocolError(message)


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be text")
    return value


def strings(value, label, nonempty=False):
    require(isinstance(value, list), f"{label} must be a list")
    for item in value:
        text(item, label)
    require(not nonempty or bool(value), f"{label} must not be empty")
    return value


def request(data):
    require(isinstance(data, dict), "Request must be an object")
    root = Path(text(data.get("project_root"), "project_root")).resolve()
    require(root.is_dir(), "project_root must be an existing directory")
    mode = data.get("mode", "plan")
    require(mode in ("plan", "execute"), "mode must be plan or execute")
    capacity = data.get("max_parallel", 3)
    attempts = data.get("max_attempts", 2)
    require(type(capacity) is int and 1 <= capacity <= 16, "max_parallel must be 1..16")
    require(type(attempts) is int and 1 <= attempts <= 5, "max_attempts must be 1..5")
    return {"id": uuid.uuid4().hex, "project_root": str(root),
            "text": text(data.get("text"), "request text"), "mode": mode,
            "max_parallel": capacity, "max_attempts": attempts, "answers": {}, "clarifications": []}


def questions(value):
    require(isinstance(value, list) and bool(value), "questions must be a nonempty list")
    ids = set()
    for item in value:
        require(isinstance(item, dict), "Question must be an object")
        key = text(item.get("id"), "question id")
        require(key not in ids, "Duplicate question id")
        ids.add(key)
        text(item.get("question"), "question")
        if "options" in item:
            strings(item["options"], "question options", nonempty=True)
    return value


def checks(value):
    require(isinstance(value, list) and bool(value), "checks must be a nonempty list")
    seen = set()
    for item in value:
        require(isinstance(item, dict), "Check must be an object")
        name = text(item.get("name"), "check name")
        require(name not in seen, "Duplicate check name")
        seen.add(name)
        require(type(item.get("required")) is bool, "Check required must be boolean")
        require(item.get("status") in ("PASS", "FAIL", "NOT_RUN", "INCONCLUSIVE", "N/A"),
                "Invalid check status")
        text(item.get("evidence"), "check evidence")
        if item["status"] == "N/A":
            require(not item["required"], "Required checks cannot be N/A")
    require(any(item["required"] for item in value), "At least one check must be required")
    return all(not item["required"] or item["status"] == "PASS" for item in value)


def evidence(response):
    require(isinstance(response, dict), "Agent response must be an object")
    text(response.get("summary"), "summary")
    strings(response.get("evidence"), "evidence", nonempty=True)
    return checks(response.get("checks"))
