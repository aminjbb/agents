"""Final independent quality review, architectural acceptance, and bounded rework."""
from .outcomes import audit, review
from .plans import reset_tasks
from .protocol import require, strings


async def finalize(state, gateway):
    context = {"plan": state["plan"], "architecture_context": {
        key: value for key, value in state.get("planning", {}).items() if key not in ("status", "plan")}}
    result = await gateway.invoke("@auditor", "review_delivery", context)
    state["audit"] = result
    verdict = audit(result)
    decision = await gateway.invoke("@architect", "accept_delivery", {**context, "audit": result})
    state["acceptance"] = decision
    acceptance = review(decision)
    if verdict == "PASS" and acceptance == "done":
        state["status"] = "simulated" if state["simulation"] else "delivered"
        gateway.event("delivery_finished", status=state["status"])
        return False
    state["status"] = "blocked" if verdict == "INCOMPLETE" or acceptance == "blocked" else "changes_required"
    retry = decision.get("retry_tasks", [])
    strings(retry, "retry_tasks")
    require(len(retry) == len(set(retry)), "Duplicate retry tasks")
    if retry and state["status"] == "changes_required":
        for task in state["plan"]["tasks"]:
            if task["id"] in retry:
                task["feedback"] = decision["summary"]
        try:
            selected = reset_tasks(state, retry)
        except ValueError as error:
            state["error"] = str(error)
            gateway.event("rework_blocked", reason=str(error))
            return False
        gateway.event("rework_scheduled", task_ids=sorted(selected))
        return True
    gateway.event("delivery_not_accepted", status=state["status"])
    return False
