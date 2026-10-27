"""Bounded diagnosis, independent repairs, strict verification and original-task resumption."""
from .blockers import register
from .protocol import questions, text
from .repair_plan import append_repair
from .task_context import task_context


def execution_limit(task, state):
    return (state["request"]["max_attempts"] + task.get("resume_allowance", 0)
            + task.get("revalidation_allowance", 0))


def verification_passed(task, response):
    recovery = task.get("recovery")
    if not recovery:
        return True
    passed = {item["name"] for item in response.get("checks", [])
              if item.get("required") and item.get("status") == "PASS"}
    return set(recovery["verification"]["checks"]).issubset(passed)


async def diagnose(task, state, gateway, failure, decision=None):
    blocker = register(task, failure)
    task["status"] = "diagnosing"
    gateway.event("blocker_detected", task_id=task["id"], reason=str(blocker["summary"]))
    # A failed repair is visible to the lead, but cannot spawn a recursive repair tree.
    task["diagnosis_in_progress"] = True
    try:
        if decision is None:
            context = task_context(task, state)
            context.update(failure=failure, blocker=blocker, rework_request=
                           "Diagnose the root cause. Propose a separate repair with verification "
                           "{reproduce, checks:[exact check names]}; preserve the original task. "
                           "For external blockers explain the missing capability/access; ask only necessary questions.")
            decision = await gateway.invoke("@architect", "review_task", context)
        blocker["diagnosis"] = decision
        task["status"] = "blocked"
        if decision.get("questions"):
            task["questions"] = [{**item, "id": task["id"] + "." + item["id"], "task_id": task["id"]}
                                 for item in questions(decision["questions"])]
            blocker["status"] = "needs_input"
            return
        repairs = sum(bool(item.get("repair_id")) for item in task["blockers"]
                      if item.get("epoch", 0) == task.get("recovery_epoch", 0))
        strategy = decision.get("retry_strategy")
        if (not blocker["repeated"] and strategy and
                task["attempts"] < execution_limit(task, state)):
            task.update(status="pending", feedback=text(strategy, "retry strategy"))
            blocker["status"] = "retry_scheduled"
            gateway.event("task_retry_scheduled", task_id=task["id"], reason=strategy)
            return
        if task.get("recovery") or blocker["repeated"] or repairs >= state["request"]["max_attempts"]:
            blocker["status"] = "stuck"
            task.update(block_reason="recovery_stuck", feedback="Recovery stopped: repeated failure or repair budget exhausted")
            gateway.event("recovery_stuck", task_id=task["id"], reason=task["feedback"])
            return
        change = decision.get("rework")
        if not isinstance(change, dict):
            blocker["status"] = "blocked"
            task["feedback"] = text(decision.get("summary"), "diagnosis summary")
            gateway.event("recovery_blocked", task_id=task["id"], reason=task["feedback"])
            return
        append_repair(task, state, gateway, change, blocker)
    except Exception as error:
        blocker.update(status="stuck", error=str(error))
        task.update(status="blocked", recovery_error=str(error), feedback="Invalid recovery plan: " + str(error))
        gateway.event("recovery_stuck", task_id=task["id"], reason=str(error))
    finally:
        task.pop("diagnosis_in_progress", None)


def settle_repairs(state, gateway):
    tasks = {item["id"]: item for item in state["plan"]["tasks"]}
    for task in tasks.values():
        if task["status"] != "waiting_for_repair":
            continue
        repair = tasks[task["active_repair"]]
        blocker = next(item for item in task["blockers"] if item.get("repair_id") == repair["id"])
        if repair["status"] == "done":
            blocker["status"] = "verified"
            task.update(status="pending", active_repair=None, block_reason=None,
                        resume_allowance=task.get("resume_allowance", 0) + 1,
                        feedback="Repair verified; resume the original objective and acceptance criteria")
            gateway.event("task_resuming", task_id=task["id"], repair_id=repair["id"])
        elif repair["status"] in ("blocked", "changes_required"):
            blocker["status"] = "repair_failed"
            task.update(status="blocked", block_reason="repair_failed",
                        feedback="Repair has not passed verification: " + repair["id"])
            gateway.event("recovery_stuck", task_id=task["id"], repair_id=repair["id"], reason=task["feedback"])
