"""Validate task-plan structure only; never execute tasks or inspect application files."""
import json
import re
import sys
from collections import deque
from pathlib import Path

OWNERS = {"@architect", "@state-master", "@ui-crafter", "@navigator",
          "@form-wizard", "@auditor"}
STATUSES = {"pending", "ready", "running", "done", "blocked"}
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{index}" for prefix in ("COM", "LPT") for index in range(1, 10)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def scope_path(value):
    require(isinstance(value, str) and value.strip() == value and bool(value),
            "Write scopes must be nonempty canonical relative path strings")
    require(not any(char in value for char in '\\:*?[]{}<>|"') and
            not value.startswith("/") and not any(ord(c) < 32 for c in value),
            f"Unsupported write scope: {value!r}")
    parts = value.rstrip("/").split("/")
    require(not value.endswith("//") and
            all(part and part not in {".", ".."} and
                part == part.strip() and not part.endswith(".") and
                part.split(".")[0].upper() not in RESERVED for part in parts),
            f"Noncanonical write scope: {value!r}")
    return value.casefold()


def overlaps(left, right):
    left, right = left.rstrip("/"), right.rstrip("/")
    return left == right or right.startswith(left + "/") or left.startswith(right + "/")


def validate_plan(plan, allow_serialized_writes=False):
    require(isinstance(plan, dict), "Plan must be an object")
    require(isinstance(plan.get("mode"), str) and
            plan["mode"] in {"plan", "execute"}, "Mode must be plan or execute")
    tasks = plan.get("tasks")
    require(isinstance(tasks, list) and bool(tasks), "Tasks must be a nonempty list")
    by_id, scopes = {}, {}
    for task in tasks:
        require(isinstance(task, dict), "Each task must be an object")
        task_id = task.get("id")
        require(isinstance(task_id, str) and
                re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", task_id), "Invalid task ID")
        require(task_id not in by_id, f"Duplicate task ID: {task_id}")
        require(isinstance(task.get("owner"), str) and
                task["owner"] in OWNERS, f"Unknown owner: {task_id}")
        require(isinstance(task.get("status"), str) and
                task["status"] in STATUSES, f"Invalid status: {task_id}")
        for field in ("objective", "deliverable"):
            require(isinstance(task.get(field), str) and bool(task[field].strip()),
                    f"Missing {field}: {task_id}")
        acceptance = task.get("acceptance_criteria")
        require(isinstance(acceptance, list) and bool(acceptance) and
                all(isinstance(item, str) and bool(item.strip()) for item in acceptance),
                f"Invalid acceptance criteria: {task_id}")
        deps = task.get("depends_on")
        require(isinstance(deps, list) and all(isinstance(dep, str) for dep in deps),
                f"Invalid dependencies: {task_id}")
        require(len(deps) == len(set(deps)), f"Duplicate dependencies: {task_id}")
        paths = task.get("write_scope")
        require(isinstance(paths, list), f"Write scope must be a list: {task_id}")
        scopes[task_id] = [scope_path(path) for path in paths]
        require(len(scopes[task_id]) == len(set(scopes[task_id])),
                f"Duplicate write scopes: {task_id}")
        by_id[task_id] = task
    children = {task_id: [] for task_id in by_id}
    indegree, ancestors = {}, {task_id: set() for task_id in by_id}
    for task_id, task in by_id.items():
        for dep in task["depends_on"]:
            require(dep in by_id and dep != task_id, f"Invalid dependency: {task_id} -> {dep}")
            children[dep].append(task_id)
        indegree[task_id] = len(task["depends_on"])
    ready = deque(task_id for task_id, degree in indegree.items() if degree == 0)
    order = []
    while ready:
        task_id = ready.popleft()
        order.append(task_id)
        for child in children[task_id]:
            ancestors[child].update(ancestors[task_id] | {task_id})
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
    require(len(order) == len(tasks), "Task dependency cycle")
    for task_id, task in by_id.items():
        if task["status"] in {"ready", "running", "done"}:
            require(all(by_id[dep]["status"] == "done" for dep in task["depends_on"]),
                    f"Prerequisites not done: {task_id}")
    conflicts = []
    for index, left in enumerate(order):
        for right in order[index + 1:]:
            if left in ancestors[right] or right in ancestors[left]:
                continue
            if any(overlaps(a, b) for a in scopes[left] for b in scopes[right]):
                conflicts.append([left, right])
                require(allow_serialized_writes, f"Unordered write conflict: {left} / {right}")
    return {"status": "PASS", "task_count": len(tasks), "topological_order": order,
            "serialized_write_conflicts": conflicts,
            "scope": "Structure only; no execution, permission, contract, or runtime verification"}


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_task_plan.py <task-plan.json>", file=sys.stderr)
        return 2
    try:
        plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"),
                          object_pairs_hook=unique_keys)
        print(json.dumps(validate_plan(plan), ensure_ascii=False))
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
