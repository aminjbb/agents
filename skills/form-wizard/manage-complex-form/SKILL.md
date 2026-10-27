---
name: manage-complex-form
description: Implement or plan dynamic arrays, conditional fields, multi-step validation, scoped subscriptions, and explicit draft/reset/conflict lifecycles without losing user edits or duplicating state ownership.
---

# Manage Complex Form and Draft Lifecycle

<inputs>

- Target project/form, accepted field schema and state owner, conditional/array/step requirements.
- Initial server/default data source, stable record/account identity, mutation/completion contract, and navigation behavior.
- `mode`: `plan` for audits/design/dry runs; `implement` for authorized changes.

</inputs>

<execution_steps>

## 1. Map the lifecycle and authority

Inspect installed form-library APIs, existing subscriptions, Query/default handling, local/RTK drafts, step routing, and UI field/ref contracts. Record current defects and preserve unrelated changes.

Define exactly one draft owner. RHF is the default owner for a component-scoped complex form. A true cross-screen draft may use an approved RTK model with explicit hydration/commit/discard, not continuous synchronization of two independent stores. Query remains the server snapshot authority.

Document the following before implementation:

| Event | Required decision |
| --- | --- |
| First data arrival | When/how the initial draft and baseline are established |
| Refetch while pristine | Whether to adopt new authoritative defaults |
| Refetch while dirty | Freeze, deliberate merge, or visible conflict policy |
| Record/account switch | Explicit discard/save/preserve policy with identity isolation |
| Save with later edits pending | How the submitted snapshot advances baseline without erasing newer edits |
| Cancel/unmount/navigation | Draft retention/discard and dirty-blocking behavior |
| Restore persisted draft | Version/identity/schema validation and sensitive-field exclusions |

Do not add persistence or conflict UX speculatively. Ask plain-language questions only for material missing product decisions; continue independent safe work while required answers are pending.

## 2. Model conditional fields and steps

- Define active branch validation and whether hidden values are retained, removed, or excluded from the payload.
- Use supported unregister/preserve APIs intentionally. Hidden stale fields must not block unrelated valid branches or leak obsolete values into requests.
- Define step prerequisites, next/back actions, per-step validation, final full-schema validation, and routing to errors on other steps.
- Keep step visibility, browser URL state, and form draft ownership distinct. Coordinate URL-backed steps with @navigator rather than mirroring history locally.
- Preserve semantic form structure: one transaction need not mean nested form elements or a separate controller per step. Define genuine independent subforms explicitly.
- Keep field names, schema paths, UI refs and error mapping consistent across conditions and steps.

In plan mode, return the lifecycle/step contracts and proposed edits before source/package mutations.

## 3. Implement stable field arrays

Use the installed RHF field-array API or the existing supported mechanism. Inspect version-specific generated key naming; do not assume beta/new-major docs match the project.

- Use library-provided stable row identity for React keys and separate domain IDs where applicable. Array index is a position, not persistent identity.
- Define append/remove/reorder defaults, validation, bounds, focus destination, and accessible names for row actions.
- Do not fabricate incomplete defaults or double-register controlled row fields.
- Map delayed errors/results to the submitted row identity and current version, not blindly to an index that may now belong to another row.
- Preserve field values/focus across supported moves. Inspect update APIs that remount fields before choosing them.
- Handle removal of a row with an active request or focused control according to the accepted transaction contract.

## 4. Preserve drafts and avoid unnecessary renders

Initialize/reset only on defined lifecycle events, not every data-object identity change. Keep-dirty flags preserve certain library metadata, not necessarily the intended business merge policy. Use installed reset/baseline APIs and verify actual behavior.

Use narrow subscriptions such as supported watch/form-state APIs at the consuming section. Derive computed values; do not watch the whole form and synchronize calculated copies through effects. Do not memoize or split arbitrarily solely to reduce a render count without a demonstrated issue.

Keep raw/parsed/payload mappings and domain-specific form logic in the owning `model`, UI in `ui`, and server requests in approved `api` contracts. No sibling/upward imports, own-barrel imports, cycles, direct UI transport, or authored inline styles. Source files/components stay within 150 physical lines.

Coordinate field accessibility with @ui-crafter, server/draft state with @state-master, and actual dirty/submitting exit behavior with @navigator. No parallel global dirty flag or implied browser-unload guarantees.

## 5. Verify behavior, not only schema shape

Exercise conditional branch toggles, preserved/excluded values, array add/remove/reorder, validation at each step/final submit, off-step server errors, and stable focus/row identity.

Use controlled refetch and delayed responses to verify dirty-edit preservation, identity isolation, save with newer edits, cancel, step back, and any authorized persistence restore. Test the actual conflict policy instead of assuming reset options implement it.

Use [implement-form-submission](../implement-form-submission/SKILL.md) only when submission changes are required. Use [audit-form](../audit-form/SKILL.md) in audit mode for integration checks and share results with the active caller to avoid recursive fix loops. Run applicable existing type/lint/test/build/import checks; report missing runtime coverage.

</execution_steps>

<output_contract>

Return `IMPLEMENTED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, with draft owner/lifecycle matrix, step/conditional/row identity contracts, changed files/public APIs, actual checks, and remaining gaps. Partial edits with mandatory unverified behavior must not be presented as completed preservation of user input.

</output_contract>
