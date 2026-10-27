---
name: analyze-feature-request
description: Turn a React feature or new-project request into a bounded product brief with observable acceptance criteria, known context, explicit assumptions, and material questions before architecture or implementation.
---

# Analyze Feature Request

<inputs>

- User request and available product/design references.
- Target `project_root` when known; otherwise inspect the current context before asking for an essential destination.
- Existing accepted behavior, constraints, prior decisions, and task mode.

This skill analyzes requirements. It does not install packages, initialize an application, change source, publish, or launch agents. Keep the instruction package and target project distinct.

</inputs>

<execution_steps>

## 1. Inspect before reinterpreting

Read applicable instructions and relevant source/docs/design evidence. Determine whether the target is an existing application, an empty destination, or only an instruction repository. Do not assume this package is the requested React app or that a new-project request meets an existing-Vite scaffold prerequisite.

Identify the user goal, current behavior, requested change, accepted stack/architecture, existing reusable capabilities, and essential external contracts. Do not invent backend endpoints, permissions, visual references, successful checks, or deployment scope.

## 2. Define the bounded outcome

State who performs what action, entry/preconditions, primary path, observable success, and relevant failure/empty/pending/cancel behavior. Scale detail to the request: a small label/layout edit does not need a full product discovery exercise.

Separate requested behavior from technical choices. Record in-scope behavior, explicit exclusions, data/identity/access implications, and existing acceptance criteria. Do not turn an example into an exhaustive requirement or add speculative features.

Label each material statement as `USER_REQUIREMENT`, `EXISTING_CONTRACT`, `PROJECT_CONVENTION`, `ASSUMPTION`, or `OPEN`. Attach a real source/decision reference and retain prior accepted answers; confidence alone is not authorization.

## 3. Resolve only material unknowns

- Reuse explicit decisions and project conventions without asking again.
- Infer routine reversible implementation details and disclose consequential assumptions.
- Inspect technical contracts or involve their owner instead of asking a nontechnical user to choose internal types/stores.
- Ask concise questions in the user's language for missing decisions that materially change persistence, access, payment/deletion, navigation, or task completion, unless already delegated.
- Prefer a few outcome-based choices over UX/framework jargon. Do not treat elapsed time or silence as a decision.
- Continue independent analysis/planning while a required answer is pending; identify only the dependent work that must wait.

For supplied Figma/reference-driven UI, use the existing [design interpretation](../../ui-crafter/interpret-design-context/SKILL.md) and [interaction contract](../../ui-crafter/define-interaction-contract/SKILL.md) procedures when useful. Do not assert skill execution or delegate without host/task authorization.

## 4. Return a reusable feature brief

```text
Feature brief / stable ID:
Target application and current baseline:
Goal / user / entry / success:
Primary path and relevant alternatives:
In scope / out of scope:
ID | Requirement or assumption | Provenance/source | Dependent work
Given ... When ... Then ... acceptance scenarios:
Confirmed constraints and reusable capabilities:
Material open questions and safe independent work:
```

Return in the task report or established authorized artifact location; do not create a documentation tree or demand approval for routine reversible work. Reuse/update current briefs rather than duplicating them.

Hand the brief to [plan-feature-architecture](../plan-feature-architecture/SKILL.md) only when architecture/implementation planning is in scope. Analysis completion does not imply permission to implement, install dependencies, or create a runtime.

</execution_steps>

<output_contract>

Return `READY`, `NEEDS_INPUT`, or `BLOCKED`, with the brief and sources. READY means the bounded task is sufficiently specified, not implemented. NEEDS_INPUT identifies material decisions and dependent work. BLOCKED identifies an essential inaccessible prerequisite; independent authorized inspection may continue.

</output_contract>
