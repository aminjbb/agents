---
name: manage-url-state
description: Define or implement validated typed path/search contracts, canonical serialization, safe history updates, and Query input integration while preserving URL ownership in a React SPA.
---

# Manage URL State

<inputs>

- Target project, bounded routes, parameters and intended shareable behavior.
- Existing router/version/mode, query inputs, supported unrelated parameters, and history policy.
- `mode`: `plan` for audits/design/dry runs; `implement` for authorized changes.

Inspect actual requirements before choosing defaults. Reject unsafe destination paths, preserve unrelated work, and avoid a new schema dependency when existing tools or a small codec suffice.

</inputs>

<execution_steps>

## 1. Assign authority and parameter ownership

URL owns committed shareable navigation/filter facts; Query owns remote results; RTK owns justified global client intent; isolated UI and explicit uncommitted edit buffers remain local. Never mirror the same committed fact continuously across these stores.

For each path/search/hash value define type, default, bounds/enum, missing/empty/invalid behavior, repeated-key policy, encoding, canonical representation, push/replace behavior, and effect on dependent values such as pagination.

Keep screen-specific codecs in the page and export required contracts through its root `index.ts`. Put genuinely reusable domain-neutral helpers at documented Shared boundaries. Application adapters consume page contracts; pages never import the app router or sibling page types. Maintain acyclic downward dependencies.

## 2. Build one parse/serialize contract

Treat URL values as unknown input. Reuse installed validation tools or native parsing with strict types; no unchecked route casts or non-null assertions. For TanStack Router use its actual search/path validation APIs and loader dependencies; for React Router validate raw params/search at the responsible boundary.

Example only for an approved catalog contract: `page` is 1..10000 (default 1), `sort` is newest/price (default newest), and `q` is trimmed to 100 characters. Repeated owned keys read their first value and collapse to one canonical value on write. Unrelated supported keys are preserved.

```ts
export type CatalogSearch = Readonly<{
  page: number;
  sort: "newest" | "price";
  q: string;
}>;

export function parseCatalogSearch(params: URLSearchParams): CatalogSearch {
  const rawPage = params.get("page") ?? "";
  const numericPage = /^[1-9]\d*$/.test(rawPage) ? Number(rawPage) : 1;
  const page = Number.isSafeInteger(numericPage) && numericPage <= 10000
    ? numericPage
    : 1;
  return {
    page,
    sort: params.get("sort") === "price" ? "price" : "newest",
    q: (params.get("q") ?? "").trim().slice(0, 100),
  };
}

export function writeCatalogSearch(
  current: URLSearchParams,
  patch: Partial<CatalogSearch>,
): URLSearchParams {
  const result = new URLSearchParams(current);
  if (patch.page !== undefined) result.set("page", String(patch.page));
  if (patch.sort !== undefined) result.set("sort", patch.sort);
  if (patch.q !== undefined) result.set("q", patch.q);
  const next = parseCatalogSearch(result);
  for (const key of ["page", "sort", "q"]) result.delete(key);
  if (next.page !== 1) result.set("page", String(next.page));
  if (next.sort !== "newest") result.set("sort", next.sort);
  if (next.q) result.set("q", next.q);
  return result;
}
```

Do not copy these sample bounds or truncation into a product whose contract differs. Normalization must be deliberate and visible where it affects user intent. URLSearchParams is the raw string-based example, not a reason to replace TanStack Router's existing typed serializer.

Do not place credentials, tokens, private records, or large drafts in URL parameters. Explicitly decide which unrelated keys are supported; preservation is not authorization to propagate secrets or arbitrary return destinations.

## 3. Wire history and consumers

Use the router's supported search/navigation API. Update against the latest relevant location and preserve supported unrelated keys; do not mutate shared URLSearchParams instances or call window.history behind the router.

Use push for meaningful committed history and replace for the specified transient/canonicalization behavior. Normalize only when needed; ensure an already canonical URL causes no redirect/update loop.

Define filter-to-page reset explicitly, such as applying `{ q: nextQuery, page: 1 }` in one update. A local input buffer has an explicit commit/cancel contract; it is not another authoritative committed filter.

Cancel or invalidate debounced callbacks on navigation/unmount as appropriate. A late callback must not overwrite newer Back/Forward navigation, route identity, or another parameter update.

Derive Query keys/options and relevant loader dependencies from the same validated values. Reuse @state-master's exported API rather than constructing a second result cache or fetch effect.

In plan mode, return schemas, examples, ownership/history policy, and integration changes without writing source.

## 4. Verify round trips and navigation

- Test defaults, valid/invalid bounds, repeated keys, enums, Unicode/encoded text, missing/empty values, and the real contract's array semantics.
- Test parse/write round trips, deterministic normalization, and canonicalization idempotence.
- Confirm supported unrelated keys survive, owned repeated keys normalize, and the input object is not mutated.
- Verify direct links, refresh, bookmarks/new tabs, Back/Forward, atomic filter/page updates, and debounced stale updates using available browser/history fixtures.
- Confirm Query inputs match the visible URL and no Redux/local committed mirror remains.

Use [audit-routing](../audit-routing/SKILL.md) for relevant integration checks in audit mode. Run existing applicable type/lint/tests/build and import checks; maintain public APIs, no cycles, and the 150-line source/component ceiling. Share evidence rather than repeatedly invoking skills.

</execution_steps>

<output_contract>

Return `IMPLEMENTED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, with parameter schema/ownership, canonical examples, history behavior, Query integration, changed files, actual verification, and remaining gaps. A passing codec test alone does not prove browser history or refresh behavior.

</output_contract>
