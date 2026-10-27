# FAgent

Agent instructions and an executable architect-first coordinator for a React SPA engineering workflow governed by Feature-Sliced Design.

The first agent is [@architect — Chief Architect & FSD Delivery Lead](prompts/architect.md), version 1.2.0. It receives every frontend request submitted through the central runtime, then handles requirements/questions, strict-FSD ownership/public contracts, package choices, specialist task plans, integrated verification, and architectural acceptance. Its seven skills are bound in [architect.agent.json](architect.agent.json).

The second agent is [@state-master — State & Data Management Expert](prompts/state-master.md). Its instruction enforces TanStack Query v5 for server state, Redux Toolkit for global client state, local UI state ownership, and FSD-compliant integration. [state-master.agent.json](state-master.agent.json) binds its three canonical skill procedures, English/Persian triggers, and analysis versus implementation modes.

The third agent is [@ui-crafter — UI & Design System Expert](prompts/ui-crafter.md). Its instruction covers Tailwind, Shadcn/Radix composition, focused components, FSD ownership, responsive behavior, accessibility, and an evidence-based design-to-implementation workflow. All seven UI skill definitions are bound in [ui-crafter.agent.json](ui-crafter.agent.json), including English/Persian activation examples and context-sensitive execution rules.

The fourth agent is [@navigator — Routing & Guard Expert](prompts/navigator.md). Its instruction defines Router/FSD ownership, page-level lazy loading, access guards, validated URL state, and navigation verification for an existing React Router v7 or TanStack Router SPA. [navigator.agent.json](navigator.agent.json) binds its four skills, bilingual triggers, and plan/implementation/audit modes.

The fifth agent is [@form-wizard — Form & Validation Expert](prompts/form-wizard.md). Its instruction defines RHF+Zod and deliberate React 19 Action strategies, typed validation, draft preservation, Query-backed submission, errors, and accessibility. [form-wizard.agent.json](form-wizard.agent.json) binds five skills and bilingual activation intents.

The sixth agent is [@auditor — Senior Reviewer](prompts/auditor.md). It independently reviews Effects, memoization, Hook correctness, TypeScript safety, performance evidence, and applicable project rules. [auditor.agent.json](auditor.agent.json) binds six skills and bilingual review/fix intents; source review is read-only by default.

## Central runtime

[frontend.entry.json](frontend.entry.json) defines architect-first intake for all frontend requests in the [Python coordinator](fagent/orchestrator.py). Ready independent tasks run concurrently; overlapping canonical write scopes are serialized, and dependencies wait for actual task approval. A blocked branch does not stop independent work. Clarifications, bounded retries, independent quality review, and final architectural acceptance are persisted.

Run `python -m fagent --help` from this repository. Python 3.11+ and its standard library are sufficient. A real host bridge command must be configured before agent execution; there is no silent mock/provider fallback. See [setup, CLI, response protocol, and limitations](docs/orchestration.md).

```powershell
python -m fagent start --project-root D:/project/my-app --text "Build the requested feature" --adapter-config D:/tools/adapter.json --state .fagent/runs/feature.json
python -m fagent resume --state .fagent/runs/feature.json --adapter-config D:/tools/adapter.json --execute
python -m fagent status --state .fagent/runs/feature.json
```

The first command plans without implementation. The second explicitly authorizes an already-planned run; add `--answers` for pending questions as described in the protocol. Adapter paths above are user-configured examples, not supplied provider bridges. Direct IDE chats outside this entry are not intercepted. All six manifests declare the shared intake policy; their specialist triggers apply to architect-assigned tasks.

Run tests with `python -m unittest discover -s tests -v`. Test bridges are explicitly simulated; successful simulations end as `simulated`, never `delivered`. Declared-scope coordination and returned-file checks are not an OS sandbox; actual tool restrictions belong to the trusted host bridge.

## Host integration

1. Use [frontend.entry.json](frontend.entry.json) and [architect.agent.json](architect.agent.json) for central frontend intake. This repository-specific format is not automatically loaded by Codex or Cursor. Without the runtime bridge, manually load `prompts/architect.md` for intake and use specialist definitions only for its assigned work; that manual workflow does not gain automatic scheduling.
2. Give the agent access to the target React repository and its applicable repository instructions.
3. Supply a concrete feature, refactoring, or review task with observable acceptance criteria.
4. Enable delegation only when your orchestration environment authorizes it and the target agents are available.

For architect-assigned UI work, use [ui-crafter.agent.json](ui-crafter.agent.json) or its instruction/selected skills. Trigger declarations do not independently bypass intake. Review requests remain read-only; design references alone do not authorize implementation.

For architect-assigned state/data work, use [state-master.agent.json](state-master.agent.json) or its instruction/selected skills. State audits use analysis mode; scaffolding/refactoring requires an implementation request. Local UI state is never promoted to Redux solely because a trigger mentions a store.

For architect-assigned routing work, use [navigator.agent.json](navigator.agent.json) or its instruction/selected skills. It preserves the installed router and state contracts; activation does not install a router or authorize hosting changes/deployment.

