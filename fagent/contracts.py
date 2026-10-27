"""Transport envelopes; role-report Markdown/XML may live inside summary/evidence."""
RESPONSE_CONTRACTS = {
    "plan": {
        "status": "planned | needs_input | blocked",
        "planned": "plan.tasks contains id, owner, objective, deliverable, depends_on, "
                   "write_scope, acceptance_criteria; every initial status is pending. "
                   "Include shared accepted contracts/brief/decisions in plan metadata or response context.",
        "needs_input": "questions: nonempty [{id, question, optional options:[text]}]",
        "blocked": "summary: concrete missing dependency",
    },
    "execute_task": {
        "status": "completed | needs_input | blocked",
        "completed": "summary, evidence:[text], changed_files:[project-relative paths], "
                     "checks:[{name,required:boolean,status,evidence}]",
        "needs_input": "summary and questions:[{id,question,optional options}]",
        "blocked": "summary: concrete blocker; changed_files if partial writes occurred. "
                   "Include blocker:{category,code,reproduce} and checks with stable names when known. "
                   "Distinguish implementation/contract from tool/access/provider/external blockers.",
    },
    "review_task": {
        "status": "approved | changes_required | blocked",
        "required": "summary, evidence:[text], checks:[{name,required,status,evidence}]",
        "rework": "Optional separate repair: {owner,write_scope,objective,acceptance_criteria,"
                  "verification:{reproduce,checks:[exact required check names]},optional depends_on:[existing IDs]}. "
                  "Diagnose the actual cause/capability, not keywords. Never replace the original objective. "
                  "Include all original failing check names. The coordinator schedules and locks the repair. "
                  "No recursive repair of repairs or repeated unchanged failure; report the real blocker instead.",
        "verification": "When context.recovery_verification is present, independently inspect/reproduce "
                        "the blocker read-only; confirm every specified check by exact name as required PASS "
                        "only with actual host/tool evidence. Missing tools or INCONCLUSIVE cannot pass.",
        "questions": "Optional [{id,question,optional options}] for essential external/user decisions; "
                     "never silently replace pending questions with a repair.",
        "retry_strategy": "Optional nonempty concrete different corrective action within this task's "
                          "existing owner/scope/acceptance. No blind retry. Repair tasks may use this "
                          "within their attempt budget; they cannot create nested repairs. "
                          "An unchanged repeated blocker stops automatic retries.",
        "changed_files": "Must be absent or empty; review is read-only",
    },
    "review_delivery": {
        "verdict": "PASS | FAIL | INCOMPLETE",
        "required": "summary, evidence:[text], checks:[{name,required,status,evidence}]",
        "changed_files": "Must be absent or empty; independent quality review is read-only",
    },
    "accept_delivery": {
        "status": "approved | changes_required | blocked",
        "required": "summary, evidence:[text], checks:[{name,required,status,evidence}]",
        "retry_tasks": "Optional existing task IDs for bounded rework, never new task definitions",
        "changed_files": "Must be absent or empty; acceptance is read-only",
    },
}
