"""Reuse the architect's plan validator with runtime scheduling semantics."""
from copy import deepcopy
from pathlib import Path
import runpy

from .paths import scope_keys
from .protocol import require

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = PACKAGE_ROOT / "skills/architect/orchestrate-feature-delivery/scripts/validate_task_plan.py"

# Architect plans sometimes use these finite config-family shorthands. Expand
# only known families; arbitrary globs remain invalid write scopes.
KNOWN_SCOPE_FAMILIES = {
    "vite.config.*": ["vite.config.ts", "vite.config.js", "vite.config.mts",
                      "vite.config.mjs", "vite.config.cjs"],
    "tsconfig*.json": ["tsconfig.json", "tsconfig.app.json", "tsconfig.node.json"],
}


def architect_plan(result):
    """Accept the two plan envelope spellings emitted by compatible Architect prompts."""
    require(isinstance(result, dict), "Architect response must be an object")
    value = result.get("plan")
    if value is None and isinstance(result.get("planned"), dict):
        value = result["planned"]
    # Some Architect responses put the validated task graph at the envelope
    # root alongside status/metadata instead of under `plan` or `planned`.
    if value is None and isinstance(result.get("tasks"), list):
        value = {key: item for key, item in result.items()
                 if key not in ("status", "context")}
    require(isinstance(value, dict), "Architect plan must be an object")
    if "tasks" not in value and isinstance(value.get("plan"), dict):
        value = value["plan"]
    require(isinstance(value.get("tasks"), list), "Architect plan must contain a tasks list")
    return value


def normalize_architect_response(result):
    """Normalize the case and presentation used by Architect status envelopes.

    The architect skill's human-facing output contract uses uppercase labels
    (for example ``PLANNED``), while the machine response contract uses
    lowercase values. Keep the transport strict, but accept equivalent labels
    at this single protocol boundary.
    """
    require(isinstance(result, dict), "Architect response must be an object")
    value = deepcopy(result)
    status = value.get("status")
    normalized = status.strip().lower() if isinstance(status, str) else ""
    aliases = {"approved": "planned", "plan": "planned", "ready": "planned",
               "complete": "planned", "completed": "planned", "success": "planned"}
    normalized = aliases.get(normalized, normalized)
    if normalized.startswith("planned"):
        normalized = "planned"
    # A few compatible Architect envelopes omit status while carrying a
    # concrete task graph. Infer only the planning state in that case.
    if not normalized and (isinstance(value.get("tasks"), list) or
                           isinstance(value.get("plan"), dict) or
                           isinstance(value.get("planned"), dict)):
        normalized = "planned"
    require(normalized in ("planned", "needs_input", "blocked"),
            "Invalid architect planning status")
    value["status"] = normalized
    return value


def prepare(plan, req):
    require(isinstance(plan, dict), "Architect plan must be an object")
    value = deepcopy(plan)
    value["mode"] = req["mode"]
    require(isinstance(value.get("tasks"), list), "Plan must contain tasks")
    for task in value["tasks"]:
        require(isinstance(task, dict), "Task must be an object")
        scopes = task.get("write_scope")
        require(isinstance(scopes, list), f"Write scope must be a list: {task.get('id', '?')}")
        expanded = []
        for scope in scopes:
            expanded.extend(KNOWN_SCOPE_FAMILIES.get(scope, [scope]))
        task["write_scope"] = list(dict.fromkeys(expanded))
        task.setdefault("status", "pending")
        require(task["status"] == "pending", "New plans cannot claim work is already done")
    report = runpy.run_path(str(VALIDATOR))["validate_plan"](
        value, allow_serialized_writes=True)
    for task in value["tasks"]:
        scope_keys(req["project_root"], task["write_scope"])
        task.update(attempts=0, result=None, review=None, feedback="", questions=[], history=[])
    return value, report


def archive_task(task):
    if task.get("result") is not None or task.get("review") is not None or task.get("error") is not None:
        task.setdefault("history", []).append(deepcopy({key: task.get(key) for key in
            ("attempts", "status", "result", "review", "feedback", "error")}))


def reset_tasks(state, task_ids, fresh_attempt_window=False):
    """Invalidate selected tasks and all consumers; never reuse stale approval."""
    tasks = {task["id"]: task for task in state["plan"]["tasks"]}
    require(bool(task_ids) and all(key in tasks for key in task_ids), "Unknown/empty retry tasks")
    selected = set(task_ids)
    while True:
        repairs = {dep for key in selected for dep in tasks[key]["depends_on"]
                   if tasks[dep].get("recovery") and tasks[dep]["status"] != "done"}
        expanded = selected | repairs | {key for key, task in tasks.items()
                                         if selected.intersection(task["depends_on"])}
        if expanded == selected:
            break
        selected = expanded
    for key in selected:
        archive_task(tasks[key])
        # An explicit user retry starts a fresh bounded retry window. Keep the
        # previous attempt in history, but never make an exhausted run
        # permanently unrecoverable.
        tasks[key].update(status="pending", result=None, review=None, questions=[], error=None, block_reason=None)
        if tasks[key].get("recovery"):
            tasks[key]["invalidation_applied"] = False
        if fresh_attempt_window:
            tasks[key]["attempts"] = 0
            tasks[key]["recovery_epoch"] = tasks[key].get("recovery_epoch", 0) + 1
            tasks[key]["resume_allowance"] = 0
            tasks[key]["revalidation_allowance"] = 0
    for key in selected:
        repair_id = tasks[key].get("active_repair")
        if repair_id in selected:
            tasks[key]["status"] = "waiting_for_repair"
    if "audit" in state or "acceptance" in state:
        state.setdefault("delivery_history", []).append(deepcopy(
            {"audit": state.pop("audit", None), "acceptance": state.pop("acceptance", None)}))
    state["questions"] = []
    return selected
