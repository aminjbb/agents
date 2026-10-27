"""Validate and append a repair dependency without replacing the original task contract."""
from copy import deepcopy

from .paths import conflicting, scope_keys
from .plans import prepare, reset_tasks
from .protocol import require, strings, text


def append_repair(task, state, gateway, change, blocker):
    verification = change.get("verification")
    require(isinstance(verification, dict), "Repair requires verification: {reproduce, checks}")
    text(verification.get("reproduce"), "repair reproduction")
    names = strings(verification.get("checks"), "repair verification checks", nonempty=True)
    require(len(names) == len(set(names)), "Duplicate repair verification checks")
    failed = {item["name"] for item in blocker["failure"].get("checks", [])
              if item.get("required") and item.get("status") != "PASS"}
    require(failed.issubset(names), "Repair must recheck every original failing required check")
    require(change.get("owner") in gateway.registry.agents, "Repair owner unavailable")
    tasks = state["plan"]["tasks"]
    existing = {item["id"] for item in tasks}
    number = 1
    while f'{task["id"]}-repair-{number}' in existing:
        number += 1
    repair_id = f'{task["id"]}-repair-{number}'
    repair = {"id": repair_id, "owner": change["owner"],
              "objective": text(change.get("objective"), "repair objective"),
              "deliverable": "Verified removal of blocker " + blocker["id"],
              "acceptance_criteria": strings(change.get("acceptance_criteria"), "repair criteria", True),
              "write_scope": change.get("write_scope"),
              "depends_on": change.get("depends_on", list(task["depends_on"])), "status": "pending"}
    # Validate the entire proposed graph before committing any dependency/scope change.
    candidate = deepcopy(state["plan"])
    for item in candidate["tasks"]:
        item["status"] = "pending"
        if item["id"] == task["id"]:
            item["depends_on"].append(repair_id)
    candidate["tasks"].append(repair)
    prepared, report = prepare(candidate, state["request"])
    repair = prepared["tasks"][-1]
    repair["recovery"] = {"parent_id": task["id"], "blocker_id": blocker["id"],
                          "verification": deepcopy(verification), "failure": deepcopy(blocker["failure"])}
    tasks.append(repair)
    task["depends_on"].append(repair_id)
    task.update(status="waiting_for_repair", active_repair=repair_id, block_reason="repair",
                feedback="Waiting for verified repair: " + repair_id)
    blocker.update(status="repair_queued", repair_id=repair_id, verification=deepcopy(verification))
    state["plan_validation"] = report
    gateway.event("repair_queued", task_id=repair_id, parent_id=task["id"],
                  agent=repair["owner"], reason=str(blocker["summary"]))


def invalidate_repair_inputs(repair, state, gateway):
    """Called only with no active workers: never reset an in-flight consumer."""
    if repair.get("invalidation_applied"):
        return
    tasks = state["plan"]["tasks"]
    root = state["request"]["project_root"]
    keys = scope_keys(root, repair["write_scope"])
    by_id = {item["id"]: item for item in tasks}
    writers = [item for item in tasks if item["status"] == "done" and
               conflicting(keys, scope_keys(root, item["write_scope"]))]
    # Do not reapply an older fix over a newer one. Its original consumer must
    # prove current acceptance again; the repair record remains historical evidence.
    affected = {item.get("recovery", {}).get("parent_id", item["id"]) for item in writers}
    affected = [key for key in affected if by_id[key]["status"] == "done"]
    waiting = [item for item in tasks if item["status"] == "waiting_for_repair"]
    if affected:
        invalidated = reset_tasks(state, affected)
        for item in tasks:
            if item["id"] in invalidated:
                item["revalidation_allowance"] = min(state["request"]["max_attempts"],
                                                     item.get("revalidation_allowance", 0) + 1)
        for item in waiting:
            item["status"] = "waiting_for_repair"
        gateway.event("repair_consumers_invalidated", task_id=repair["id"], tasks=sorted(invalidated))
    repair["invalidation_applied"] = True
