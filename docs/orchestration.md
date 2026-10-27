# Frontend orchestration runtime

FAgent now has an executable Python coordinator using only the standard library (Python 3.11+). Every request submitted through this runtime starts with `@architect`, including text that explicitly mentions another agent. The architect plans/questions first; specialists receive only planned tasks. Direct IDE chats outside this entry point are not intercepted.

The command-adapter CLI includes a real subprocess adapter for a trusted host command implementing the JSON protocol below. The [local React control room](control-room.md) additionally supplies a Codex App Server bridge. Each bridge supplies model/tool access and owns filesystem, network, approval, and process-lifecycle restrictions. No missing bridge silently falls back to simulation.

## Start with a concrete host bridge

Create an adapter configuration pointing to an actual bridge executable/script, using argument arrays rather than a shell command:

```json
{
  "command": ["C:/Python313/python.exe", "D:/tools/my_agent_bridge.py"],
  "timeout_seconds": 300,
  "simulation": false
}
```

These example paths are placeholders for your host integration, not files supplied by this repository. Commands run without shell expansion, with the target project as cwd. Use absolute script paths and keep credentials in the host's established configuration, not committed adapter JSON. Timeout defaults to 300 seconds; stdout and stderr each have a 1 MiB limit. Stderr is not copied into run evidence; the bridge should retain its own appropriate diagnostics.

From this repository, plan first:

```powershell
python -m fagent start --project-root D:/project/my-app --text "Build the requested product form" --adapter-config D:/tools/adapter.json --state .fagent/runs/product.json
```

The default mode is `plan`. After architect intake/clarification and structural validation, the run stops at `planned` without dispatching implementation tasks. A plan is not an execution grant.

For an already-authorized implementation request, add `--mode execute`; concurrency defaults to 3 and is configurable with `--max-parallel` (1..16). `--max-attempts` (1..5, default 2) bounds code/review rework per task in both CLI and web control room. After the cap, the failure is surfaced to Tech Lead for an explicit rework assignment instead of looping indefinitely. A user-triggered retry starts a fresh bounded window while retaining prior attempts in task history, so an exhausted run remains recoverable. The runtime does not estimate tokens or billable cost; the host bridge owns provider limits.

Explicitly execute an existing planned run:

```powershell
python -m fagent resume --state .fagent/runs/product.json --adapter-config D:/tools/adapter.json --execute
python -m fagent status --state .fagent/runs/product.json
```

Use `status --full` to inspect the plan, task results/reviews, check evidence, audit/acceptance, and ordered timestamped events. Run files contain the request, answers, and agent-reported evidence; store them appropriately. Default CLI summaries do not print complete prompts or adapter arguments.

When execution or review fails, the coordinator sends the evidence to `@architect`.
A bounded `rework` proposal now creates a separate repair task with exact scope,
reproduction and named verification checks. It preserves the original assignment,
reacquires scheduler locks and resumes the original specialist only after the
repair passes execution and read-only review. See the [recovery contract](recovery.md)
for budgets, repeated-failure detection, external blockers and response examples.

## Clarification and resuming

An architect can return `needs_input` before planning. A specialist can also ask a material question while independent tasks continue. The runtime saves questions and stops with `needs_input`; it never treats silence as an answer.

Provide a JSON object keyed by exactly the pending question IDs:

```json
{
  "destination": "Stay on the page and show confirmation"
}
```

```powershell
python -m fagent resume --state .fagent/runs/product.json --adapter-config D:/tools/adapter.json --answers D:/tools/answers.json
```

Task question IDs are namespaced, for example `UI.destination`. Replies and question text remain in clarification history sent to the host. Clarification-only task responses that report no changes do not consume the code retry budget. Answers alone do not elevate a planned request to execute mode.

To explicitly retry a blocked/interrupted task after inspecting its side effects and resolving its dependency:

```powershell
python -m fagent resume --state .fagent/runs/product.json --adapter-config D:/tools/adapter.json --retry API
```

