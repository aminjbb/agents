---
name: verify-design-implementation
description: Compare an implemented React UI against identified design evidence and an interaction contract using matched screenshots, user-path checks, responsiveness, and accessibility evidence. Report visual fidelity and UX behavior separately.
---

# Verify Design Implementation

<inputs>

- Target project root, implemented route/component, local preview access, and bounded verification scope.
- Exact design reference/node/variant and evidence brief from [interpret-design-context](../interpret-design-context/SKILL.md) or equivalent traceable sources.
- Interaction contract/decisions from [define-interaction-contract](../define-interaction-contract/SKILL.md), or existing accepted behavior sufficient for the scope.
- Mode: `audit` by default; `fix` when corrections are authorized. A request to implement the UI includes relevant reversible corrections, but not real external transactions or publishing.

</inputs>

<execution_steps>

## 1. Establish a reproducible comparison

1. Discover available browser, screenshot, interaction, accessibility, and project-check tools. Do not assume a tool exists or invent screenshots.
2. Inspect current source and existing run commands. Use the project's normal local preview when authorized; do not deploy or expose a server publicly to obtain a screenshot.
3. Identify the implementation revision or changed files, route, fixture/account scope, reference node/variant, and comparison state. Missing evidence must be recorded rather than treated as a pass.
4. Match viewport, content, locale/direction, theme, state, and screenshot framing. Record browser, viewport CSS dimensions, device scale when available, and capture conditions. Wait for fonts/assets and the relevant settled state; disable incidental animation only when it does not change the behavior under test.
5. Use controlled test data for risky flows. Never execute a real payment, delete real user data, send a message, or make another external mutation solely for verification without explicit authorization. Label fixtures, mocked requests, and untested integration boundaries.

## 2. Compare visual evidence

Capture the actual implementation and inspect it alongside the reference. Use overlays or pixel-diff tools when available and useful; record alignment, masks, and limitations. Do not stretch images to conceal layout differences.

Check hierarchy, content order, component sizing, alignment, spacing, typography/font availability, colors, borders, radius, elevation, asset choice/crop, and relevant state variants.

For each discrepancy record reference evidence ID, actual/expected result, location, impact, and suggested correction. Distinguish rendering/antialiasing noise from a meaningful layout mismatch.

Do not invent a similarity percentage, universal pixel threshold, or pixel-perfect verdict. A numeric result requires an actual tool, declared method, and justified tolerance. Mask only nondeterministic regions, disclose them, and never mask missing content or broken states.

For sizes not represented in the design, verify the disclosed responsive contract rather than claiming visual equivalence to a nonexistent reference. Accessibility or functional corrections may justify a documented design deviation; preserve required semantics and resolve material product conflicts instead of copying a flaw blindly.

## 3. Execute the interaction contract

Test the selected path's accepted Given/When/Then scenarios, not just the initial screenshot:

- Entry, primary action, navigation, completion, cancellation/back behavior where relevant.
- Pending, empty, failure/retry, success, and disabled states required by the contract.
- Preservation of user input/drafts and prevention of unintended duplicate submissions.
- Keyboard access, visible focus, overlay opening/dismissal/return focus, accessible names, and valid label/description/error relationships.
- Narrow, intermediate, wide, and relevant breakpoint widths; long content, zoom/text enlargement, supported RTL/themes, and reduced motion as applicable.

Read and use existing project interaction/accessibility tests when available. Automated accessibility checks do not establish screen-reader coverage; record manual keyboard and assistive-technology checks separately. Do not claim a business flow works if only a mocked happy path was exercised.

## 4. Check implementation boundaries

Confirm corrections preserve typed props, FSD ownership/public APIs, no authored inline styles, the 150-line source limit, and no UI transport or duplicate state ownership.

Use available static/build checks and the shared [validate-fsd-boundaries skill](../../validate-fsd-boundaries/SKILL.md) within its scope. A boundary PASS or successful build does not replace visual and behavioral evidence.

## 5. Correct and recheck within scope

- In `audit` mode, report findings without source edits or auto-fixes.
- In `fix` mode, correct demonstrated discrepancies using existing components/tokens, then recapture affected views and rerun affected scenarios/checks. Do not redesign unrelated screens or alter global tokens for a local problem.
- Prioritize broken paths, inaccessible controls, data-loss risks, and major structural mismatches before decorative discrepancies.
- Continue while actionable evidence supports progress. If repeated corrections leave the same failure unchanged, diagnose the reference, environment, or missing contract before further edits. Report a concrete unresolved dependency rather than cycling cosmetic guesses or claiming success.

## 6. Return evidence and a bounded verdict

```text
Design implementation verification
Scope / route / source revision:
Reference nodes/variants and contract decisions:
Environment / viewports / state / data / locale / theme:
Capture or test artifact | Reference/state | Method | Limitation
Finding | Expected | Actual | Impact | Location | Correction/recheck
Visual fidelity: PASS / FAIL / INCOMPLETE
Interaction behavior: PASS / FAIL / INCOMPLETE
Responsive/accessibility: PASS / FAIL / INCOMPLETE
Architecture/source checks: PASS / FAIL / INCOMPLETE
Changes made, actual commands/results, and remaining work:
```

Link real artifacts where the host supports them. Do not save duplicate screenshots indefinitely, commit sensitive captures, or report nonexistent artifact paths. Use established task-artifact conventions and authorized storage only.

</execution_steps>

<output_contract>

Return overall `PASS`, `FAIL`, or `INCOMPLETE`, preserving separate category verdicts and the scope of each check.

- `PASS`: all applicable declared checks passed with adequate evidence; known design deviations are explicit and justified by accepted requirements.
- `FAIL`: at least one confirmed unmet requirement remains. Still disclose missing coverage.
- `INCOMPLETE`: no confirmed remaining violation, but missing reference, browser, environment, or contract evidence prevents a pass.

A missing category may be `N/A` only with a scope-based explanation, never merely because its tools are unavailable. Evidence from one viewport or state does not verify the whole application. This verdict is not @architect's final architectural acceptance or proof of research-based UX usability.

</output_contract>
