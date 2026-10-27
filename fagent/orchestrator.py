"""Architect-first, resumable request lifecycle with independent ready work."""
import asyncio
from pathlib import Path

from .delivery import finalize
from .gateway import Gateway
from .plans import architect_plan, normalize_architect_response, prepare, reset_tasks
from .protocol import questions, request, require, text
from .registry import Registry
from .scheduler import execute
from .store import Store


class Orchestrator:
    def __init__(self, adapter, store, registry=None, unlimited_attempts=False):
        self.adapter, self.store = adapter, store
        self.registry = registry or Registry()
        self.unlimited_attempts = unlimited_attempts

    def bind(self, state):
        self.state = state
        self.gateway = Gateway(self.adapter, self.registry, state, self.store.save)
        state["simulation"] = state.get("simulation", False) or self.adapter.simulation
        state["unlimited_attempts"] = False  # Retained field; all automatic retries are bounded.

    async def start(self, data):
        state = {"protocol_version": "1.0", "request": request(data), "status": "intake",
                 "plan": None, "questions": [], "events": [], "simulation": False}
        self.store.create(state)
        self.bind(state)
        return await self.drive()

    async def resume(self, answers=None, retry_tasks=None, authorize_execute=False):
        self.bind(self.store.read())
        state = self.state
        require(state.get("protocol_version") == "1.0", "Unsupported saved-state protocol")
        validated = request(state["request"])
        require(validated["project_root"] == state["request"]["project_root"], "Project root changed")
        require(state["status"] not in ("delivered", "simulated"), "Completed runs are immutable")
        if answers is not None:
            require(isinstance(answers, dict), "Answers must be an object")
            required = {item["id"] for item in state["questions"]}
            require(required and required == answers.keys(), "Answer exactly the pending question IDs")
            for value in answers.values():
                text(value, "answer")
            state["request"]["answers"].update(answers)
            state["request"].setdefault("clarifications", []).append(
                {"questions": state["questions"], "answers": answers})
            if state["plan"]:
                waiting = [task["id"] for task in state["plan"]["tasks"] if task.get("questions")]
                if waiting:
                    reset_tasks(state, waiting, fresh_attempt_window=True)
            state["questions"] = []
        elif state["questions"]:
            return state
        if retry_tasks:
            require(state["plan"] is not None, "No task plan to retry")
            reset_tasks(state, retry_tasks, fresh_attempt_window=True)
        if authorize_execute:
            state["request"]["mode"] = "execute"
            if state["plan"]:
                state["plan"]["mode"] = "execute"
        self.gateway.event("request_resumed")
        return await self.drive()

    async def drive(self):
        state, gateway = self.state, self.gateway
        state.pop("error", None)
        try:
            if state["plan"] is None:
                state["status"] = "intake"
                result = normalize_architect_response(
                    await gateway.invoke("@architect", "plan", {"questions": state["questions"]}))
                if result.get("status") == "needs_input":
                    state.update(status="needs_input", questions=questions(result.get("questions")))
                    gateway.event("input_required")
                    return state
                if result.get("status") == "blocked":
                    state.update(status="blocked", error=text(result.get("summary"), "summary"))
                    gateway.event("intake_blocked")
                    return state
                require(result.get("status") == "planned", "Invalid architect planning status")
                state["planning"] = result
                state["plan"], state["plan_validation"] = prepare(architect_plan(result), state["request"])
                for task in state["plan"]["tasks"]:
                    require(task["owner"] in self.registry.agents, "Planned agent unavailable")
                gateway.event("plan_validated")
            if state["request"]["mode"] == "plan":
                state["status"] = "planned"
                gateway.event("planning_finished")
                return state
            root = Path(state["request"]["project_root"])
            lock = (root / ".fagent" / "workspace").resolve()
            require(lock.is_relative_to(root), "Workspace lease escapes project root")
            with Store(lock):
                await self.execute_plan()
        except asyncio.CancelledError:
            state.update(status="blocked", error="Interrupted; inspect side effects before explicit retry")
            gateway.event("request_interrupted")
            raise
        except Exception as error:
            state.update(status="blocked", error=str(error))
            gateway.event("request_error", reason=str(error))
        return state

    async def execute_plan(self):
        state, gateway = self.state, self.gateway
        # Legacy constructor flag must never bypass recovery/delivery budgets.
        rounds = state["request"]["max_attempts"] + 1
        round_number = 0
        while round_number < rounds:
            round_number += 1
            state["status"] = "executing"
            gateway.event("execution_started")
            await execute(state, gateway)
            tasks = state["plan"]["tasks"]
            state["questions"] = [item for task in tasks for item in task.get("questions", [])]
            if not all(task["status"] == "done" for task in tasks):
                state["status"] = "needs_input" if state["questions"] else "blocked"
                gateway.event("execution_incomplete", status=state["status"])
                return
            state["status"] = "reviewing"
            gateway.event("delivery_review_started")
            if not await finalize(state, gateway):
                return
        state.update(status="changes_required", error="Delivery review round limit reached")
        gateway.event("delivery_round_limit")
