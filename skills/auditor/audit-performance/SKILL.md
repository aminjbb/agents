---
name: audit-performance
description: Inspect and measure relevant React render, subscription, request, bundle, or resource concerns using reproducible workloads and explicit evidence. Separate structural defects, performance hypotheses, and measured improvements.
---

# Audit Performance

<inputs>

- Target project and bounded interaction/change/claimed regression or improvement.
- Available baseline, realistic fixtures/data volume, supported environment, and metric/budget if defined.
- Existing build/browser/profiler/network tools and `mode`: `audit` default, `fix` only when authorized.

</inputs>

<execution_steps>

## 1. Define what is being assessed

Identify the user path, workload/data size, changed behavior, affected consumers, relevant metric, and accepted budget if any. Never invent a universal timing/render/bundle threshold.

Inspect installed React/compiler/library versions, actual compiler configuration, build mode, and available tools. Do not infer enabled compiler, memo coverage, or production costs from React version.

If a request concerns only unrelated type/text changes, justify excluding measurement by impact. If it explicitly claims speed/memory improvement or a regression, missing required measurements are unresolved coverage, not N/A.

## 2. Inspect plausible causes

Trace expensive repeated calculations, wide subscriptions, Context churn, unstable props consumed by memoized children, remounts from keys/nested components, repeated requests/waterfalls, eager page imports, retained listeners/timers, and resource cleanup in the affected path.

Classify evidence accurately:

- A confirmed duplicate request, leaked listener, or broken lazy import may be a structural/correctness defect even without a speed measurement.
- A large loop, repeated render, or unstable reference without demonstrated impact is a hypothesis, not proven user-visible slowness.
- Existing memoization, Query deduplication, or a library subscription model may already avoid suspected work; inspect the actual consumer behavior.

Use [audit-memoization](../audit-memoization/SKILL.md), [audit-effects](../audit-effects/SKILL.md), or the relevant specialist procedure only when their depth is needed. Share evidence and do not recurse into quality-gate orchestration.

## 3. Measure when the claim requires it

Use installed React Profiler, browser performance/network tooling, build reports, or appropriate resource diagnostics. Record environment, versions, build/instrumentation mode, route/fixture, device/viewport where relevant, reproduction steps, metric units, samples, and baseline identity.

Compare like conditions. Distinguish development StrictMode/instrumentation overhead and warm/cold caches. Repeat enough to identify obvious noise; report raw observations and variability rather than fabricated precision or cherry-picked best runs.

Do not use console-log counts as elapsed-time evidence, label one microbenchmark an application-wide gain, fabricate percentages, or claim memory leaks from one unexplained snapshot. Missing tools/baselines produce explicitly bounded conclusions.

## 4. Correct within authorized scope

Audit mode does not authorize source/config changes, profiler installation, compiler adoption, or external writes. In fix mode choose the smallest evidenced intervention: narrow subscriptions, correct ownership/dependencies, preserve stable identity, remove real duplicate work, or adjust loading boundaries.

Do not add blanket memoization, caching, virtualization, workers, debounce, or a new library without a demonstrated requirement. Do not remove valid memoization to meet a stylistic target. Preserve form edits/focus, route behavior, data freshness, accessibility, and FSD/public APIs.

Recheck correctness and the same workload after changes. If the measurement is inconclusive, report it rather than asserting the optimization worked. Keep no-any, acyclic imports, source limits, and existing applicable type/lint/test/build checks.

## 5. Report bounded evidence

```text
Workload / changed path / revision:
Environment / build mode / fixture size:
Metric / method / units / baseline:
Samples and variation:
Confirmed structural findings:
Measured regression/improvement, if substantiated:
Hypotheses and missing evidence:
Actual corrections and correctness checks:
```

Use [review cases](../review-quality-gate/references/review-cases.md) for calibration. A benchmark plan or fixture is not an executed profile. Do not claim whole-product speed, accessibility, or resource safety from a single bounded path.

</execution_steps>

<output_contract>

Return `PASS`, `FAIL`, or `INCOMPLETE` under the auditor rules, with scope, structural findings, real measurements, hypotheses, authorized changes, actual verification, and gaps. Optional performance suggestions alone do not block PASS; an unverified requested performance claim remains INCOMPLETE absent another confirmed blocker.

</output_contract>
