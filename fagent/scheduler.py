"""Dependency-aware concurrent execution with canonical declared write-scope locks."""
import asyncio

from .paths import conflicting, scope_keys
from .recovery import settle_repairs
from .repair_plan import invalidate_repair_inputs
from .worker import work


async def execute(state, gateway):
    tasks = state["plan"]["tasks"]
    active = {}
    capacity = state["request"]["max_parallel"]
    root = state["request"]["project_root"]
    try:
        while True:
            settle_repairs(state, gateway)
            by_id = {task["id"]: task for task in tasks}
            for task in tuple(tasks):
                if task["status"] not in ("pending", "ready"):
                    continue
                if task.get("recovery") and not task.get("invalidation_applied"):
                    if active:
                        continue
                    invalidate_repair_inputs(task, state, gateway)
                deps = [by_id[key] for key in task["depends_on"]]
                if any(dep["status"] in ("blocked", "changes_required") for dep in deps):
                    task.update(status="blocked", block_reason="dependency",
                                feedback="A prerequisite did not complete")
                    gateway.event("task_dependency_blocked", task_id=task["id"])
                    continue
                if not all(dep["status"] == "done" for dep in deps):
                    continue
                task["status"] = "ready"
                keys = scope_keys(root, task["write_scope"])
                if len(active) >= capacity or any(conflicting(keys, info[1]) for info in active.values()):
                    continue
                task["status"] = "running"
                future = asyncio.create_task(work(task, state, gateway))
                active[future] = (task, keys)
            if not active:
                # Invalidation can reset a prerequisite already visited above.
                # Rescan runnable work before declaring the schedule settled.
                if any(task["status"] in ("pending", "ready") and
                       all(by_id[key]["status"] == "done" for key in task["depends_on"])
                       for task in tasks):
                    continue
                while True:
                    blocked = [task for task in tasks if task["status"] in ("pending", "ready") and
                               any(by_id[key]["status"] in ("blocked", "changes_required")
                                   for key in task["depends_on"])]
                    if not blocked:
                        break
                    for task in blocked:
                        task.update(status="blocked", block_reason="dependency",
                                    feedback="A prerequisite did not complete")
                break
            finished, _ = await asyncio.wait(active, return_when=asyncio.FIRST_COMPLETED)
            for future in finished:
                task, _ = active.pop(future)
                try:
                    await future
                except Exception as error:
                    task.update(status="blocked", block_reason="execution_error", error=str(error))
                    gateway.event("task_error", task_id=task["id"], reason=str(error))
        gateway.event("schedule_settled")
    finally:
        for future, (task, _) in active.items():
            future.cancel()
            task.update(status="blocked", block_reason="interrupted",
                        feedback="Execution interrupted; inspect side effects before retry")
        await asyncio.gather(*active, return_exceptions=True)
        settle_repairs(state, gateway)
        if active:
            gateway.event("schedule_interrupted")
