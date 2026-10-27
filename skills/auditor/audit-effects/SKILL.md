---
name: audit-effects
description: Review React Effects for real external synchronization, redundant derived state, misplaced event work, dependency/cleanup defects, and project-specific server-state violations. Preserve valid Effects and default to read-only review.
---

# Audit Effects

<inputs>

- Target project, bounded files/diff and relevant consumers, accepted behavior/baseline.
- `mode`: `audit` by default; `fix` only for authorized corrections.

</inputs>

<execution_steps>

1. Read applicable policy and inspect installed React/lint versions, imported Hook identities, custom synchronization hooks, Query/form/router contracts, and existing checks. Search for candidates, then inspect actual syntax/dataflow; an identifier containing Effect is not sufficient evidence.
2. For each relevant Effect record trigger, external resource if any, reactive reads, state/external writes, consumer behavior, dependencies, cleanup, and identity lifetime.
3. Classify it using the decision table below. Trace consumers before deciding removal is safe.
4. Check stale closures, missing dependencies, async races, cleanup on input changes/unmount, repeated setup/teardown, and resource ownership. Development StrictMode repetition alone is not evidence of production duplication or slowness.
5. Return findings in the parent instruction's evidence/impact format. In audit mode do not edit source/config, install tooling, or run auto-fix. Expected behavior can require a legitimate Effect; absence of a test is a coverage gap, not proof the Effect is wrong.

| Classification | Review decision |
| --- | --- |
| Pure render derivation copied into state | Propose render calculation and remove the duplicate writable fact if behavior agrees |
| Response to one known user event | Move to the event's handler/controller while preserving transaction/ordering semantics |
| External subscription/timer/widget/DOM synchronization | Keep justified synchronization; correct dependencies/cleanup rather than deleting it |
| UI fetch or Query-result mirror | Enforce this project's API/Query policy and propose a bounded state-owner correction |
| Form reset, draft sync, route redirect, persistence | Inspect the specific identity/dirty/history contract before changing it |
| Initialization claimed to run exactly once | Inspect resource semantics; do not use a ref flag or suppression to conceal repeated lifecycle defects |

Illustrative removal candidate:

```tsx
const [fullName, setFullName] = useState("");
useEffect(() => setFullName(`${firstName} ${lastName}`), [firstName, lastName]);
```

If fullName is purely derived and no separate edit transaction exists, calculate it during render. Do not add useMemo automatically for this trivial string.

Illustrative valid synchronization:

```tsx
useEffect(() => {
  function onResize() {
    setWidth(window.innerWidth);
  }
  window.addEventListener("resize", onResize);
  return () => window.removeEventListener("resize", onResize);
}, []);
```

This pattern is not redundant merely because it uses an Effect. Inspect initialization and actual resource contract separately; do not certify all surrounding behavior from the fragment.

## Authorized correction

Make the smallest ownership correction, preserve valid external lifecycles, update consumers, and remove replaced state paths together. Avoid remount/key hacks that discard input or focus without an accepted reset policy.

For substantial state/form/router changes read the relevant existing specialist procedure in analysis/refactor mode as authorized; do not invent transport or duplicate caches. Keep FSD/public APIs, no cycles, and 150-line source limits.

Run applicable existing lint/type/tests/build and focused behavior checks: dependency changes, event timing, cleanup/unmount, identity changes, and relevant pending/dirty behavior. Do not claim unchanged behavior from fewer hook calls or static inspection alone.

For calibration use the relevant cases in [review cases](../review-quality-gate/references/review-cases.md). Fixtures are not an executable application or substitute for project evidence.

</execution_steps>

<output_contract>

Return `PASS`, `FAIL`, or `INCOMPLETE` under the auditor verdict rules, with scope/mode, Effect classifications, confirmed findings, hypotheses, actual fixes if authorized, checks, and coverage gaps. A confirmed mandatory violation blocks PASS; legitimate synchronization is not a finding simply because it exists.

</output_contract>
