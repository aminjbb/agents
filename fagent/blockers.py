"""Persist reproducible failures and detect repeated blockers without trusting prose progress."""
from copy import deepcopy
import hashlib
import json


def register(task, failure):
    details = failure.get("blocker") or {}
    if not isinstance(details, dict):
        details = {}
    failed = sorted((item["name"], item["status"]) for item in failure.get("checks", [])
                    if item.get("required") and item.get("status") != "PASS")
    category = details.get("category", failure.get("category", task.get("block_reason", "implementation")))
    category = category if isinstance(category, str) and category.strip() else "unknown"
    code = details.get("code") if isinstance(details.get("code"), str) else None
    identity = {"category": category, "code": code, "checks": failed}
    if not failed and not identity["code"]:
        identity["summary"] = " ".join(str(failure.get("summary", "Unknown failure")).casefold().split())
    fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    history = task.setdefault("blockers", [])
    epoch = task.get("recovery_epoch", 0)
    repeated = any(item["fingerprint"] == fingerprint and item.get("epoch", 0) == epoch for item in history)
    blocker = {"id": f'{task["id"]}-blocker-{len(history) + 1}', "fingerprint": fingerprint,
               "epoch": epoch, "category": category, "code": code,
               "summary": failure.get("summary", "Unknown failure"), "failure": deepcopy(failure),
               "reproduce": details.get("reproduce"), "status": "diagnosing", "repeated": repeated}
    history.append(blocker)
    return blocker
