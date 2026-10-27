# Task blocker recovery

The architect diagnoses a stopped task; the coordinator repairs the dependency and resumes the original assignment. A repair is a separate scheduled task, not a replacement objective for the original task.

## Lifecycle

```text
original running -> diagnosing -> waiting_for_repair
repair pending -> running -> read-only architectural verification -> done
original pending -> running with repair result -> normal review -> done
```

Missing material answers produce `needs_input` at request level. Failed repairs, unchanged repeated failures, malformed repair proposals, and exhausted budgets stop with a concrete blocker. Independent tasks continue. Every transition is persisted through events and shown in the control room with links between original and repair tasks.

## Failure report

An execution may return:

```json
{
  "status": "blocked",
  "summary": "Session consumer expects authenticated:boolean",
  "blocker": {
    "category": "contract",
    "code": "SESSION_MISMATCH",
    "reproduce": "Run the existing session contract check against the local fixture"
  },
  "checks": [
    {"name": "session contract", "required": true, "status": "FAIL", "evidence": "Actual failing observation"}
  ],
  "changed_files": []
}
```

Use stable codes and check names. Distinguish implementation/contract issues from tool availability, authentication/access, provider limits, and external dependencies. Report partial writes truthfully. `needs_input` responses retain their questions; the coordinator does not replace those questions with a repair.

The coordinator stores blocker IDs, category/code, the full failure, normalized fingerprint, diagnosis, repair reference, verification and status in the original task's `blockers` history. Fingerprints use category/code and failing required check names/statuses; failures without either use normalized summary text. Changed prose is not reliable proof of progress, so repair count also has an independent cap.

## Architect proposal

Use the existing read-only `review_task` operation. Its ordinary summary/evidence/checks are still required. Add:

```json
{
  "rework": {
    "owner": "@state-master",
    "objective": "Restore the accepted boolean session contract",
    "write_scope": ["src/entities/session/model/", "src/entities/session/index.ts"],
    "acceptance_criteria": ["The original session contract check passes"],
    "verification": {
      "reproduce": "Re-run the existing session contract check using the same local fixture",
      "checks": ["session contract"]
    }
  }
}
```

`verification` is mandatory for a repair; older owner/scope-only rework envelopes are rejected with an actionable error. Include all original failed required check names. Optional `depends_on` contains existing task IDs; by default a repair uses the original task's current prerequisites. Referencing the original task or a consumer would form a cycle and is rejected before graph mutation.

The runtime assigns a collision-free repair ID and adds it to the original task's dependencies. Original owner, objective, scope, deliverable and acceptance remain intact. Keyword-based fallback assignments and mid-execution scope expansion are removed.

Repairs must be executable by the selected agent with available tools and permission. When an external blocker needs a user decision, return concrete `questions` instead. Questions are namespaced and persisted. Do not request secret credentials in chat; use the host's established authentication/configuration flow.

## Scheduling and verification

- Every retry is a new scheduler dispatch with freshly calculated canonical scope locks.
- Repair invalidation waits until active workers have drained; in-flight work is never reset or dispatched twice.
- Completed writers overlapping the repair scope and their dependent consumers lose stale results/approvals. Independent completed work stays intact. Revalidation allowances are capped at `max_attempts` per task/window, so overlapping repairs cannot create an unbounded invalidation loop.
- If a later repair overlaps a previous repair, revalidate the previous repair's original consumer rather than reapplying the old fix over the new one. The previous repair record remains historical evidence; current original acceptance and integrated audit must pass again.
- Execution checks must all pass. Required INCONCLUSIVE checks no longer silently count as implementation success.
- Both the repair result and its read-only architect review must contain all specified verification names as required PASS, supported by actual evidence.
- The reviewer receives `context.recovery_verification`; the repair executor receives the reproduction and original failure in `task.recovery`.
- Only after verification does the original task resume with repair results in `prerequisite_results`. Original acceptance and final auditor gates still apply.

The Python coordinator validates evidence structure and exact named outcomes; it does not itself authenticate test claims or run arbitrary agent-supplied commands. The trusted execution bridge must execute actual checks, and the reviewer must inspect/reproduce them. No model-provider or browser capability is fabricated by these gates.

## Budgets, repeated failure, retry and interruption

Planner tasks are rebuilt from an explicit allowlist before execution: `id`, `owner`, `objective`, `deliverable`, `depends_on`, `write_scope`, `acceptance_criteria`, initial `status`, and descriptive `contracts`, `checks`, `inputs`, `outputs`, `metadata`, `context`, `constraints`, `handoff`, `skills`, `read_scope`, `evidence`. Unknown task fields are discarded; put extensions in `metadata` or `context`. Descriptive context does not grant execution permissions. Top-level plan contracts/metadata are preserved.

Attempt counts, budget allowances, repair links, blocker records, diagnostic flags and errors are created by the coordinator, never copied from a planner task. This boundary also applies when a proposed repair graph is validated; existing runtime state is retained separately from the sanitized validation copy.

`max_attempts` bounds ordinary attempts and the number of automatic repairs per original task in a retry window. Each verified repair grants one additional original-task execution so an attempt-limit boundary cannot prevent resumption. Repair attempts are separately bounded. Same-contract retries return to the scheduler. The legacy `unlimited_attempts` constructor flag no longer disables these limits or delivery review limits.

A repair cannot spawn another repair. The lead may supply `retry_strategy` describing a concrete corrective action within the repair's existing contract and remaining attempt budget. The same unchanged blocker stops automatic recovery even if another strategy is proposed. A newly discovered distinct blocker may receive a separate repair within the original task's repair budget.

An explicit user retry starts a fresh bounded window, retaining prior attempts and blockers. Retrying an original task also resets its incomplete repair prerequisites and dependent consumers; already verified independent work is retained. A plain resume does not reset budgets or replay interrupted workers.

Before resetting a task or starting its next attempt, archive the prior result/review/errors, including `recovery_error`, then clear the current recovery error. Error-only attempts are archived too. Blocker history remains available, and the control room does not present old errors as current failures on completed tasks.

```powershell
python -m fagent resume --state .fagent/runs/product.json --adapter-config D:/tools/adapter.json --retry FORM
```

Cancellation records the active repair as interrupted and its waiting parent as blocked. Inspect side effects before explicit retry. Persisted graphs/repair links are reused after restart; a retry does not create a duplicate repair for an existing incomplete repair prerequisite.

Events include `blocker_detected`, `repair_queued`, `repair_consumers_invalidated`, `repair_verifying`, `task_retry_scheduled`, `task_resuming`, `recovery_blocked`, and `recovery_stuck`.

## Regression checks

```powershell
python -m unittest discover -s tests -v
```

Recovery tests exercise a real temporary contract fixture through a simulated adapter, original/consumer resumption, named verification failures, INCONCLUSIVE rejection, repeated-error termination, scope serialization and revalidation, atomic graph rejection, worker errors, external questions, explicit retry after restart, and cancellation during repair. Simulation remains labeled simulated rather than delivered.