For architect-assigned form work, use [form-wizard.agent.json](form-wizard.agent.json) or its instruction/selected skills. Complex forms default to compatible RHF+Zod; React 19 Actions require a supported installed version and explicit input/reset ownership. Audits remain read-only.

For architect-assigned quality review, use [auditor.agent.json](auditor.agent.json) or its instruction/matching skills. Confirmed blocking defects yield FAIL, missing required evidence yields INCOMPLETE, and PASS may retain explicit nonblocking suggestions. Fixes require an implementation request; a verdict does not grant merge or deployment authority.

Example task:

```text
@architect: Review the product screen and design an add-to-cart interaction.
Inspect the existing architecture before choosing state or API tools.
Define ownership, public exports, and implementation handoffs.
Implement the authorized changes and report actual verification results.
Acceptance: users can add a product, see pending state, and recover from errors.
```

The prompt can also be used for review-only tasks. State that scope explicitly when implementation is not wanted.

## Architect skills

The architect has four leadership/planning skills and three existing structural skills:

- [analyze-feature-request](skills/architect/analyze-feature-request/SKILL.md): inspect requirements/evidence, establish observable acceptance, and ask only material product questions.
- [plan-feature-architecture](skills/architect/plan-feature-architecture/SKILL.md): map current FSD owners, public contracts, consumers, state authority, and integration order without speculative scaffolding.
- [select-project-dependencies](skills/architect/select-project-dependencies/SKILL.md): reuse installed capabilities or record a verified compatible dependency decision before dependent code; selection itself installs nothing.
- [orchestrate-feature-delivery](skills/architect/orchestrate-feature-delivery/SKILL.md): create bounded task dependencies/write scopes and coordinate authorized specialist execution, integration, and acceptance.
- [init-fsd-structure](skills/init-fsd-structure/SKILL.md): initialize six FSD layers and merge base configuration in an existing React Vite TypeScript project.
- [validate-fsd-boundaries](skills/validate-fsd-boundaries/SKILL.md): audit module references, public APIs, layer direction, slice isolation, and dependency cycles.
- [scaffold-slice](skills/scaffold-slice/SKILL.md): generate a feature or entity skeleton with four segments and an explicit public API.

Load the relevant `SKILL.md` alongside the architect prompt when performing that task. These are execution specifications; they are not installed globally and do not include a standalone scanner or scaffolding CLI.

The orchestration skill includes a [task-plan structural validator](skills/architect/orchestrate-feature-delivery/scripts/validate_task_plan.py) for IDs, owners, dependency cycles/status readiness, and unordered overlapping write scopes. Run it with `python <validator-path> <task-plan.json>`. It does not execute agents, inspect real filesystem links/contracts, grant permissions, or prove application behavior. [Coordination cases](skills/architect/orchestrate-feature-delivery/references/coordination-cases.md) cover ambiguous requests, small edits, multi-owner features, dependency reuse, and architecture conflicts.

Strict FSD remains the active profile across all agents; Bulletproof React is not silently mixed into its import/folder policy. New-project requests begin with intake, while the existing initializer still requires a React Vite TypeScript application. Plan/decomposition requests do not install packages or launch agents; actual parallel work requires host/task authorization and compatible disjoint scopes.

## State management skills

[@state-master](prompts/state-master.md) routes matching work to three complete procedures:

- [scaffold-query-hook.md](skills/state-master/scaffold-query-hook.md): typed Query v5 keys, validated requests, hooks, and public exports.
- [scaffold-redux-slice.md](skills/state-master/scaffold-redux-slice.md): client-only RTK models, selectors, public exports, and application integration.
- [refactor-spaghetti-state.md](skills/state-master/refactor-spaghetti-state.md): step-by-step auditing and state migration with analysis/refactor modes.

The existing discoverable [refactor-spaghetti-state entry point](skills/refactor-spaghetti-state/SKILL.md) loads the canonical procedure above. These Markdown procedures are linked by the prompt; their filenames alone do not install them in a coding tool's automatic skill catalog.

## UI design-understanding skills

For reference-driven work, @ui-crafter reads the design evidence, defines behavior, implements the selected path, and verifies the result:

- [interpret-design-context](skills/ui-crafter/interpret-design-context/SKILL.md): inspect exact Figma nodes or supplied references, map existing components, and distinguish observations from assumptions.
- [define-interaction-contract](skills/ui-crafter/define-interaction-contract/SKILL.md): define user goals, interactions, states, responsive behavior, and acceptance scenarios; ask plain-language questions only for material unresolved decisions.
- [verify-design-implementation](skills/ui-crafter/verify-design-implementation/SKILL.md): compare matched visual references and exercise the behavior contract, with separate verdicts and actual evidence.

Each skill has a `SKILL.md` definition loaded by the prompt. This repository does not install a Figma connector, browser, or automatic skill-discovery adapter. Missing tools or references are reported as coverage gaps, and audits do not authorize source or Figma edits.

## UI implementation and review skills

