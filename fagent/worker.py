"""One bounded task transaction: execution, evidence gate, then architect review."""
from .outcomes import grade, review
from .plans import archive_task
from .paths import scope_keys
from .protocol import questions, require, text


def architecture_context(state):
    """Share architectural metadata without the stale planned task graph."""
    def strip_tasks(value):
        if isinstance(value, dict):
            return {key: strip_tasks(item) for key, item in value.items() if key != "tasks"}
        if isinstance(value, list):
            return [strip_tasks(item) for item in value]
        return value
    return strip_tasks({key: value for key, value in state.get("planning", {}).items()
                        if key not in ("status", "plan")})


def normalize_execution_owner(task):
    """Keep implementation and audit work with their specialist owners."""
    if task.get("owner") != "@architect":
        return
    scope = task.get("write_scope", [])
    objective = str(task.get("objective", "")).lower()
    if any(path.startswith(("src/pages/", "src/widgets/", "src/features/",
                            "src/entities/", "src/shared/ui/")) for path in scope):
        task["owner"] = "@ui-crafter"
    elif any(word in objective for word in ("audit", "review", "quality", "بازبینی", "کیفیت")):
        task["owner"] = "@auditor"


async def work(task, state, gateway):
    limit = state["request"]["max_attempts"]
    normalize_execution_owner(task)
    while state.get("unlimited_attempts") or task["attempts"] < limit:
        archive_task(task)
        task.update(status="running", attempts=task["attempts"] + 1, error=None, result=None, review=None)
        gateway.event("task_running", task_id=task["id"], attempt=task["attempts"])
        try:
            prerequisites = {item["id"]: item["result"] for item in state["plan"]["tasks"]
                             if item["id"] in task["depends_on"]}
            prerequisite_states = {item["id"]: {
                "status": item["status"],
                "attempts": item["attempts"],
                "block_reason": item.get("block_reason")
            } for item in state["plan"]["tasks"] if item["id"] in task["depends_on"]}
            result = await gateway.invoke(task["owner"], "execute_task",
                                          {"task": task, "prerequisite_results": prerequisites,
                                           "prerequisite_states": prerequisite_states,
                                           "architecture_context": architecture_context(state),
                                           "plan_contracts": {key: value for key, value in
                                               state["plan"].items() if key != "tasks"}},
                                          task["write_scope"])
            task["result"] = result
            status = result.get("status")
            require(status in ("completed", "needs_input", "blocked"), "Invalid task response status")
            if status != "completed":
                task.update(status="blocked", feedback=text(result.get("summary"), "summary"))
                task["block_reason"] = status
                if status == "needs_input":
                    if not result.get("changed_files"):
                        task["attempts"] -= 1
                    task["questions"] = [{**item, "id": task["id"] + "." + item["id"],
                                          "task_id": task["id"]}
                                         for item in questions(result.get("questions"))]
                decision = await rework_decision(task, state, gateway, result)
                if decision:
                    continue
                gateway.event("task_blocked", task_id=task["id"], reason=status)
                return
            require("changed_files" in result, "Completed tasks must report changed_files")
            # Static implementation evidence can proceed when runtime browser
            # coverage is unavailable; final review/audit still requires it.
            quality = grade(result, allow_inconclusive=True)
            if quality != "PASS":
                task.update(status="changes_required" if quality == "FAIL" else "blocked",
                            feedback="Required execution checks did not pass", block_reason="checks")
                decision = await rework_decision(task, state, gateway, result)
                if decision:
                    continue
            else:
                task["status"] = "review"
                gateway.event("task_review", task_id=task["id"])
                decision = await gateway.invoke("@architect", "review_task", {
                    "task": task, "plan_contracts": {key: value for key, value in
                        state["plan"].items() if key != "tasks"},
                    "architecture_context": architecture_context(state)})
                if apply_rework(task, state, gateway, decision):
                    continue
                task.update(review=decision, status=review(decision), feedback=decision["summary"])
            gateway.event("task_result", task_id=task["id"], status=task["status"])
            if task["status"] != "changes_required":
                return
        except Exception as error:
            task.update(status="blocked", block_reason="execution_error", error=str(error))
            gateway.event("task_error", task_id=task["id"], reason=str(error))
            return
    task["feedback"] = task.get("feedback", "") + " (attempt limit reached)"
    gateway.event("task_attempt_limit", task_id=task["id"])


def apply_rework(task, state, gateway, decision):
    change = decision.get("rework") if isinstance(decision, dict) else None
    if not isinstance(change, dict):
        return False
    owner = change.get("owner", task["owner"])
    scope = change.get("write_scope", task["write_scope"])
    require(owner in gateway.registry.agents, "Rework owner unavailable")
    require(isinstance(scope, list), "Rework write_scope must be a list")
    scope_keys(state["request"]["project_root"], scope)
    if "objective" in change:
        text(change["objective"], "rework objective")
        task["objective"] = change["objective"]
    if "acceptance_criteria" in change:
        require(isinstance(change["acceptance_criteria"], list) and change["acceptance_criteria"],
                "Rework acceptance_criteria must be nonempty")
        task["acceptance_criteria"] = change["acceptance_criteria"]
    task.update(owner=owner, write_scope=scope, status="changes_required",
                feedback=text(decision.get("summary"), "summary"), result=None,
                review=None, questions=[])
    gateway.event("task_reassigned", task_id=task["id"], owner=owner, write_scope=scope)
    return True


def fallback_rework(task, state, gateway, failure):
    """Assign a bounded specialist fallback when Tech Lead omits rework."""
    text_blob = str(failure).lower()
    if any(word in text_blob for word in ("browser", "viewport", "keyboard", "accessibility")):
        owner, scope = "@auditor", []
    elif any(word in text_blob for word in ("integration", "app.tsx", "assembly", "route")):
        owner, scope = "@navigator", list(dict.fromkeys(task["write_scope"] + ["src/App.tsx"]))
    elif any(word in text_blob for word in ("source of truth", "canonical", "entities/product")):
        owner, scope = "@ui-crafter", list(dict.fromkeys(task["write_scope"] +
                                                        ["src/pages/", "src/widgets/"]))
    else:
        return False
    if owner == task["owner"] and scope == task["write_scope"]:
        return False
    scope_keys(state["request"]["project_root"], scope)
    task.update(owner=owner, write_scope=scope, status="changes_required",
                feedback="Tech Lead fallback assignment: " + text(failure.get("summary"), "summary"),
                result=None, review=None, questions=[])
    gateway.event("task_reassigned_fallback", task_id=task["id"], owner=owner, write_scope=scope)
    return True


async def rework_decision(task, state, gateway, failure):
    decision = await gateway.invoke("@architect", "review_task", {
        "task": task,
        "failure": failure,
        "rework_request": "If the failure needs another owner or write scope, return rework with the exact authorized changes.",
        "plan_contracts": {key: value for key, value in state["plan"].items() if key != "tasks"},
        "architecture_context": architecture_context(state)})
    return apply_rework(task, state, gateway, decision) or fallback_rework(task, state, gateway, failure)
