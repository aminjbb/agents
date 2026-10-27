"""Deterministic test bridge, not an AI/provider adapter. Always reports simulation."""
import json
import sys
from pathlib import Path


def evidence(**fields):
    return {"simulation": True, "summary": "Controlled bridge fixture checked",
            "evidence": ["Fixture protocol and local file assertions"],
            "checks": [{"name": "bridge assertions", "required": True,
                        "status": "PASS", "evidence": "Assertions in deterministic test bridge"}], **fields}


packet = json.load(sys.stdin)
assert packet["definition"]["manifest"]["metadata"]["name"] == packet["agent"]
assert packet["definition"]["instruction"] and packet["definition"]["skills"]
operation = packet["operation"]
root = Path(packet["request"]["project_root"])
if operation == "plan":
    assert packet["agent"] == "@architect" and packet["allowed_write_scope"] == []
    if packet["request"]["text"] == "ask" and not packet["request"]["answers"]:
        response = {"simulation": True, "status": "needs_input",
                    "questions": [{"id": "goal", "question": "What should be created?"}]}
    else:
        response = {"simulation": True, "status": "planned", "plan": {"tasks": [
            {"id": "UI", "owner": "@ui-crafter", "objective": "Write fixture output",
             "deliverable": "Fixture text file", "depends_on": [], "write_scope": ["src/result.txt"],
             "acceptance_criteria": ["File contains the fixture text"]}]}}
elif operation == "execute_task":
    assert packet["request"]["mode"] == "execute"
    assert packet["allowed_write_scope"] == ["src/result.txt"]
    target = root / "src/result.txt"
    target.parent.mkdir(exist_ok=True)
    target.write_text("fixture output", encoding="utf-8")
    response = evidence(status="completed", changed_files=["src/result.txt"])
else:
    assert packet["allowed_write_scope"] == []
    assert (root / "src/result.txt").read_text(encoding="utf-8") == "fixture output"
    response = evidence(verdict="PASS") if operation == "review_delivery" else evidence(status="approved")
print(json.dumps(response))
