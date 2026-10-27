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
        "blocked": "summary: concrete blocker; changed_files if partial writes occurred",
    },
    "review_task": {
        "status": "approved | changes_required | blocked",
        "required": "summary, evidence:[text], checks:[{name,required,status,evidence}]",
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
