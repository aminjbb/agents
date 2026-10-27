---
name: plan-feature-architecture
description: Map a bounded React feature brief into the project's strict FSD owners, public contracts, allowed dependencies, affected consumers, and an implementation order without speculative scaffolding or architecture migration.
---

# Plan Feature Architecture

<inputs>

- Target project, bounded feature brief or equivalent accepted requirements, relevant source/consumers.
- Existing architecture, stack, public APIs, constraints, and accepted product decisions.
- Scope: architecture plan only, or planning within an authorized implementation task. This procedure itself defines the plan, not application source changes.

</inputs>

<execution_steps>

## 1. Establish the active profile

Inspect instructions, source tree, aliases, imports, public boundaries, installed libraries, and tests. This package's active architecture is strict FSD; do not silently switch to Bulletproof React or mix direct-import/barrel/layer policies.

If the inspected application uses another architecture, describe the mismatch and plan a coherent adaptation/migration only if requested. Do not run FSD validators as proof for an unsupported profile. An explicit architecture-change request needs coordinated changes to affected agents/checks, not an isolated folder rename.

## 2. Reuse responsibilities before extracting

Map each behavior to an existing owner where possible. Keep truly screen-specific composition in its page; reusable user actions in features, business concepts in entities, substantial justified blocks in widgets, generic primitives/infrastructure in Shared, and assembly in app.

Prevent both dumping everything into generic folders and creating unnecessary micro-modules. File count alone does not prove a responsibility problem. Do not put domain code in Shared to avoid forbidden imports.

Create only directories needed by current behavior; the existing base scaffold's empty layers/segments remain deliberate structural placeholders, not permission for speculative implementation.

## 3. Define contracts and dependencies

For affected responsibilities specify layer/slice/segment, files to reuse/create/modify, external consumers, typed inputs/results, async/error behavior, state/data authority, and root public exports.

Enforce `app → pages → widgets → features → entities → shared`, no sibling-slice dependencies or type cycles, explicit root `index.ts` external APIs, no own-barrel imports, and no wildcard/layer barrels. Lower modules must not import application router/store types to obtain contracts.

Keep Query/server state in owning api, justified global client state in RTK model, component state local, committed URL facts in navigation contracts, and drafts in one explicit form owner. Assign specialist responsibilities rather than selecting competing implementations.

Identify conflict points: shared index/config files, schema/API type ownership, lazy entry imports, session policy, form defaults/refetch, and consumers of changed exports. Choose one contract owner and a safe integration order before parallel work.

## 4. Decide dependency needs before dependent code

Use [select-project-dependencies](../select-project-dependencies/SKILL.md) for a real new capability/library decision, not for every unchanged installed package. Reuse established Query/RTK/router/form/UI choices; do not install alternatives because an example uses them.

A missing essential backend/design/package decision leaves the dependent contract open. Plan independent pieces without inventing endpoints or locking in speculative interfaces.

## 5. Return a concrete architecture plan

```text
Architecture plan / feature brief ID:
Active profile and inspected evidence:
Responsibility | Existing/new owner | Layer/slice/segment | Files
Public contract | Types/behavior | Consumers | Change owner
Allowed dependency relationships and rejected alternatives:
State/URL/draft/access authority:
Package decisions or no-new-dependency rationale:
Contract/file conflicts and implementation order:
Acceptance scenarios and relevant verification:
Open dependencies and independent work:
```

Do not generate source/folders, install packages, or claim architectural approval merely from this plan. In an implementation task, pass it to [orchestrate-feature-delivery](../orchestrate-feature-delivery/SKILL.md), then execute only authorized operations. The existing scaffold/init skills have their own prerequisites; an empty target is not an existing React Vite project.

Check the plan for consistent ownership, valid contract directions, unnecessary abstractions, affected consumers, and a feasible verification path. Keep small tasks proportionate.

</execution_steps>

<output_contract>

Return `PLANNED`, `NEEDS_INPUT`, or `BLOCKED`, with owners/contracts, inspected evidence, dependency decisions, implementation order, verification needs, and unresolved dependencies. PLANNED is not implemented or architecturally accepted code.

</output_contract>
