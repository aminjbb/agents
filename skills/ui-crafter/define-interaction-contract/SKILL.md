---
name: define-interaction-contract
description: Turn design evidence and product goals into an implementation-ready user journey, state matrix, and acceptance scenarios. Resolve material UX ambiguity using plain-language choices rather than requiring technical explanations from the user.
---

# Define Interaction Contract

<inputs>

- Bounded feature/screen goal and target project root.
- Evidence brief from [interpret-design-context](../interpret-design-context/SKILL.md), or equivalent traceable references.
- Existing accepted behavior, routes, state/API contracts, supported devices/locales, and user decisions.
- Task mode: analysis/design only or authorized implementation. This skill defines behavior; it does not itself authorize source changes or publishing.

</inputs>

<execution_steps>

## 1. Define the user's job

State the intended user, task, entry point, primary action, and observable success in plain language. Use the requested scope, not an invented persona or business objective.

Trace the happy path and relevant alternatives: cancellation, back navigation, invalid input, pending requests, failure/retry, empty results, and completion. Include permissions, draft loss, or destructive actions only when relevant to the requested feature.

## 2. Build the behavior contract

For each actionable element, specify:

- Trigger and prerequisites.
- Resulting state, visible feedback, and next location/action.
- Keyboard operation and focus behavior.
- Pending, disabled, failure, retry, cancel, and success behavior where applicable.
- Whether data is local, client-global, remote-authoritative, or URL-authoritative.
- Evidence/decision source and unresolved assumptions.

Map server operations to @state-master's Query API contract, global client intent to its RTK model contract, and local presentation state to UI. Do not invent endpoints or implement fetch effects to fill missing contracts. Keep field validation/submission ownership with @form-wizard when applicable.

Specify responsive content order and navigation, not just smaller dimensions. Use supplied mobile evidence when available; label proposed adaptations explicitly. Keep accessible reading/focus order and equivalent essential actions across layouts.

## 3. Classify ambiguity by consequence

| Decision type | Action |
| --- | --- |
| Explicit current requirement or previously accepted behavior | Reuse it; do not ask again. |
| Routine visual/interaction detail covered by the project system | Follow the convention and record its source. |
| Reversible low-impact detail without a convention | Choose a reasonable default and disclose the assumption. |
| Material ambiguity affecting destination, data persistence/loss, purchase, deletion, permissions, or core task completion | Obtain the missing decision before implementing that dependent behavior, unless existing task authorization explicitly delegates it. |
| Missing technical contract | Inspect existing interfaces or coordinate with the responsible owner; do not ask a nontechnical user to design store/API internals. |

Do not make every question a mandatory approval gate. Do not interpret elapsed time or silence as a decision. While a required answer is pending, continue independent authorized layout/component work with clearly isolated unresolved behavior.

## 4. Ask questions the user can answer

Use the user's language and describe outcomes, not UI jargon. Ask a small bundle of essential questions, preferably with two or three concrete choices and a recommendation with its tradeoff.

Example:

> After someone adds a product, should they stay on this page and see confirmation, or go straight to the cart?

Avoid asking the user to choose between technical mechanisms such as Redux versus Query, portal versus inline DOM, or optimistic versus pessimistic cache updates.

When a visual choice is difficult to describe, offer a small reversible comparison preview if the task authorizes building one. Label fixtures and simulated interactions. A preview must not execute real purchases, deletes, messages, or other external effects merely to demonstrate a choice.

## 5. Record decisions and acceptance scenarios

Use stable decision IDs such as `DEC-001`, linked to evidence IDs. Mark each as `ACCEPTED`, `CONVENTION`, `ASSUMED`, or `OPEN`; identify the source. Do not mark an agent proposal accepted without an actual decision or explicit delegated authority.

Use this compact contract, scaled to the task:

```text
Interaction contract
Goal / user / scope:
Design references and evidence IDs:
Entry → primary steps → completion:
Element | Trigger | Preconditions | State/result | Feedback/focus | Source
State | Visible content | Available actions | Recovery/next step
Responsive and accessibility behavior:
Data/command interfaces and responsible owners:
Decision ID | Decision | Status/source | Dependent work
Acceptance: Given ... When ... Then ...
Open questions and explicitly excluded behavior:
```

Write observable scenarios for critical success and failure paths. For example, a failed add-to-cart operation must show recovery and must not claim the item was added. Avoid tests phrased solely as implementation details or screenshot similarity.

If the contract changes, update affected scenarios and consumers; retain relevant decision provenance. Reconfirm only material changes that invalidate a prior user decision.

## 6. Hand off one complete path

For multi-screen or ambiguous work, implement one bounded end-to-end path first under the parent instruction after resolving its required decisions. For a simple component, use its complete local interaction as the path; do not force a separate prototype project.

Pass the contract, evidence references, accepted decisions, and open dependencies to implementation and [verify-design-implementation](../verify-design-implementation/SKILL.md). Keep mock data clearly identified and do not report simulated behavior as integrated functionality.

</execution_steps>

<output_contract>

Return `READY`, `NEEDS_INPUT`, or `BLOCKED`, the contract, required questions if any, safe independent work, and remaining dependencies.

- `READY`: the selected path has sufficient behavior definitions and no unresolved material decisions. Disclosed low-impact assumptions may remain.
- `NEEDS_INPUT`: a specific material product decision remains open; only its dependent behavior waits.
- `BLOCKED`: essential references, technical contracts, or access prevent defining the selected path. Identify the missing dependency without fabricating behavior.

The contract is not a blanket user approval or permission grant. Preserve the assigned scope and host authorization rules.

</output_contract>