The selected task, its incomplete repair prerequisites and dependent consumers lose active results/approvals and return to pending in a fresh bounded retry window. Prior attempts/reviews remain in task history, previous blockers remain in blocker history, and integrated review remains in delivery_history. Independent completed work is retained. Architectural scope changes still require architect planning; the runtime only adds validated repair dependencies through its recovery contract.

## Scheduling and review

- New plans must contain only pending tasks; the planner cannot forge already-completed prerequisites.
- Ready tasks have actual architect-approved dependencies, not merely existing task IDs.
- Independent tasks execute concurrently up to the configured capacity. Each task has one owner.
- Canonical case-insensitive scope comparisons serialize overlapping file/directory writers, including aliases that resolve to the same actual path. Strict standalone plan validation still rejects unordered conflicts by default; runtime validation explicitly opts into scheduling them serially.
- Locks cover a task's execution and architect review. Read-only review calls receive an empty allowed write scope.
- A failed/blocked branch blocks its consumers; independent branches continue.
- Each completed task must report changed files, nonempty evidence and named checks with at least one required check. Required checks must pass before completion can be approved.
- Task changes requested by architect are retried within the attempt budget. There is no blind retry of arbitrary failed external operations.
- After all tasks are done, `@auditor` reviews the integrated result; `@architect` then accepts it. Auditor FAIL/INCOMPLETE or nonpassing required checks cannot be overridden by an architect approval string.
- Architect acceptance may identify existing `retry_tasks`; selected tasks and descendants are invalidated for bounded rework, including when the audit is INCOMPLETE. An explicit architect `blocked` response prevents automatic rework. Scheduling evidence work is not acceptance: fresh auditor PASS and passing architectural acceptance remain mandatory, and automatic retries do not reset task budgets.

Task states are `pending`, `ready`, `running`, `diagnosing`, `waiting_for_repair`, `review`, `done`, `blocked`, and `changes_required`. Request states are `intake`, `needs_input`, `planned`, `executing`, `reviewing`, `delivered`, `blocked`, `changes_required`, and `simulated`.

An adapter declaring simulation, or any response declaring simulation, permanently marks that run as simulated. Successful simulated execution ends at `simulated`, never `delivered`. Real mode still relies on the bridge's truthful evidence and tool enforcement; JSON validation alone cannot verify a claimed test result.

## JSON-over-stdio bridge protocol

For each operation the command receives exactly one UTF-8 JSON packet on stdin and must print exactly one JSON object on stdout. Logs belong on stderr or in host-managed diagnostics. Duplicate JSON keys, malformed envelopes, nonzero process exits, output overflow, and timeouts fail the operation. The runtime kills the immediate bridge process on timeout/cancellation; the host must also clean up its own descendants/tools before returning or exiting.

Packet fields:

| Field | Meaning |
| --- | --- |
| `protocol_version` | `1.0` |
| `agent`, `operation` | Selected role and bounded operation |
| `request` | Original text, canonical project root, plan/execute mode, limits, answers/history |
| `allowed_write_scope` | Project-relative file paths or directory prefixes ending in `/`; empty means read-only. Architect's finite `vite.config.*` and `tsconfig*.json` families are expanded to explicit config filenames before execution. |
| `definition` | Actual manifest, instruction, skill definitions, and package root |
| `context` | Task/prerequisite results, shared architect brief/decisions, plan contracts, review or audit inputs as applicable |
| `response_contract` | Operation-specific transport envelope requirements |

The bridge loads the supplied role instruction and required skill context in its host, passes the bounded task, applies the host's tool restrictions, and returns the structured envelope. Existing role XML/Markdown reports can be included in summary/evidence; the transport itself must remain JSON.

Operations and responses:

