---
name: implement-form-submission
description: Wire one validated RHF or React 19 Action submit transaction to the approved Query mutation, including safe FormData/error mapping, input preservation, reconciliation, and deliberate success/reset/navigation behavior.
---

# Implement Form Submission

<inputs>

- Target project/form owner, raw/parsed/payload schema, chosen RHF or Action strategy.
- Existing approved mutation command and validated success/error contract, draft identity/revision behavior, and completion/reset/navigation policy.
- `mode`: `plan` for audits/design/dry runs; `implement` for authorized changes.

Missing API/idempotency/business contracts are named dependencies, not permission to invent endpoints or simulate saved data.

</inputs>

<execution_steps>

## 1. Define one transaction

Inspect installed versions, current submit wiring, payload mapper, mutation/Query owner, server issue shape, UI refs, draft state, and tests. Trace native submit, button callbacks, effects, Actions, and listeners to find duplicate request paths.

Define validation → parsed input → API payload → one approved mutation → authoritative reconciliation → completion. Distinguish validation rejection, conflicts, permission/session errors, transport failure, and unexpected defects.

Agree how duplicate submissions, edits during pending, navigation/cancellation, record/account changes, and late responses are handled. UI disabling alone is not backend idempotency. Define submitted identity/revision so late success cannot clear a newer draft or redirect an unrelated page.

Query v5 remains the owner of server writes/cache in `api`. Controllers in `model` may compose its hook and expose an async command. No raw transport in UI/Actions, hooks inside async action functions, second server cache, or manual mirrored request flags.

## 2. Implement the selected entry point

### RHF

Use the compatible Zod resolver and raw/output typing. Bind `handleSubmit` once and return/await the mutation command through reconciliation required by the form contract. Map known failures explicitly and preserve current values; never reset in `finally` or report success after fire-and-forget mutation.

Use actual supported `setError`/focus mechanisms for known registered paths. Keep form transaction pending distinct from the mutation's transport/cache lifecycle without maintaining a competing boolean state machine.

### React 19 Action

Use `useActionState` only in a supported Action context with correctly typed previous result and submitted data. A bound controller may supply the approved mutation command; the Action must not replace it with direct fetch or call hooks internally.

Decode FormData by the schema's actual field semantics. Missing, repeated, file, unchecked, and disabled values require deliberate handling. Example decoder for one required text occurrence:

```ts
export type SingleTextResult =
  | { ok: true; value: string }
  | { ok: false; reason: "missing" | "multiple" | "not-text" };

export function readSingleText(
  data: FormData,
  name: string,
): SingleTextResult {
  const values = data.getAll(name);
  if (values.length === 0) return { ok: false, reason: "missing" };
  if (values.length !== 1) return { ok: false, reason: "multiple" };
  const value = values[0];
  if (typeof value !== "string") return { ok: false, reason: "not-text" };
  return { ok: true, value };
}
```

Then validate decoded values with the approved schema; repeated lists use `getAll` and a different explicit contract. Never use a blind object conversion or unchecked cast to collapse files/repeated fields. Decode submit intent when multiple submit buttons have different accepted actions.

A resolving function-form Action can reset uncontrolled inputs even when its returned result represents validation failure. Choose explicit controlled field ownership or a verified restoration strategy before implementation. Do not assume returning error data prevents reset or throw expected validation failures just to alter it. Action result state does not become a duplicate authoritative field store.

Keep expected issues as typed results and unexpected defects distinguishable through supported error handling. This SPA has no implicit Server Functions or no-JavaScript submission guarantee.

## 3. Map server issues safely

Normalize and runtime-validate external error payloads in the owning API layer. Apply only known, current registered field paths; unknown/private backend paths must not be blindly cast into form keys.

This pure helper illustrates allowlist mapping after API normalization. It keeps the first issue for a known field and substitutes a safe form message for unknown fields:

```ts
export type ServerIssue = Readonly<{ field: string; message: string }>;

export function mapServerIssues<Field extends string>(
  knownFields: readonly Field[],
  issues: readonly ServerIssue[],
  fallback: string,
): { fieldErrors: Map<Field, string>; formErrors: string[] } {
  const fieldErrors = new Map<Field, string>();
  const formErrors: string[] = [];
  for (const issue of issues) {
    const field = knownFields.find((candidate) => candidate === issue.field);
    if (field === undefined) {
      if (!formErrors.includes(fallback)) formErrors.push(fallback);
    } else if (!fieldErrors.has(field)) {
      fieldErrors.set(field, issue.message);
    }
  }
  return { fieldErrors, formErrors };
}
```

Known messages must already be safe user-facing messages from the API contract, not stacks/internal details. This helper does not validate unknown JSON, translate array indices, or prove a response belongs to the current draft. Build those checks from submitted identities/revisions before applying errors.

## 4. Complete without losing input

Preserve recoverable failed submissions and relevant dirty edits. Clear stale server errors only by the accepted field/version policy. Define focus/summary and how off-step errors become reachable.

On success, reconcile server state at the API/mutation owner, then advance baseline/reset only for the matching submitted identity and accepted edit policy. Use supported installed-library APIs; do not erase edits made while the request was pending.

Coordinate accepted post-submit navigation with @navigator and presentation with @ui-crafter. Use a single optimistic owner when explicitly justified; account for rollback, overlapping submissions, and authoritative base updates. Do not optimistically apply the same item/count in both Query and `useOptimistic`.

In plan mode, return entry point, typed error/result/identity contract, and lifecycle before source mutation. No real external write is authorized merely by testing a form.

## 5. Verify and report

Use controlled mutation outcomes and isolated form/Query/router fixtures. Verify invalid input sends no write, valid input sends one, expected field/global failures preserve values, unexpected defects stay distinguishable, duplicate submits follow policy, and late results do not reset newer drafts.

Test relevant FormData semantics, safe field mapping, pending context, React Action reset/input preservation, cache reconciliation on unmount, success baseline and navigation, and optimism if used. Pure helper tests alone do not prove React/browser or backend behavior.

Use [audit-form](../audit-form/SKILL.md) in audit mode with shared evidence. Run existing applicable type/lint/tests/build/boundary checks; maintain public APIs, acyclic downward imports, no inline styles, and 150-line source/component limits.

</execution_steps>

<output_contract>

Return `IMPLEMENTED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, with strategy, transaction/data/error/identity contracts, files, actual checks/results, and remaining gaps. Implemented adapters without mandatory runtime verification remain explicitly partial; no status proves backend authorization or idempotency.

</output_contract>
