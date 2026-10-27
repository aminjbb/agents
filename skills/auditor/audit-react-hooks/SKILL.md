---
name: audit-react-hooks
description: Review actual React Hook/API usage for legal call context, dependency correctness, pure rendering, stable identities, refs, and async lifecycle behavior using the installed version. Account for the distinct use API rules.
---

# Audit React Hooks and Render Rules

<inputs>

- Target project/files/diff and relevant call sites/custom Hooks.
- Installed React/lint/compiler setup and accepted behavior.
- `mode`: `audit` default; `fix` only when authorized.

</inputs>

<execution_steps>

1. Inspect effective Hook lint rules and installed APIs. Resolve import origins/aliases, custom Hook definitions, and component call contexts; do not classify solely by a use prefix or regex.
2. Check ordinary Hooks are called consistently at the top level of a component/custom Hook, not conditionally, in loops/handlers, after a conditional early return, or in arbitrary callbacks/async functions.
3. Apply React's use API rules separately: conditions/loops are allowed, but component/hook context is still required and try/catch is not allowed. Do not generalize this exception or assume an unfamiliar use-prefixed function is that API.
4. Inspect actual reactive reads/dependencies and supported custom-hook lint configuration. Detect stale closures and hidden dependencies; do not silence lint, substitute run-once refs, or prescribe unsupported new APIs.
5. Inspect render purity, prop/state immutability, refs, stable component definitions/keys, and correct ownership of subscriptions/resources. A new object allocation alone is not an impurity defect.
6. Inspect event/default-prevention/ref composition and relevant Action/transition context. Never invoke hooks in async mutation/loader/action bodies; use approved bound commands.
7. Check setup/cleanup behavior, unmount/identity changes, late asynchronous results, and development StrictMode interpretation. Trace semantic outcomes, not console-log counts alone.

## Avoid false positives

- Legitimate refs for non-render resources are allowed; inspect their reads/writes rather than banning refs.
- Supported narrow conditional render-state adjustment patterns require semantic inspection; do not force every adjustment into an Effect.
- Module-scope component definitions and stable keys preserve identity; extraction inside render can introduce remounts and input/focus loss.
- An intact primitive's internal implementation is not automatically a defect because it contains unfamiliar Hooks. Review authored adapters and real installed contracts.
- A passing lint command covers configured/included files and supported rules only. Compiler diagnostics may exist without compiler execution; compiler coverage is not implied by React version.

Confirmed ordinary Hook violation example:

```tsx
function Counter({ enabled }: { enabled: boolean }) {
  if (!enabled) return null;
  const [count] = useState(0);
  return <span>{count}</span>;
}
```

When enabled changes, the ordinary Hook call sequence changes. Use actual component/Hook semantics to correct it rather than suppressing a rule.

Distinct React use example:

```tsx
function Label({ enabled }: { enabled: boolean }) {
  if (!enabled) return null;
  const theme = use(ThemeContext);
  return <span>{theme.label}</span>;
}
```

Assuming supported React and the actual imported use API/context contract, this is not an ordinary-hook-order violation. It does not certify unrelated context typing or application behavior.

## Corrections and checks

Audit mode is read-only: no source/config changes, installs, or auto-fix. In authorized fix mode make bounded corrections preserving state, focus, and consumers; no framework migration or blanket effect/memo deletion.

Use [audit-effects](../audit-effects/SKILL.md) or [audit-memoization](../audit-memoization/SKILL.md) for relevant depth and share evidence with the active caller. Do not orchestrate the quality gate recursively.

Run supported existing lint/type/tests/build and focused behavior checks where applicable. Keep FSD boundaries, no any, acyclic imports, and 150-line limits. Use [review cases](../review-quality-gate/references/review-cases.md) for calibration and report unavailable runtime/tool coverage.

</execution_steps>

<output_contract>

Return `PASS`, `FAIL`, or `INCOMPLETE`, with scope/mode/version coverage, resolved API identities, confirmed findings/reproduction, hypotheses, authorized changes, actual checks, and gaps under the auditor finding/verdict contract.

</output_contract>
