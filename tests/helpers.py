import asyncio
from copy import deepcopy


def task(task_id="T1", owner="@ui-crafter", deps=None, scopes=None):
    return {"id": task_id, "owner": owner, "objective": "Implement a bounded UI change",
            "deliverable": "Changed UI and verification", "depends_on": deps or [],
            "write_scope": scopes or [], "acceptance_criteria": ["Expected behavior is verified"]}


def evidence(**fields):
    return {"summary": "Verified fixture outcome", "evidence": ["Controlled test fixture"],
            "checks": [{"name": "fixture check", "required": True,
                        "status": "PASS", "evidence": "Asserted by the test bridge"}], **fields}


class ScriptedAdapter:
    simulation = True

    def __init__(self, tasks=None, handler=None):
        self.tasks = tasks or [task()]
        self.handler = handler
        self.calls = []

    async def invoke(self, packet):
        self.calls.append(deepcopy(packet))
        if self.handler:
            response = await self.handler(packet)
            if response is not None:
                return response
        operation = packet["operation"]
        if operation == "plan":
            return {"status": "planned", "plan": {"tasks": deepcopy(self.tasks)}}
        if operation == "execute_task":
            await asyncio.sleep(0)
            return evidence(status="completed", changed_files=[])
        if operation == "review_delivery":
            return evidence(verdict="PASS")
        return evidence(status="approved")
