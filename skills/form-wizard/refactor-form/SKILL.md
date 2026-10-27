---
name: refactor-form
description: Refactor duplicated, oversized, effect-synchronized, or unreliable React forms into explicit schema, controller, mutation, and UI ownership while preserving edits, focus, contracts, and product behavior.
---

# Refactor Form

<inputs>

- Target project, bounded form/files, demonstrated defects, and expected behavior.
- Existing field/schema/default/submission/draft contracts, consumers, and available tests/findings.
- `mode`: `analyze` for reviews/design/dry runs; `refactor` for authorized implementation.

</inputs>

<execution_steps>

## 1. Preserve the baseline

Read instructions and inspect installed versions, consumers, public exports, form controllers, field refs/events, schemas, Query/Redux state, server errors, reset effects, persistence, and routes. Protect unrelated/uncommitted changes.

Record current accepted behavior and actual defects: duplicate state/submits, lost edits, excessive mixed responsibilities, unsafe coercions/path casts, inaccessible errors, stale responses, and forbidden dependencies. Count hooks/lines only as discovery signals; justify each extraction by responsibility.

Capture useful runtime evidence if available, without real external writes or logging sensitive values. Missing tooling is a stated limit, not proof that behavior is preserved.

## 2. Plan ownership and migration

Define one raw-value owner, parsed schema output, API payload, default/baseline lifecycle, mutation command/error contract, and completion behavior. Separate server snapshots from editable transactions and genuine global client drafts.

Keep schema/controller/mapping in the owning model, rendering in ui, network/mutations in api, and reusable primitives/invariants at legal lower owners. Preserve root public APIs or coordinate necessary changes with @architect. No app-store/router imports or sibling/type cycles.

Prefer existing compatible RHF+Zod for complex forms. React Actions require a real supported-version/task benefit, not a trend-driven rewrite. If replacing a controller strategy, update consumers in one integrated transition so old/new submit paths are never active together.

In analyze mode, return findings, proposed ownership/extractions, migration order, and verification without source/package changes.

## 3. Execute bounded corrections

1. Use [scaffold-validated-form](../scaffold-validated-form/SKILL.md) only for necessary new/adapted contracts, not regeneration over existing implementation.
2. Extract pure schemas and explicit value/payload mappers; reuse domain invariants. Correct input/output typing without unsafe casts or broadening to any.
3. Use [manage-complex-form](../manage-complex-form/SKILL.md) for dirty/default/refetch, array/conditional/step, and subscription problems. Remove uncontrolled synchronization/reset effects only after establishing replacement lifecycle semantics.
4. Use [implement-form-submission](../implement-form-submission/SKILL.md) for one awaited mutation path, typed errors, safe FormData handling, input-preserving failures, and revision-aware completion.
5. Remove redundant booleans, mirrors, requests, validators, stale forwarding layers, and dead exports after checking all consumers. Do not remove legitimate draft buffers or external-system effects without understanding their contract.
6. Preserve native/controlled field contracts, focus/selection, refs, names/IDs, button semantics, stable array keys, and the accepted interaction. Extract component types at module scope to avoid accidental remount/reset.
7. Keep consequential dirty/exit decisions with the product contract and @navigator; field presentation with @ui-crafter and data/cache authority with @state-master. Do not invent parallel services or assume collaborator execution.

Keep source files/components within 150 physical lines through cohesive extraction, not minification or arbitrary wrappers. No authored inline-style bypasses, wildcard/layer barrels, illegal dependencies, or cycles.

## 4. Verify behavioral preservation

Exercise affected validation branches, default arrival/refetch, dirty edits, array moves/step revisits, failure/retry, submit count, late errors/results, successful baseline updates, and exit behavior. Include React Action reset/pending behavior if that path is used.

Use isolated form/Query/router fixtures, controlled requests, and existing applicable type/lint/tests/build/boundary checks. Add focused tests for meaningful regressions; do not introduce a new test stack or claim coverage from copied schema snapshots.

Use [audit-form](../audit-form/SKILL.md) in audit mode after changes. When called from an audit, return evidence/findings to the active caller rather than recursively requesting fixes. Reuse current checks unless changed inputs invalidate them.

Repeat execution on a compliant unchanged form must not manufacture further controllers, schema layers, or wrappers. Report unrelated debt separately rather than broadening the task.

</execution_steps>

<output_contract>

Return `ANALYZED`, `REFACTORED`, `UNCHANGED`, or `BLOCKED`, with findings/locations, before/after ownership, contract/consumer changes, files, actual verification and gaps, and remaining work.

REFACTORED requires completed correction and applicable verification. If mandatory behavior cannot be verified, report concrete partial progress and the blocker rather than asserting edit/focus preservation. No skill result replaces @architect's final acceptance.

</output_contract>
