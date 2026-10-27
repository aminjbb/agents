"""Reuse the architect's plan validator with runtime scheduling semantics."""
from copy import deepcopy
from pathlib import Path
import runpy

from .paths import scope_keys
from .protocol import require

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = PACKAGE_ROOT / "skills/architect/orchestrate-feature-delivery/scripts/validate_task_plan.py"


def prepare(plan, req):
    require(isinstance(plan, dict), "Architect plan must be an object")
    value = deepcopy(plan)
    value["mode"] = req["mode"]
    require(isinstance(value.get("tasks"), list), "Plan must contain tasks")
    for task in value["tasks"]:
        require(isinstance(task, dict), "Task must be an object")
        task.setdefault("status", "pending")
        require(task["status"] == "pending", "New plans cannot claim work is already done")
    report = runpy.run_path(str(VALIDATOR))["validate_plan"](
        value, allow_serialized_writes=True)
    for task in value["tasks"]:
        scope_keys(req["project_root"], task["write_scope"])
        task.update(attempts=0, result=None, review=None, feedback="", questions=[], history=[])
    return value, report


def archive_task(task):
    if task.get("result") is not None or task.get("review") is not None:
        task.setdefault("history", []).append(deepcopy({key: task.get(key) for key in
            ("attempts", "status", "result", "review", "feedback", "error")}))


def reset_tasks(state, task_ids):
    """Invalidate selected tasks and all consumers; never reuse stale approval."""
    tasks = {task["id"]: task for task in state["plan"]["tasks"]}
    require(bool(task_ids) and all(key in tasks for key in task_ids), "Unknown/empty retry tasks")
    selected = set(task_ids)
    while True:
        expanded = selected | {key for key, task in tasks.items()
                               if selected.intersection(task["depends_on"])}
        if expanded == selected:
            break
        selected = expanded
    limit = state["request"]["max_attempts"]
    require(all(tasks[key]["attempts"] < limit for key in selected), "Task attempt limit reached")
    for key in selected:
        archive_task(tasks[key])
        tasks[key].update(status="pending", result=None, review=None, questions=[])
    if "audit" in state or "acceptance" in state:
        state.setdefault("delivery_history", []).append(deepcopy(
            {"audit": state.pop("audit", None), "acceptance": state.pop("acceptance", None)}))
    state["questions"] = []
    return selected
