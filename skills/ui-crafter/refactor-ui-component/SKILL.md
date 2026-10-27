---
name: refactor-ui-component
description: Refactor oversized, duplicated, inline-styled, or inaccessible React UI into cohesive FSD-owned components while preserving public behavior, focus, state ownership, and design-system consistency.
---

# Refactor UI Component

<inputs>

- Target project and bounded files/components, demonstrated problem, expected behavior, and accepted visual/interaction contracts.
- Mode `analyze` for review/design/dry run; `refactor` for authorized implementation.
- Relevant findings from a responsive/accessibility audit or visual verification when available. A prior audit is not mandatory for an obvious source-level issue.

</inputs>

<execution_steps>

## 1. Capture the current contract

Read instructions and inspect components, consumers, styles/tokens, primitives, events, refs, ID relationships, local state, and integration tests. Preserve unrelated/uncommitted work.

Identify public exports, controlled/uncontrolled behavior, form semantics, native attributes, focus/selection behavior, overlays, responsive/themed layouts, and observable success/error/pending states. Capture relevant existing runtime evidence if tools are available; distinguish current defects from behavior to preserve.

Use [interpret-design-context](../interpret-design-context/SKILL.md) for supplied references and [define-interaction-contract](../define-interaction-contract/SKILL.md) for materially ambiguous behavior. Do not reinterpret a layout cleanup as permission to change the user journey.

## 2. Diagnose responsibilities

- [ ] Count physical source lines, including blanks/comments, and identify cohesive extractions needed to meet the 150-line file/component maximum.
- [ ] Locate authored `style` props, style-object spreads, HTML style attributes, DOM style writes, CSS-variable style injection, and runtime class fragments.
- [ ] Identify duplicate primitives, repeated variant/token definitions, broad global selectors, and incidental DOM-dependent styling.
- [ ] Trace nested interactions, swallowed props/handlers/refs, invalid naming/ARIA, focus bugs, and responsive clipping.
- [ ] Trace data/state ownership. UI transport, query cache mirrors, and global/local state confusion require coordination with @state-master, not a cosmetic wrapper.

Dependency-internal positioning styles are not authored UI overrides. Preserve them; do not blanket-exempt copied/customized project files or strip library styles blindly.

## 3. Plan a bounded correction

Choose meaningful responsibility boundaries: primitive, domain representation, action UI, compound subcomponent, finite variant map, local behavior hook, or screen composition.

Place generic primitives in Shared and domain code in its slice. Cross-slice dependencies point strictly downward with no sibling imports. External consumers use root `index.ts` APIs; internal implementation uses relative imports. No wildcard/layer barrels or cycles, including type cycles.

Keep the existing public contract when possible. For necessary ownership/export changes, provide @architect with the concrete proposal and affected consumers. Do not leave compatibility re-exports that launder forbidden dependencies.

In `analyze` mode, return findings, proposed extractions, contract changes, and verification needs now. Do not modify source, auto-fix, install packages, or run generators.

## 4. Refactor without behavioral drift

1. Reuse [scaffold-ui-component](../scaffold-ui-component/SKILL.md) for genuinely new focused components and [compose-design-system](../compose-design-system/SKILL.md) for shared primitive/variant changes. Do not regenerate existing implementation or run overwrite-prone generators.
2. Replace authored inline styles with static Tailwind classes, bounded class maps, or justified scoped stylesheet classes. Map repeated values to existing tokens; do not change global tokens to repair a local layout.
3. If a required runtime layout cannot comply without an exception, report the concrete conflict; do not inject styles through another route or break the behavior to satisfy a text search.
4. Preserve prop defaults, controlled ownership, event/default-prevention semantics, ref forwarding, ID relationships, and native form behavior. Use the installed React/primitive API conventions.
5. Define extracted components at stable module scope. Do not create component types inside render and accidentally remount subtrees, reset input state, or lose focus. Preserve meaningful list keys.
6. Restore semantics and keyboard/focus contracts when accessibility correction is part of the task. Use proper primitives rather than hand-rolled incomplete interaction models.
7. Remove replaced implementation, unused classes, dead exports, and obsolete wrappers after checking all consumers. Keep independent UI state local and data orchestration with its owner.

Do not evade line limits with minification, arbitrary fragments, or code-generation labels. Do not claim a hook extraction fixed the problem if the same mixed responsibilities remain.

## 5. Recheck the actual change

Run affected existing type/lint/build and behavior checks; add proportionate tests for nontrivial changed interactions. Verify preserved local state, focus, controlled props, native attributes/events, and repeated instances.

Use [audit-responsive-accessibility](../audit-responsive-accessibility/SKILL.md) in audit mode after corrections where relevant; when invoked from an audit, return results to that caller rather than starting another fix/refactor loop. Use [verify-design-implementation](../verify-design-implementation/SKILL.md) for reference fidelity and [validate-fsd-boundaries](../../validate-fsd-boundaries/SKILL.md) for import/cycle checks as applicable. Reuse current evidence and avoid recursive skill invocation.

Confirm source limits, no introduced inline-style bypass, no duplicated components, no illegal imports, and no competing state owner. Report missing browser/test coverage rather than claiming preserved appearance or focus without observation.

A repeat execution on compliant unchanged code must not create further unnecessary layers or wrappers.

</execution_steps>

<output_contract>

Return `ANALYZED`, `REFACTORED`, `UNCHANGED`, or `BLOCKED`, with findings/locations, before-and-after responsibilities, public-contract changes, files, actual verification, remaining risks, and work.

`REFACTORED` requires implemented correction and applicable verification. Partial source edits with unresolved required checks must be reported as progress with the concrete blocker, not full completion. No skill status replaces @architect's final acceptance.

</output_contract>
