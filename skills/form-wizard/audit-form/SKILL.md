---
name: audit-form
description: Audit React form ownership, schemas, defaults/drafts, arrays/steps, submission and Action reset behavior, server errors, FSD boundaries, and accessibility using bounded evidence. Read-only by default.
---

# Audit Form

<inputs>

- Target project/form or bounded changed-file scope with relevant consumers.
- Accepted field/payload/default/mutation/interaction contracts and installed package versions.
- `mode`: `audit` by default; `fix` only for authorized corrections.

</inputs>

<execution_steps>

## 1. Establish the actual path

Read applicable instructions, form/schema/controller/UI/API sources, providers, default/refetch handling, error contract, routing/blockers, persistence, public exports, and tests. Preserve unrelated changes.

Record versions and strategy: RHF+Zod, React 19 Actions, or an explicitly justified hybrid. Trace value producers, subscribers, submit triggers, asynchronous callbacks, and reset/navigation paths instead of relying on keyword counts.

Declare scope, data fixtures, browser/assistive-tool coverage, mocked versus actual integrations, and existing failures. Without a browser or dependencies, retain useful static analysis but never claim runtime preservation or schema compilation.

Audit mode does not authorize source auto-fixes, package installation, generators, or external writes. Use controlled responses; never exercise real purchases, deletions, or messages merely to verify a form.

## 2. Check authority and schema contracts

- [ ] One field/draft owner and one submit entry point; no competing RHF/Action/native handlers, double registration, or independent committed copies.
- [ ] Query owns server data; Redux only owns a justified cross-screen client draft. No form-local values globalized for convenience or URL mirrors.
- [ ] Raw input, parsed output, and API payload types are accurate, including transforms and defaults; resolver/schema APIs match installed versions.
- [ ] Missing/empty/numeric/date/file/array and conditional rules reflect accepted requirements; no invented limits or silent coercion bugs.
- [ ] Async validation accounts for stale input and approved remote contracts; no UI fetch effects or unchecked validation bypasses.
- [ ] External defaults/persisted/API errors are runtime-validated and domain invariants reused through legal public APIs.

## 3. Check lifecycle, arrays, and steps

- [ ] Initial loading and first defaults are distinct from subsequent refetches; no unconditional reset on every Query-data change.
- [ ] Dirty edits survive the defined refetch/conflict policy; record/account switches isolate drafts.
- [ ] Save with newer pending edits, cancel/discard, navigation, persistence restore, and sensitive-field handling are explicit.
- [ ] Stable array row identities/keys, add/remove/reorder defaults and focus, and late error mapping cannot target a different row.
- [ ] Conditional hidden values follow preserve/remove/payload policy; step validation, revisiting, final full validation, and off-step errors remain reachable.
- [ ] Scoped subscriptions and cohesive components avoid demonstrated render/complexity problems without arbitrary fragmentation.

## 4. Check submission and errors

- [ ] One validated submit reaches one approved mutation; no raw component/Action transport, fire-and-forget success, or duplicated mutation lifecycle.
- [ ] Pending/duplicate/edit/cancel semantics and consequential-write idempotency boundaries are stated accurately.
- [ ] Expected validation/conflict/permission/network errors and unexpected defects remain distinguishable.
- [ ] Known current field paths receive safe server messages; unknown paths use safe form errors; no blanket FieldPath casts or stale result application.
- [ ] Recoverable failure preserves values; success baseline/reset/navigation belongs to the submitted identity and cannot erase newer edits.
- [ ] Query reconciliation stays at its owner and does not rely solely on callbacks lost on component unmount.
- [ ] React Actions have correct context, previous-result/data types, FormData decoding, and demonstrated uncontrolled-reset/input-preservation behavior when used.
- [ ] Optimism is justified, single-owned, recoverable, and safe for overlapping requests; no double-applied cache/local projection.

## 5. Check UI and architecture

- [ ] Semantic form/buttons, keyboard submission, correct field refs, labels and description/error ID relationships, repeated instances, invalid focus, and meaningful announcements.
- [ ] Disabled/readOnly/submitted-value behavior is deliberate; no nested forms, inaccessible hidden errors, color-only failure, or lost names during pending.
- [ ] Responsive/long-message/supported locale behavior follows the UI contract; no authored inline styles.
- [ ] Correct FSD owners, explicit root public APIs, no upward/sibling/own-barrel imports, no cycles including types, and source/components at most 150 physical lines.

Read [validate-fsd-boundaries](../../validate-fsd-boundaries/SKILL.md) for applicable import/cycle checks and [audit-responsive-accessibility](../../ui-crafter/audit-responsive-accessibility/SKILL.md) when deeper UI auditing is needed. Their checks do not replace form semantics; share evidence instead of recursively re-auditing.

## 6. Exercise and report

For an edit form, exercise initial data → dirty edits → controlled refetch → server field/global failure → correction → successful save → accepted exit. Add relevant arrays/reordering, step back, rapid identity changes, newer edits during pending, and Action reset cases. Adapt to real scope; do not manufacture an edit flow for a simple create form.

Use existing applicable type/lint/tests/build and focused controlled interaction tests. Automated accessibility or pure helper tests alone do not prove full accessibility, backend enforcement, or preserved browser state.

For each finding give stable ID, severity, file/field/state location, actual evidence/reproduction, violated contract, user impact, and concrete correction. Distinguish static hypotheses, confirmed failures, pre-existing debt, and missing coverage.

In fix mode, use [refactor-form](../refactor-form/SKILL.md) for required bounded changes, then rerun affected checks. If invoked by an implementation skill, return findings to that caller rather than launching a recursive fix/scaffold chain.

</execution_steps>

<output_contract>

Return `PASS`, `FAIL`, or `INCOMPLETE` with scope/strategy, separate ownership/validation/lifecycle/submission/accessibility/FSD coverage, findings, actual checks, authorized fixes if any, and remaining work.

PASS requires evidence for all applicable declared checks. FAIL means a confirmed unmet requirement remains, even if other coverage is missing. INCOMPLETE means no confirmed remaining failure but missing required evidence. Use N/A only for true scope exclusions, not absent tools. No audit verdict replaces architectural acceptance or server validation testing.

</output_contract>
