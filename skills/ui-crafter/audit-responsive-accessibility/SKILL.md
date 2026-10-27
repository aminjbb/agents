---
name: audit-responsive-accessibility
description: Audit bounded React UI for responsive layout, accessible semantics, keyboard and focus behavior, status communication, and supported themes or directions. Default to read-only findings with evidence and coverage gaps.
---

# Audit Responsive Accessibility

<inputs>

- Target project, routes/components, relevant states, and accepted behavior.
- Supported browsers/devices, locales/directions/themes, project accessibility target, and available tooling.
- Mode `audit` by default; `fix` only when corrections are authorized by the task.

Do not require Figma for this audit. This skill checks usability mechanics and responsive/accessibility requirements; exact visual-reference fidelity belongs to [verify-design-implementation](../verify-design-implementation/SKILL.md).

</inputs>

<execution_steps>

## 1. Establish bounded coverage

Inspect instructions, source, interaction contracts, existing tests, and supported platforms. Discover actual browser/accessibility capabilities. Record route, data fixture, UI state, viewport, theme, locale/direction, and tools/versions when available.

Use controlled fixtures for pending/error/empty cases. Do not mutate real user data, send messages, or exercise payment/destructive flows without explicit authorization. A mocked flow verifies only the stated boundary.

If browser access is missing, perform useful static inspection and label runtime coverage unavailable. Do not convert missing checks into PASS or N/A. Run non-mutating commands in audit mode; do not install tools, auto-fix, or alter source.

## 2. Check responsive behavior

- [ ] Record actual narrow/mobile, intermediate, wide, and relevant breakpoint-adjacent viewport sizes; use existing product breakpoints rather than inventing a universal device matrix.
- [ ] Check wrapping, flexible sizing, content order, scroll regions, overlays, sticky controls, and accidental page overflow.
- [ ] Exercise long labels, unbroken values, realistic content density, validation messages, pending and empty states.
- [ ] Check zoom/text enlargement and reflow against the project's target. Do not hide clipped content with global overflow rules.
- [ ] Ensure essential actions remain accessible when navigation changes or content is hidden at a breakpoint.
- [ ] Check touch/pointer operation, non-hover access, orientation where relevant, supported theme modes, reduced motion, and RTL when required.
- [ ] Confirm visual reordering does not break reading/tab order. Scrollable wide content must remain discoverable and operable.

## 3. Check semantics and accessible relationships

- [ ] Prefer appropriate native elements, correct heading/landmark structure, action buttons, navigation links, and explicit button types.
- [ ] Check accessible names for all controls, including icon-only and loading controls. Tooltips alone must not supply essential instruction.
- [ ] Check label/control connections, description/error references, required/invalid state, and repeated component IDs.
- [ ] Check `useId` is used at hook-safe scope for generated relationships where needed, caller IDs are respected, and no list keys are generated from it.
- [ ] Inspect `aria-*` and roles for the actual pattern; verify referenced elements exist. Avoid redundant/contradictory ARIA and hidden-but-focusable content.
- [ ] Check meaningful image alternatives and decorative image/icon treatment.
- [ ] Verify errors and selected/disabled states are not conveyed by color alone. Measure applicable text, non-text, and focus contrast against the project's target; do not infer compliance from screenshots.

## 4. Exercise keyboard and focus

- [ ] Reach and operate essential actions with keyboard; verify visible focus and logical order without positive `tabIndex` hacks.
- [ ] Exercise the expected keys for the actual pattern. Tabs, dialogs, menus, and listboxes have distinct interaction contracts.
- [ ] Verify overlay initial focus, modal containment where required, dismissal, and return focus, including trigger removal or disabled triggers when relevant.
- [ ] Check dynamic updates and destructive actions for unexpected focus loss.
- [ ] Check asynchronous announcements and field errors without excessive or duplicate live-region output.
- [ ] Confirm composed Shadcn/Radix children preserve native semantics, props, handlers, and refs rather than assuming library defaults suffice.

Use automated accessibility tools where available and record their scope. Record manual keyboard checks separately. Claim screen-reader coverage only for named assistive technology/browser combinations actually exercised; never present automation as complete accessibility certification.

## 5. Report findings or apply authorized corrections

For each finding include stable ID, severity, route/state/viewport, file location when known, evidence/reproduction, expected versus actual behavior, user impact, and a concrete remedy. Label static-only findings and unverified runtime hypotheses accurately.

Prioritize inaccessible essential actions, focus traps/loss, unreadable content, and missing equivalent mobile actions before decorative issues. Do not describe a preference as a conformance failure. Cite the relevant project criterion or authoritative requirement when asserting a standards violation; do not invent requirement numbers.

In `fix` mode, use [refactor-ui-component](../refactor-ui-component/SKILL.md) for structural corrections when needed and rerun affected checks. Preserve FSD, typed contracts, state ownership, no authored inline styles, and 150-line source limits. Do not redesign unrelated screens.

Share evidence with [verify-design-implementation](../verify-design-implementation/SKILL.md) when it is already running. Do not make the two skills call each other recursively or repeat identical audits without changed inputs.

</execution_steps>

<output_contract>

Return `PASS`, `FAIL`, or `INCOMPLETE`, with declared scope/environment, findings, actual methods/results, fixes if authorized, and coverage gaps.

- `PASS`: all applicable checks in the declared bounded scope passed with evidence.
- `FAIL`: confirmed unmet requirements remain; still report unavailable coverage.
- `INCOMPLETE`: no confirmed remaining violation, but required coverage is missing.

Use N/A only for a genuine scope exclusion with rationale, not absent tooling. This audit is neither full-product accessibility certification nor research-based proof of user comprehension. It does not replace @architect's acceptance.

</output_contract>
