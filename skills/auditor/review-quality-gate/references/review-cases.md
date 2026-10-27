# Auditor Calibration Cases

These bounded snippets are static review fixtures, not an executable React application. Assume imports/types mentioned in each case resolve as stated. Evaluate the stated scope; do not invent surrounding defects or claim lint/browser/profile execution from reading a snippet.

For each case return confirmed findings, optional suggestions, missing evidence, safe correction if relevant, and a bounded verdict. The expectations below calibrate policy; they are not evidence of independent model/runtime validation.

## 1. Redundant derived state

```tsx
const [fullName, setFullName] = useState("");
useEffect(() => setFullName(`${firstName} ${lastName}`), [firstName, lastName]);
```

Scope: fullName has no independent editor/consumer contract; the task explicitly requires removing duplicated derived state.

Expected: confirmed requirement violation; calculate from current names during render, no automatic memo. Unresolved blocker means FAIL. Do not infer user-visible speed improvement without measuring it.

## 2. Valid external subscription

```tsx
useEffect(() => {
  function onResize() { setWidth(window.innerWidth); }
  window.addEventListener("resize", onResize);
  return () => window.removeEventListener("resize", onResize);
}, []);
```

Scope: only whether this subscription is unnecessary; setup/cleanup and initialization elsewhere are otherwise accepted.

Expected: preserve the Effect; no redundant-effect finding. A broader runtime lifecycle verdict requires its actual checks. Do not replace the subscription with a click handler or mark production duplication from StrictMode alone.

## 3. Trivial memoization

```tsx
const count = useMemo(() => rows.length, [rows]);
```

Scope: no further reference contract or specific simplification acceptance requirement.

Expected: optional simplification to rows.length, not a blocking defect or demonstrated performance regression. Static scope may PASS if all its required checks are complete.

## 4. Potentially useful memoization

```tsx
const visible = useMemo(() => expensiveFilter(rows, filter), [rows, filter]);
return <MemoizedGrid rows={visible} />;
```

Scope: real expensiveFilter and memoized consumer exist; cost is not measured in the fixture.

Expected: preserve pending consumer/workload analysis; do not blanket-delete. A request to prove an optimization remains INCOMPLETE without measurements, while a narrow structural review need not require benchmarking.

## 5. Stale memo output

```tsx
const visible = useMemo(() => rows.filter(row => row.kind === filter), [rows]);
```

Scope: filter is reactive and changes independently of rows.

Expected: confirmed stale-result defect with a filter-change trigger; correct dependencies/design. FAIL while unresolved. Do not silence dependency lint.

## 6. Conditional ordinary Hook

```tsx
function Counter({ enabled }: { enabled: boolean }) {
  if (!enabled) return null;
  const [count] = useState(0);
  return <span>{count}</span>;
}
```

Expected: confirmed ordinary Hook ordering violation when enabled changes. FAIL while unresolved; correction must preserve intended state/visibility semantics.

## 7. Allowed conditional use API

```tsx
import { use } from "react";

function Label({ enabled }: { enabled: boolean }) {
  if (!enabled) return null;
  const theme = use(ThemeContext);
  return <span>{theme.label}</span>;
}
```

Scope: installed React supports use and ThemeContext has the stated typed label contract.

Expected: no ordinary-hook-order finding. This exception does not authorize conditional useState or wrapping use in try/catch. Do not infer compiler coverage or whole-component runtime correctness.

## 8. Explicit and propagated any

```ts
function readName(value: any) { return value.name; }
const external = await response.json();
const name = external.user.name;
```

Scope: response.json is confirmed by the actual library types to return any; authored no-any policy applies.

Expected: explicit type violation and unsafe boundary flow; FAIL while unresolved. noImplicitAny alone cannot prove this safe. Validate unknown data with the actual required contract; do not use unknown-as-desired-type casts.

## 9. Safe unknown and non-code text

```ts
const help = "Do not use any unsafe values";
function isNamed(value: unknown): value is { name: string } {
  return typeof value === "object" && value !== null &&
    "name" in value && typeof value.name === "string";
}
```

Expected: no any-type finding from the string and no unsafe narrowing finding for the stated shape. This does not validate unrelated domain fields or imply compiler execution.

## 10. Incomplete and failed evidence

| Evidence | Expected overall outcome |
| --- | --- |
| No blockers; all required checks adequately PASS; P3 simplification suggestion remains | PASS with suggestion |
| Confirmed unresolved explicit-any blocker; build tool unavailable | FAIL plus build coverage gap |
| No confirmed blocker; required reviewed-file type check unavailable | INCOMPLETE |
| Requested claim of 20% speed improvement; no reproducible profiler/baseline | INCOMPLETE, no invented percentage |
| All configured lint rules pass, but relevant reviewed files were excluded | INCOMPLETE for the required uncovered checks |
| Producer says tests passed; reviewer did not inspect changed source/consumers | INCOMPLETE independent review |
| Profiling unrelated to a pure spelling change, with no performance claim and documented impact analysis | Measurement can be N/A; remaining applicable checks determine verdict |

Do not turn optional unmeasured concerns into confirmed blockers, mark unavailable tools N/A, or let a passing command erase a confirmed source violation.
