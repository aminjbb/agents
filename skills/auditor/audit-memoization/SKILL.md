---
name: audit-memoization
description: Review useMemo, useCallback, and memo through dependency, reference-consumer, purity, compiler, and workload evidence. Preserve useful memoization and avoid unmeasured performance claims or blanket deletion.
---

# Audit Memoization

<inputs>

- Target project/files or diff, relevant consumers, accepted behavior, and any claimed performance improvement/regression.
- Available profiler/workload evidence and effective compiler setup.
- `mode`: `audit` by default; `fix` only for authorized corrections.

</inputs>

<execution_steps>

1. Read policy and inspect actual React/compiler/lint/build versions and configuration. React 19 alone does not establish compiler activation or coverage; verify the integration before relying on it.
2. Resolve useMemo/useCallback/memo imports and aliases. For each candidate record calculation/function, reactive dependencies, output consumers, avoided work, identity-sensitive behavior, and evidence.
3. Trace memoized children, subscription/effect dependencies, caches, and API expectations before removing reference stability. The absence of a local consumer in the same file does not prove irrelevance.
4. Evaluate the cases below. Keep correctness violations separate from optional simplification and performance hypotheses.

| Pattern | Expected assessment |
| --- | --- |
| Trivial primitive calculation with no reference-sensitive consumer | Simplification candidate; not a proven performance regression |
| Expensive computation with repeatable avoided work | Preserve unless a measured/semantic reason supports change |
| Stable props/callbacks feeding a meaningful memoized consumer | Potentially useful; trace actual workload and preserve without contrary evidence |
| Fresh object/function dependency on every render | Cache may be ineffective; inspect how to define inputs at the right scope |
| Missing reactive dependency or impure memo callback | Correctness finding with a concrete trigger |
| Resource correctness relying on permanent cache identity | Redesign ownership; memo is not a lifetime guarantee |
| Compiler-enabled surface with manual memo | Inspect diagnostics/coverage and consumers; no automatic deletion rule |

Trivial candidate:

```tsx
const count = useMemo(() => items.length, [items]);
```

Direct items.length is usually clearer if surrounding behavior has no additional contract. Treat this as an optional simplification unless it violates an explicit task requirement; do not manufacture a blocking defect or speed claim.

Potentially useful pattern:

```tsx
const visibleRows = useMemo(() => expensiveFilter(rows, filter), [rows, filter]);
return <MemoizedGrid rows={visibleRows} />;
```

The fragment does not prove cost or benefit, but it is sufficient reason to inspect consumers rather than blanket-remove caching. A workload/profiler is required to substantiate a performance claim.

## Authorized correction and verification

Change only the demonstrated problem: move stable constants out, correct pure dependency structure, simplify trivial work, or preserve needed memoization. Do not hoist instance-specific data globally or hide reactive reads with refs/suppressions.

If removal changes an Effect's execution frequency, correct its semantic resource/dependency design before asserting preservation. Recheck affected props, subscriptions, references, and observable behavior. Maintain FSD/public APIs, type safety, no cycles, and source limits.

Use [audit-performance](../audit-performance/SKILL.md) when performance is a required claim; return focused evidence rather than recursively invoking memo audits. Run existing relevant lint/type/behavior checks. Report unavailable runtime measurements instead of invented gains.

In audit mode never edit source/config or enable the compiler. Use [review cases](../review-quality-gate/references/review-cases.md) for classification calibration, not proof of project behavior.

</execution_steps>

<output_contract>

Return `PASS`, `FAIL`, or `INCOMPLETE` with candidate decisions and reasons, confirmed correctness findings, optional simplifications, performance hypotheses/measurements, actual fixes if authorized, and gaps. Missing benchmark data is not automatically blocking when no performance claim is in scope; missing evidence for a requested improvement is unresolved.

</output_contract>
