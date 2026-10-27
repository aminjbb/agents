"""One execution attempt; retries and repairs must reacquire scheduler locks."""
from .outcomes import grade, review
from .plans import archive_task
from .protocol import questions, require, text
from .recovery import diagnose, execution_limit, verification_passed
from .task_context import task_context


async def work(task, state, gateway):
    if task["attempts"] >= execution_limit(task, state):
        task.update(status="blocked", block_reason="attempt_limit",
                    feedback="Attempt limit reached; inspect evidence before explicit retry")
        gateway.event("task_attempt_limit", task_id=task["id"])
        return
    archive_task(task)
    task.pop("recovery_error", None)
    task.update(status="running", attempts=task["attempts"] + 1, error=None, result=None, review=None)
    gateway.event("task_running", task_id=task["id"], attempt=task["attempts"])
    try:
        context = task_context(task, state)
        dependencies = [item for item in state["plan"]["tasks"] if item["id"] in task["depends_on"]]
        context.update(prerequisite_results={item["id"]: item["result"] for item in dependencies},
                       prerequisite_states={item["id"]: {key: item.get(key) for key in
                           ("status", "attempts", "block_reason")} for item in dependencies})
        result = await gateway.invoke(task["owner"], "execute_task", context, task["write_scope"])
        task["result"] = result
        status = result.get("status")
        require(status in ("completed", "needs_input", "blocked"), "Invalid task response status")
        if status != "completed":
            task.update(status="blocked", feedback=text(result.get("summary"), "summary"), block_reason=status)
            if status == "needs_input":
                if not result.get("changed_files"):
                    task["attempts"] -= 1
                task["questions"] = [{**item, "id": task["id"] + "." + item["id"], "task_id": task["id"]}
                                     for item in questions(result.get("questions"))]
            else:
                await diagnose(task, state, gateway, result)
            gateway.event("task_blocked", task_id=task["id"], reason=status)
            return
        require("changed_files" in result, "Completed tasks must report changed_files")
        if grade(result) != "PASS" or not verification_passed(task, result):
            task.update(status="blocked", feedback="Required execution/repair checks did not pass",
                        block_reason="checks")
            await diagnose(task, state, gateway, result)
            return
        task["status"] = "review"
        gateway.event("task_review", task_id=task["id"])
        context = task_context(task, state)
        if task.get("recovery"):
            context["recovery_verification"] = task["recovery"]["verification"]
            gateway.event("repair_verifying", task_id=task["id"], parent_id=task["recovery"]["parent_id"])
        decision = await gateway.invoke("@architect", "review_task", context)
        task.update(review=decision, status=review(decision), feedback=decision["summary"])
        if task.get("recovery") and not verification_passed(task, decision):
            task.update(status="blocked", block_reason="repair_verification",
                        feedback="Reviewer did not confirm the original reproduction checks")
        if task["status"] != "done" and (decision.get("rework") or task["status"] == "blocked"):
            await diagnose(task, state, gateway, decision, decision=decision)
        elif task["status"] == "changes_required":
            task["status"] = "pending"
        gateway.event("task_result", task_id=task["id"], status=task["status"])
    except Exception as error:
        task.update(status="blocked", block_reason="execution_error", error=str(error), feedback=str(error))
        gateway.event("task_error", task_id=task["id"], reason=str(error))
        if not task.get("diagnosis_in_progress"):
            try:
                await diagnose(task, state, gateway, {"summary": str(error), "category": "execution_error"})
            except Exception as diagnosis_error:
                task["recovery_error"] = str(diagnosis_error)
                gateway.event("recovery_stuck", task_id=task["id"], reason=str(diagnosis_error))
