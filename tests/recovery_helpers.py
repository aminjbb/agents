"""Recovery protocol fixtures; simulations never claim a real provider was called."""
from helpers import evidence


def verified(**fields):
    value = evidence(**fields)
    value["checks"][0]["name"] = "session contract"
    return value


def failure():
    value = verified(status="blocked", summary="Session contract is incompatible")
    value["checks"][0]["status"] = "FAIL"
    value["blocker"] = {"category": "contract", "code": "SESSION_MISMATCH",
                        "reproduce": "Read session.json and assert authenticated is boolean"}
    return value


def repair(**overrides):
    change = {"owner": "@state-master", "write_scope": ["session.json"],
              "objective": "Repair the session contract", "acceptance_criteria": ["Session check passes"],
              "verification": {"reproduce": "Read session.json and assert authenticated is boolean",
                               "checks": ["session contract"]}, **overrides}
    return verified(status="changes_required", rework=change)
