"""Stable context shared by execution and read-only architectural review."""


def architecture_context(state):
    def strip_tasks(value):
        if isinstance(value, dict):
            return {key: strip_tasks(item) for key, item in value.items() if key != "tasks"}
        if isinstance(value, list):
            return [strip_tasks(item) for item in value]
        return value
    return strip_tasks({key: value for key, value in state.get("planning", {}).items()
                        if key not in ("status", "plan")})


def task_context(task, state):
    return {"task": task, "architecture_context": architecture_context(state),
            "plan_contracts": {key: value for key, value in state["plan"].items() if key != "tasks"}}
