"""One bounded task transaction: execution, evidence gate, then architect review."""
from .outcomes import grade, review
from .plans import archive_task
from .protocol import questions, require, text


async def work(task, state, gateway):
    limit = state["request"]["max_attempts"]
    while task["attempts"] < limit:
        archive_task(task)
        task.update(status="running", attempts=task["attempts"] + 1, error=None, result=None, review=None)
        gateway.event("task_running", task_id=task["id"], attempt=task["attempts"])
        try:
            prerequisites = {item["id"]: item["result"] for item in state["plan"]["tasks"]
                             if item["id"] in task["depends_on"]}
            result = await gateway.invoke(task["owner"], "execute_task",
                                          {"task": task, "prerequisite_results": prerequisites,
                                           "architecture_context": {key: value for key, value in
                                               state.get("planning", {}).items() if key not in ("status", "plan")},
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
                gateway.event("task_blocked", task_id=task["id"], reason=status)
                return
            require("changed_files" in result, "Completed tasks must report changed_files")
            quality = grade(result)
            if quality != "PASS":
                task.update(status="changes_required" if quality == "FAIL" else "blocked",
                            feedback="Required execution checks did not pass", block_reason="checks")
            else:
                task["status"] = "review"
                gateway.event("task_review", task_id=task["id"])
                decision = await gateway.invoke("@architect", "review_task", {
                    "task": task, "plan_contracts": {key: value for key, value in
                        state["plan"].items() if key != "tasks"},
                    "architecture_context": {key: value for key, value in
                        state.get("planning", {}).items() if key not in ("status", "plan")}})
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
