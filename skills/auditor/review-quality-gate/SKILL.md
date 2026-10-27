---
name: review-quality-gate
description: Coordinate applicable React, Effect, memoization, TypeScript, performance, and FSD checks for a bounded independent quality review, deduplicate evidence, and issue PASS, FAIL, or INCOMPLETE without changing source by default.
---

# Review Quality Gate

<inputs>

- `project_root`, requested scope/diff/files, comparison base if explicitly available, and acceptance criteria.
- Existing owner instructions, prior findings/check evidence, installed tools, and `mode`: `audit` default or authorized `fix`.

Resolve the target independently of this package. Missing Git/base/access must be reported; do not invent a clean baseline or implied user approval.

</inputs>

<execution_steps>

## 1. Establish the review matrix

Read applicable instructions and inspect the actual diff/source plus relevant consumers, public contracts, config, versions, and tests. Identify introduced changes versus demonstrated pre-existing debt without expanding into an unrelated rewrite.

Select skills/checks by the change's impact, not a requirement to run every audit:

| Surface | Procedure |
| --- | --- |
| Effects or lifecycle/data synchronization | [audit-effects](../audit-effects/SKILL.md) |
| Memoized values/callbacks/consumers | [audit-memoization](../audit-memoization/SKILL.md) |
| Hooks, render/ref/component identity, React APIs | [audit-react-hooks](../audit-react-hooks/SKILL.md) |
| Authored types, external data, contracts | [audit-typescript-safety](../audit-typescript-safety/SKILL.md) |
| Requested performance claim or demonstrated cost/resource concern | [audit-performance](../audit-performance/SKILL.md) |
| Import/public API/dependency changes | [validate-fsd-boundaries](../../validate-fsd-boundaries/SKILL.md) |

Read selected definitions in full and honor their audit modes. For domain-specific state, UI, routing, or forms use the specialist definitions linked by the auditor instruction only when applicable. A producer's report can supply traceable evidence but cannot replace independent source/consumer inspection.

Record each check as required or excluded with scope rationale and expected evidence. Tool absence is not an exclusion. Do not silently require a full browser/profile suite for a trivial unrelated change.

## 2. Gather independent evidence

Run existing supported non-fixing type/lint/tests/build and necessary behavior/import checks in authorized temporary/ignored output locations. Do not auto-fix source, overwrite tracked output, install packages, migrate configs, or perform real external writes during audit.

Inspect tool coverage: included files, tsconfig references, aliases, type-aware lint support, Hook rule versions, compiler integration, and partial scans. A passing command is evidence only for what it checked.

Preserve concrete findings, uncertainties, optional suggestions, actual commands/results, and unavailable coverage. Follow suspected issues through imports/consumers before calling them confirmed; do not fill a report with ungrounded warnings.

## 3. Apply corrections only if authorized

Keep corrections bounded to confirmed defects/requirements. Use selected skills in fix mode while preserving their scope and specialist ownership; do not delegate unless authorized and available.

Preserve valid Effects/memos, behavior, state/focus, public APIs, strict typing, FSD, source limits, and unrelated work. Update consumers and rerun only affected checks unless new evidence justifies broader testing. Return evidence to this active caller rather than recursively starting another quality gate.

## 4. Aggregate the verdict deterministically

Deduplicate root causes and attach locations, severity/impact, explicit blocking flag, rule/contract, trigger, consequence, evidence/certainty, remedy, and verification needed. Separate confirmed defects from hypotheses and optional P3 suggestions.

Use check statuses `PASS`, `FAIL`, `NOT_RUN`, `INCONCLUSIVE`, or justified `N/A`. Preserve required-check gaps even when a blocker already determines the verdict.

Apply this order:

1. Any confirmed unresolved blocking violation or acceptance failure → overall `FAIL`.
2. Otherwise, any required applicable check not adequately passed or a missing essential contract/evidence → overall `INCOMPLETE`.
3. Otherwise → overall `PASS`, possibly with explicit nonblocking suggestions.

A raw tool failure may be infrastructure/inconclusive rather than a confirmed code defect; diagnose it before categorization. Conversely a passing build does not cancel a confirmed policy violation or missing runtime evidence.

Scope PASS to the actual reviewed revision/files/path. This is not a merge/deployment grant, @architect's final acceptance, backend authorization proof, or complete accessibility certification.

## 5. Calibrate and report

Use [review cases](references/review-cases.md) when validating or changing these instructions. The cases include both defects and correct patterns; expected answers are calibration aids, not proof an audit tool ran. Record static assessment separately from runtime/compiler/profiler coverage.

Use the parent auditor response contract: scope/mode/baseline, concise conclusion, impact-ordered confirmed findings, hypotheses/suggestions, actual fixes if any, skills/check statuses, evidence gaps, and remaining work. If no confirmed findings exist, state that clearly without implying unperformed checks passed.

</execution_steps>

<output_contract>

Return `PASS`, `FAIL`, or `INCOMPLETE` with the exact declared scope/revision and evidence matrix. A review remains useful when incomplete; report the missing dependency and independent progress instead of inventing success or stopping all inspection prematurely.

</output_contract>