- [scaffold-ui-component](skills/ui-crafter/scaffold-ui-component/SKILL.md): focused typed component scaffolding with a complete accessible-field example and explicit FSD exports.
- [compose-design-system](skills/ui-crafter/compose-design-system/SKILL.md): reuse primitives, semantic tokens, and typed variants while preserving keyboard, focus, and composition contracts.
- [audit-responsive-accessibility](skills/ui-crafter/audit-responsive-accessibility/SKILL.md): read-only audit by default, with viewport/state evidence, keyboard checks, and explicit coverage gaps.
- [refactor-ui-component](skills/ui-crafter/refactor-ui-component/SKILL.md): bounded correction of oversized, inline-styled, duplicated, or inaccessible UI while preserving behavior and public contracts.

The UI instruction routes new components, design-system composition, audits, and refactors to their definitions. Visual-reference verification and accessibility auditing share applicable evidence without recursively launching each other. Analysis/dry-run modes preserve their non-mutating scope.

## Navigator skills

- [scaffold-route](skills/navigator/scaffold-route/SKILL.md): route/page ownership, supported lazy imports, pending/error handling, and actual chunk/navigation verification.
- [implement-route-guard](skills/navigator/implement-route-guard/SKILL.md): typed session-decision contract, route/data access wiring, safe redirects, and identity transitions without a duplicate auth cache.
- [manage-url-state](skills/navigator/manage-url-state/SKILL.md): typed codecs, canonicalization, history semantics, and Query integration with exclusive URL ownership.
- [audit-routing](skills/navigator/audit-routing/SKILL.md): bounded read-only audit by default, with access, URL/history, lazy, FSD, hosting, and navigation evidence reported separately.

The navigator instruction and manifest route matching work to these definitions. Plan/audit requests do not mutate the application. Query owns session/server data; route guards do not prove backend authorization. Examples are templates for a target application, not an executable router added to this instruction repository.

## Form and validation skills

- [scaffold-validated-form](skills/form-wizard/scaffold-validated-form/SKILL.md): typed schema/controller/UI ownership, RHF resolver example, defaults, and explicit public exports.
- [manage-complex-form](skills/form-wizard/manage-complex-form/SKILL.md): arrays, conditions, steps, subscriptions, draft baselines, refetch/conflict behavior, and stable identity.
- [implement-form-submission](skills/form-wizard/implement-form-submission/SKILL.md): one awaited mutation path, RHF or React Actions, safe FormData/error mapping, reconciliation, and deliberate completion.
- [audit-form](skills/form-wizard/audit-form/SKILL.md): read-only review by default, with validation/lifecycle/submission/accessibility/FSD evidence and explicit gaps.
- [refactor-form](skills/form-wizard/refactor-form/SKILL.md): bounded correction of duplicate state, lost edits, unsafe errors, and tangled forms while preserving public behavior.

The form instruction and manifest route matching work to these procedures. They do not add an executable form application, install packages, implement backend validation, or enable automatic activation without a host adapter.

## Senior reviewer skills

- [audit-effects](skills/auditor/audit-effects/SKILL.md): distinguish derived/event work from valid external synchronization and inspect dependencies/cleanup.
- [audit-memoization](skills/auditor/audit-memoization/SKILL.md): inspect consumers, reference contracts, dependencies, and useful versus ineffective memoization without blanket removal.
- [audit-react-hooks](skills/auditor/audit-react-hooks/SKILL.md): review actual imported APIs, ordinary Hook rules, use exceptions, purity, refs, and identity.
- [audit-typescript-safety](skills/auditor/audit-typescript-safety/SKILL.md): trace authored any and unsafe external flows with effective compiler/type-aware lint coverage.
- [audit-performance](skills/auditor/audit-performance/SKILL.md): define workloads and distinguish confirmed structural problems from measured regressions and hypotheses.
- [review-quality-gate](skills/auditor/review-quality-gate/SKILL.md): select applicable audits/checks, deduplicate findings, and issue an evidence-based verdict.

[Calibration cases](skills/auditor/review-quality-gate/references/review-cases.md) include defective and valid patterns plus verdict scenarios. They are static reference fixtures, not an executable React benchmark or evidence of independent agent/runtime evaluation.

## Scope

This repository contains agent instructions plus a tested local orchestration core and JSON-over-stdio command adapter. It does not contain a React application or a provider-specific model/IDE bridge. A configured trusted host command supplies actual agent/tool execution; the coordinator itself validates protocols, schedules declared work, persists state, and enforces evidence gates.

The 150-line source limit, prohibition of all sibling entity imports, and agent acceptance workflow are project policies. They deliberately make this configuration stricter than baseline FSD. Prose instruction files are outside the source-file limit.

Instruction packages and manifests are available for all six agents: architect, state-master, ui-crafter, navigator, form-wizard, and auditor. The runtime routes frontend intake through architect and uses these definitions for planned work. Tests validate coordination with explicit fixtures, not actual model-provider behavior.

## References

- [FSD layer reference](https://feature-sliced.design/docs/reference)
- [FSD overview](https://feature-sliced.design/docs/get-started/overview)
- [FSD tutorial and public APIs](https://feature-sliced.design/docs/get-started/tutorial)
