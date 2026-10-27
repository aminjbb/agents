# FAgent control room

A local React interface over the existing architect-first Python coordinator.
No hosted service is needed. Requests use the actual six manifests and their
linked prompts/skills through `Registry`, not a separate set of role prompts.

## Start

Prerequisites: Python 3.11+, a Node version supported by Vite (20.19+ or 22.12+),
npm, and the Codex CLI available as `codex` on PATH. See the official
[App Server documentation](https://learn.chatgpt.com/docs/app-server).

From this repository:

```powershell
cd web
npm ci
npm run build
cd ..
python -m fagent.web
```

Open **http://127.0.0.1:8765**. Connect using an OpenAI API key, or leave the
key blank to use an existing Codex CLI login. The optional model field uses
the account's available model identifier; blank uses Codex's configured default.
Connection checks start the local CLI and inspect authentication presence;
they do not make a paid inference request or validate model entitlement.

Enter the absolute path to the target repository and describe the work in Persian
or English. The architect asks material questions or returns a plan. Answer all
pending questions, then inspect task owners, dependencies and write scopes.
**Execution starts only after the explicit plan approval action.**
Independent tasks run within the coordinator's limits. Each task needs architect
review, integrated delivery needs the auditor's PASS and architect acceptance.

For frontend development, keep the Python server running and, in another terminal:

```powershell
cd web
npm run dev
```

Vite proxies `/api` to port 8765. `python -m fagent.web --port 8765 --runs .fagent/web-runs`
configures the local server and snapshot directory. Changing the backend port
also requires updating the development proxy. The server always binds loopback.

## Connection troubleshooting

After updating Python connection code, stop the running server with Ctrl+C and
start `python -m fagent.web` again. An existing authenticated CLI session can be
used by leaving the API-key input blank.

The resolver checks PATH, the standard Windows standalone install, and installed
VS Code Codex extension binaries. npm's Windows shim is launched through Node
without shell execution. To select a specific installation, set the executable
path in the same terminal before starting the server:

```powershell
$env:FAGENT_CODEX_BIN = 'C:\path\to\codex.exe'
python -m fagent.web
```

For existing login, the bridge honors `CODEX_HOME`; otherwise it explicitly uses
the existing profile `.codex` directory. This fixes native home discovery errors
in some Windows launch environments. An invalid explicit override is reported,
not silently replaced. See [official environment variable documentation](https://learn.chatgpt.com/docs/config-file/environment-variables).
If no login exists, run `codex login` in the terminal and reconnect. Installation,
home and missing-login errors now retain distinct credential-safe messages.
Raw provider output and credentials are never sent to the browser.

Model operations report their failing stage separately from login: thread/turn
creation, model usage or network errors, absent final output, and malformed JSON
are distinct credential-safe diagnostics. Final-message collection retains streamed
text when a completion item is empty; a later empty item cannot erase a valid
answer. A single JSON Markdown fence or a valid JSON object surrounded by short
agent prose is accepted; prose without a protocol object, duplicate JSON keys and
incorrect envelopes are rejected. Architect status labels are normalized at the
protocol boundary, so `PLANNED` and `APPROVED` can be consumed as the planning
state `planned` while unknown statuses remain blocked.

Live troubleshooting on 2026-10-27 verified a short read-only model request and
the saved clothing landing-page planning request with the actual architect packet.
Planning returned `needs_input` with one question; no implementation task ran.
This establishes the planning path, not complete specialist delivery. The initial
generic failure was not reproduced during these checks; categorized errors now
identify the failing stage if it recurs.

Transient model-service failures (`serverOverloaded`, stream disconnects and
upstream 5xx/network errors) are retried up to three times with short exponential
backoff only for read-only operations. Writable operations are never automatically
replayed by the Codex adapter: a failed turn may already have changed files.
Inspect actual side effects before any explicit retry or architect-directed repair.
Rate-limit data is read separately from `account/rateLimits/read`; a
nonzero usage percentage alone is not a limit failure. The UI still reports a
limit reset or unavailable model when the service supplies that specific error.

The Codex decoder uses the operation's envelope field: `verdict` for integrated
auditor reviews and `status` for other operations. It preserves the entire response
and rejects nested Check objects, malformed parents and ambiguous multiple envelopes.

Architect responses are normalized at the coordinator boundary. In addition to
the canonical `{ "plan": { "tasks": [...] } }` envelope, the compatible
`{ "planned": { "metadata": ..., "tasks": [...] } }` envelope emitted by some
Architect instruction versions is accepted and validated through the same task
validator. A missing or non-object plan still blocks the run with a direct error.

## Persistence and credentials

Run snapshots live in ignored `.fagent/web-runs/`, including request text, question
history, task results and verification evidence. Restarting preserves that history.
No run is automatically resumed after restart; reconnect before resuming work.
Interrupted task side effects must be inspected before choosing an explicit retry.

Keys live in backend memory and transient password form state. They never enter
run snapshots, browser storage or command arguments. For API-key sessions, each
Codex child has a disposable `CODEX_HOME`; Codex's temporary authentication file
is deleted when the operation ends. Without a supplied key, existing CLI auth and
configuration are reused. Disconnect is refused during active work, then clears
the backend credential reference. Process termination also discards that reference.

The HTTP API rejects remote Host/Origin headers and mutations without the local
client header. This is a single-user local tool, not a network/multiuser server.

## Architecture and boundaries

`web/` is a React/Vite/TypeScript SPA with strict downward FSD imports and explicit
public APIs. Query owns server snapshots; forms own input drafts; page composition
owns selected session. There is one workspace screen, so no extra router or Redux
store is needed. UI uses native accessible controls and semantic CSS tokens.

`fagent.web_http` serves production assets and API routes. `web_jobs` runs the
existing asynchronous `Orchestrator` on a background loop, persists snapshots,
serializes Windows readers/writers, and prevents duplicate active submissions.
Polling exposes coordinator events and committed task results, not internal
reasoning or token-by-token Codex output. `codex_adapter` starts an ephemeral
Codex thread for each operation and loads its full role packet.

Plan and review operations use read-only sandboxing. Execute operations use
Codex's project workspace sandbox, disable network access and decline interactive
permission escalation. Declared per-task scopes are instructions plus checked
reported paths; they are **not per-file OS isolation**. Use separate checkouts
where stronger separation is needed. Tasks requiring package downloads or
additional permissions may block; there is no silent sandbox bypass.

Execution is genuine when configured. There is no mock fallback or invented
progress. Provider failures and malformed JSON responses block the run. Model
results and test evidence still need review; the coordinator cannot authenticate
an agent's evidence by validating JSON alone. Cancellation on server shutdown
persists interruption where possible and terminates owned Codex children.

## Verify

```powershell
python -m unittest discover -s tests -v
cd web
npm run typecheck
npm run build
```

Protocol tests use explicitly simulated subprocesses and fake adapters. They cover
plan/execute gating, history, persistence, HTTP protection and credential cleanup;
they do not establish a successful paid model call. A real model run needs the
user's authenticated account and access to its selected model.

## Implementation verification (2026-10-27)

The architect used `analyze-feature-request`, `plan-feature-architecture`,
`select-project-dependencies`, and `orchestrate-feature-delivery` to bind the
requested local workflow, API contracts, owners and checks. Implementation was
delegated to the UI and Codex integration specialists with disjoint file scopes;
the auditor performed a separate read-only review using `review-quality-gate`.
The UI interaction contract and remaining manual checks are in
[`web/INTERACTION.md`](../web/INTERACTION.md).

- Full Python suite: 51 tests, 50 passed and one Windows symlink capability skip.
- Production TypeScript/Vite build: passed.
- Independent compiler-based FSD boundary audit: 22 TS/TSX modules, 47 resolved
  application edges, no confirmed boundary violations or cycles. All authored
  application source files satisfy the 150-line policy.
- Real local HTTP checks: production HTML and bootstrap returned 200; bootstrap
  exposed six actual agent manifests and disconnected authentication status.
- Local Codex handshake/auth probe: passed with disposable CLI home, without
  inference. Simulated protocol tests remain explicitly simulated.
- Browser visual, viewport and keyboard checks: unavailable (no enabled browser).
- Paid model execution: not run (no supplied application credential/account).

Code and build checks passed. Full behavioral/visual acceptance remains limited
by the last two items; those are not certified as passed.
