---
name: refactor-spaghetti-state
description: Audit and refactor effect-based requests, duplicated server state, coupled local transitions, and relay-only prop chains into exclusive FSD state ownership.
---

# Refactor Spaghetti State

## Inputs and scope

- `project_root`, bounded `target_files` or source area, and expected product behavior.
- `mode`: `analyze` for audits/design/dry runs; `refactor` only for authorized implementation.
- Read applicable instructions and inspect packages, providers, contracts, and existing tests. Keep the instruction package and target project roots separate.
- Preserve unrelated and uncommitted work. Do not invent endpoints or business behavior. Missing essentials block dependent changes, not independent analysis.

## 1. Audit the actual dataflow

Use text search for discovery, then inspect syntax and resolved imports; keyword matches alone are not proof.

- [ ] Find `useEffect` callbacks invoking `fetch`, Axios, SDKs, or helpers that perform requests. Follow renamed imports, wrappers, and indirect calls.
- [ ] Find component/presentation-hook transport, manual data/loading/error triples, Redux fetching thunks, and query results copied into stores.
- [ ] Trace every affected `useState`/`useReducer`, setter, effect, selector, subscription, timer, and persistence path.
- [ ] Identify coupled setters, contradictory booleans, redundant derived values, stale closures, and missing cleanup. Many independent local values alone do not prove a problem.
- [ ] Follow prop chains to their real consumers. Distinguish meaningful parent-child props from components forwarding unrelated state/commands unchanged.
- [ ] Record file locations, producers, consumers, request identity, expected behavior, existing failures, and ownership violations.

Problematic request pattern:

```tsx
useEffect(() => {
  fetch(`/api/products/${productId}`)
    .then((response) => response.json())
    .then(setProduct);
}, [productId]);
```

This example is a detection target, not production boilerplate. Hiding the same request in a local custom hook does not correct ownership.

## 2. Assign one authoritative owner per fact

| Fact | Mechanism | Placement |
| --- | --- | --- |
| Remote data and request status | TanStack Query v5 | Owning slice `api/` |
| Client-owned cross-screen/workflow state | RTK | Owning slice `model/` |
| Isolated UI values and local transitions | `useState`, `useReducer`, local hook | Nearest UI owner |
| Computable facts | Calculation/selector | Computation owner |
| URL-authoritative values | Existing router contract | Route composition |

Separate fetched records from selected IDs, URL parameters, and open menus. A draft is a distinct editing transaction with initialization, dirty tracking, save/cancel, and conflict semantics; it must not become a synchronized server mirror. Never put authoritative server records/status in Redux or duplicate one authoritative fact across mechanisms.

## 3. Plan before mutation

- [ ] Define owners, lifetimes, reset conditions, query keys, API hooks, reducer transitions, local interfaces, and affected consumers.
- [ ] Define cancellation, error behavior, cache reconciliation, identity changes, and draft preservation where relevant.
- [ ] Keep cross-slice imports strictly downward: `app → pages → widgets → features → entities → shared`. No sibling-slice dependencies or upward type imports.
- [ ] Use root `index.ts` public APIs. Lower layers must not import application `RootState`, typed hooks, or the assembled store; use slice-owned contracts and higher composition.
- [ ] Return proposed boundary/public-contract changes to @architect. Delegate only when authorized and collaborators are available.
- [ ] In `analyze` mode, return findings and the plan now. Do not mutate source, install packages, auto-fix, or generate application output.

## 4. Execute the matching migration

### A. Direct requests or server mirrors

1. Read [scaffold-query-hook.md](scaffold-query-hook.md) and apply its procedure to create or adapt the owning API contract. Reuse existing canonical queries rather than generating duplicates.
2. Preserve the real endpoint/payload, validate unknown responses, forward cancellation, and derive keys from all response-defining inputs.
3. Replace request effects and manual flags with the exported hook. Update consumers without conditional hook calls.
4. Remove superseded Redux/local cache copies and request subscriptions. Keep genuinely separate client intent and owned drafts.
5. For writes, define a v5 `useMutation` hook in `api/`, targeted reconciliation, and rollback/concurrency behavior if optimism is required. Do not treat a write as a query or automatically retry unsafe mutations.

Example higher-layer consumer after implementing the approved product query contract:

```tsx
import { useProductQuery } from "@/entities/product";
import type { ProductDetailInput } from "@/entities/product";

export function ProductSummary(props: ProductDetailInput) {
  const query = useProductQuery(props);
  if (query.isPending) return <p role="status">Loading product…</p>;
  if (query.isError) return <p role="alert">Could not load product.</p>;
  return <p>{query.data.name}</p>;
}
```

This minimal example assumes valid known identity and a non-null product response. Adapt empty/background/error behavior to the real screen. Render the consumer only when prerequisites are known; never call hooks conditionally within a component.

### B. Global client state

1. Prove client authority and cross-screen/workflow lifetime.
2. Read [scaffold-redux-slice.md](scaffold-redux-slice.md); create or adapt an RTK model, public exports, and application registration.
3. Replace duplicated owners with narrow selectors/actions. Keep server status and isolated local controls out of the model.

### C. Tangled local state and prop drilling

1. Keep independent local values local. Replace coupled flags with explicit states or a local reducer when justified.
2. Derive totals, filtered data, and validity instead of synchronizing copies through effects.
3. Move state to its nearest common owner, use composition, or let a real consumer access the approved query contract. Repeated query observers share the canonical cache.
4. Use RTK only for genuine global client facts, never merely to eliminate props. Do not invent a business Context/global singleton to bypass the rule.
5. Extract cohesive UI/hooks instead of relocating a tangled component unchanged. Preserve form edits and relevant accessibility; coordinate form contracts with @form-wizard when available.

## 5. Complete the transition

- [ ] Update affected consumers and remove obsolete effects, setters, requests, forwarding props, subscriptions, and dead exports.
- [ ] Ensure old/new request paths are not active together and submissions are not duplicated.
- [ ] Preserve legitimate non-fetching external-system effects and cleanup.
- [ ] Keep source files/components at most 150 physical lines and graphs acyclic, including type edges.
- [ ] Do not weaken lint/compiler checks or perform unrelated package upgrades.

## 6. Verify and report

- [ ] Test relevant pending/error/empty/success/background states, query identity across parameters, shared consumers, and cancellation with controlled requests and isolated QueryClients.
- [ ] Verify mutation reconciliation, applicable optimistic recovery, draft preservation, local/client transitions, reset behavior, and resource disposal.
- [ ] Confirm no UI transport, server cache in Redux, duplicated authority, broken public API, or relay-only chain remains in the assigned scope.
- [ ] Read [validate-fsd-boundaries](../validate-fsd-boundaries/SKILL.md) before boundary auditing. Its PASS covers imports/cycles, not state correctness.
- [ ] Run applicable existing type checks, lint, tests, and build in refactor mode. Report missing coverage and pre-existing failures; never invent a passing check.

Return `ANALYZED`, `REFACTORED`, or `BLOCKED`, mode/scope, findings with locations, before/after ownership, public-contract changes, changed files, executed checks/results, and remaining work. `REFACTORED` requires completed migration and applicable verification; it does not replace @architect's acceptance. A rerun on compliant unchanged code must not manufacture new changes.
