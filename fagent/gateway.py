"""Deliver actual definitions and bounded operation context to an execution adapter."""
import asyncio
from datetime import datetime, timezone

from .contracts import RESPONSE_CONTRACTS
from .paths import changed_files, scope_keys
from .protocol import normalize_agent_response, require


class Gateway:
    def __init__(self, adapter, registry, state, save):
        require(type(getattr(adapter, "simulation", None)) is bool,
                "Adapter must explicitly declare simulation: boolean")
        self.adapter, self.registry, self.state, self.save = adapter, registry, state, save
        self.architect_lock = asyncio.Lock()

    def event(self, name, **fields):
        self.state["events"].append({"sequence": len(self.state["events"]) + 1,
                                    "at": datetime.now(timezone.utc).isoformat(),
                                    "event": name, **fields})
        self.save(self.state)

    async def invoke(self, owner, operation, context, write_scope=None):
        if owner == "@architect":
            async with self.architect_lock:
                return await self._invoke(owner, operation, context, write_scope or [])
        return await self._invoke(owner, operation, context, write_scope or [])

    async def _invoke(self, owner, operation, context, write_scope):
        req = self.state["request"]
        require(not write_scope or req["mode"] == "execute", "Planning cannot authorize writes")
        scope_keys(req["project_root"], write_scope)
        packet = {"protocol_version": "1.0", "agent": owner, "operation": operation,
                  "request": req, "allowed_write_scope": write_scope,
                  "response_contract": RESPONSE_CONTRACTS[operation],
                  "transport_rule": "Return exactly one JSON object matching response_contract. "
                                    "Role XML/Markdown belongs inside summary/evidence. "
                                    "No source/config/external mutation outside this operation scope.",
                  "definition": self.registry.packet(owner), "context": context}
        self.event("agent_started", agent=owner, operation=operation,
                   task_id=context.get("task", {}).get("id"))
        try:
            response = normalize_agent_response(await self.adapter.invoke(packet))
            require(isinstance(response, dict), "Adapter response must be an object")
            require(type(response.get("simulation", False)) is bool, "Invalid simulation response flag")
            if response.get("simulation"):
                self.state["simulation"] = True
            changed_files(req["project_root"], write_scope, response.get("changed_files", []))
            return response
        finally:
            # Invocation lifecycle must stay balanced on failure, cancellation and retry.
            self.event("agent_finished", agent=owner, operation=operation)
