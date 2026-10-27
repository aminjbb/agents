"""Deterministic evidence gates; returned evidence is still a trusted-host assertion."""
from .protocol import evidence, require


def grade(response, allow_inconclusive=False):
    if evidence(response):
        return "PASS"
    return "FAIL" if any(item["required"] and item["status"] == "FAIL"
                         for item in response["checks"]) else (
                             "PASS" if allow_inconclusive and all(
                                 not item["required"] or item["status"] in ("PASS", "INCONCLUSIVE")
                                 for item in response["checks"]) else "INCOMPLETE")


def review(response):
    status = response.get("status")
    require(status in ("approved", "changes_required", "blocked"), "Invalid architect review status")
    quality = grade(response)
    if quality != "PASS":
        return "changes_required" if quality == "FAIL" else "blocked"
    return "done" if status == "approved" else status


def audit(response):
    verdict = response.get("verdict")
    require(verdict in ("PASS", "FAIL", "INCOMPLETE"), "Invalid auditor verdict")
    quality = grade(response)
    if "FAIL" in (quality, verdict):
        return "FAIL"
    return "INCOMPLETE" if "INCOMPLETE" in (quality, verdict) else "PASS"