| Operation / agent | Response |
| --- | --- |
| `plan` / architect | `status: planned` with `plan.tasks`, or `needs_input` with questions, or `blocked` with summary |
| `execute_task` / planned owner | `status: completed` with summary/evidence/checks/changed_files, or `needs_input` with summary/questions, or `blocked` with summary and any partial changed_files |
| `review_task` / architect | `status: approved`, `changes_required`, or `blocked`, with summary/evidence/checks; no changes |
| `review_delivery` / auditor | `verdict: PASS`, `FAIL`, or `INCOMPLETE`, with summary/evidence/checks; no changes |
| `accept_delivery` / architect | `status: approved`, `changes_required`, or `blocked`, with summary/evidence/checks and optional existing retry_tasks; no changes |

Minimal task in a planning response:

The architect may include the accepted brief/decisions beside `plan` and shared contracts within plan metadata. They are persisted and supplied to workers as architecture_context/plan_contracts alongside their bounded task; do not rely on an implicit conversation shared between independent host processes.

```json
{
  "status": "planned",
  "plan": {
    "tasks": [
      {
        "id": "UI",
        "owner": "@ui-crafter",
        "objective": "Implement the approved bounded view",
        "deliverable": "View and relevant verification",
        "depends_on": [],
        "write_scope": ["src/features/product/ui/"],
        "acceptance_criteria": ["The accepted interaction behaves correctly"]
      }
    ]
  }
}
```

Minimal completed response shape; replace the example evidence with real observations:

```json
{
  "status": "completed",
  "summary": "Describe the actual outcome",
  "changed_files": ["src/features/product/ui/ProductForm.tsx"],
  "evidence": ["Actual inspection or artifact reference"],
  "checks": [
    {"name": "relevant behavior", "required": true, "status": "PASS", "evidence": "Actual method and result"}
  ]
}
```

Checks accept `PASS`, `FAIL`, `NOT_RUN`, `INCONCLUSIVE`, and a justified optional `N/A`; required checks cannot be N/A. Returned evidence must be nonempty but is not independently authenticated by the coordinator. The host must execute real tools and reviewers must inspect the actual scope. A blocker or question is preferable to fabricated success.

## Isolation, persistence, and recovery boundaries

Run snapshots are atomically replaced, and a state-file lock prevents two processes from driving the same run. Execute mode additionally holds `<project>/.fagent/workspace.lock`, allowing only one active execution run per project. Planning does not create that project lease. Parallelism exists within that run; cross-request parallel execution on one project is deliberately serialized.

The runtime rechecks resolved declared scopes and rejects paths escaping the target and protected `.git`, `.agents`, `.codex`, and `.fagent` paths. It checks reported changed_files against those declarations. These checks and locks are coordination controls, not an OS filesystem sandbox: a trusted-but-buggy or malicious bridge could write unreported files or external systems. Use host sandboxing or isolated checkouts for actual enforcement; automatic rollback and cross-worktree merging are not implemented.

If a process crashes, a lock may remain. Inspect the recorded PID/process and actual side effects before manually removing a stale lock. Resume does not replay running tasks automatically; use explicit retry after inspection. Cancellation persists interrupted tasks as blocked when cleanup can run. Interrupted subprocess descendants require host cleanup; do not remove locks while they still operate.

The coordinator uses an architect-planned graph with validated repair dependencies and bounded retries. The separate [control room](control-room.md) provides visual intake, task/repair tracking and a Codex adapter. Distributed scheduling, automatic conflict resolution, release/merge automation and interception of arbitrary IDE messages remain outside this runtime.

## Verification

```powershell
python -m unittest discover -s tests -v
```

Tests include true asyncio overlap, serialized writers, approved prerequisite ordering, independent progress after failure, clarification/resume, retry invalidation, auditor vetoes, actual command subprocesses/timeouts/cancellation, atomic locks, and full CLI plan/execute round trips through the explicitly simulated test bridge. Symlink creation tests skip where the Windows session lacks that capability. No model-provider or real IDE-agent integration is claimed by these tests.

CLI exit codes: `0` planned/delivered/simulated or successful status inspection; `1` configuration/protocol entry error; `2` needs input; `3` blocked/changes required; `130` interrupted. Full state always distinguishes simulation and actual review outcomes.
