---
name: scaffold-query-hook
description: Create strictly typed TanStack Query v5 read hooks, canonical query keys, request functions, and public exports inside an owning FSD slice's api segment.
---

# Scaffold Query Hook

## Inputs

- `project_root`, owning `layer`/`slice_name`, operation, and confirmed request/response contract.
- Optional `source_root` and `dry_run` (default false).
- Inspect repository instructions, installed Query v5, aliases, transport, provider, and existing keys before writing. Resolve the target independently of this file's location.

## Execution rules

1. Confirm remote authority and ownership. Reuse an existing resource query instead of introducing a competing cache. Do not invent an endpoint or copy the example domain into an unrelated task.
2. Validate names and canonical destination paths, including junctions/symlinks. Reject traversal and collisions. Reuse identical files; preserve nonidentical existing implementations and merge only changes authorized by the task.
3. Place all files below in the owner's `api/`. Cross-slice imports use root `index.ts` and point strictly downward. No sibling-slice imports, upward type imports, own-barrel imports, or cycles.
4. Use keys shaped as `[layer, slice, scope, operation, parameters]` with optional extra hierarchy levels. Include all non-secret response-defining values. Follow an existing compatible canonical factory rather than renaming live keys without migration.
5. Scope private data by account/tenant when applicable; never include tokens. Keep list, detail, and infinite keys distinct. Normalize parameters once and use the same values in the key and request.
6. Use strict types and validate unknown responses. No `any`, unchecked response casts, non-null assertions, query-result copies in Redux, or manual UI request flags.
7. Use a stable application QueryClient/Provider. Never create a client in this hook. Components call the exported hook without `useEffect` fetching.

## Exact example tree

For an approved product detail contract `GET /api/tenants/:tenantId/products/:productId` returning `{ id: string, name: string }`:

```text
src/entities/product/
  api/
    product.types.ts
    product.keys.ts
    get-product.ts
    product.options.ts
    use-product-query.ts
  index.ts
```

Adapt the contract and names to inspected requirements. Reuse existing domain types through legal internal imports instead of redeclaring them.

### api/product.types.ts

```ts
export type Product = Readonly<{ id: string; name: string }>;

export type ProductDetailInput = Readonly<{
  tenantId: string;
  productId: string;
}>;
```

### api/product.keys.ts

```ts
import type { ProductDetailInput } from "./product.types";

export const productKeys = {
  all: ["entities", "product"] as const,
  tenant: (tenantId: string) =>
    [...productKeys.all, { tenantId }] as const,
  detail: (input: ProductDetailInput) =>
    [...productKeys.tenant(input.tenantId), "detail", input.productId] as const,
};
```

### api/get-product.ts

Use the existing `shared/api` transport when available, adapting its actual signature while preserving cancellation, HTTP errors, and decoding. This self-contained template uses fetch only inside `api/`; do not introduce a competing transport abstraction.

```ts
import type { Product, ProductDetailInput } from "./product.types";

function isProduct(value: unknown): value is Product {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value && typeof value.id === "string" &&
    "name" in value && typeof value.name === "string"
  );
}

export async function getProduct(
  input: ProductDetailInput,
  signal: AbortSignal,
): Promise<Product> {
  if (!input.tenantId.trim() || !input.productId.trim()) {
    throw new Error("Product identity is required");
  }
  const tenant = encodeURIComponent(input.tenantId);
  const product = encodeURIComponent(input.productId);
  const response = await fetch(`/api/tenants/${tenant}/products/${product}`, {
    signal,
  });
  if (!response.ok) {
    throw new Error(`Product request failed (${response.status})`);
  }
  const data: unknown = await response.json();
  if (!isProduct(data) || data.id !== input.productId) {
    throw new Error("Invalid product response");
  }
  return data;
}
```

### api/product.options.ts

```ts
import { queryOptions } from "@tanstack/react-query";
import { getProduct } from "./get-product";
import { productKeys } from "./product.keys";
import type { ProductDetailInput } from "./product.types";

export function productDetailOptions(input: ProductDetailInput) {
  const identity = { ...input };
  return queryOptions({
    queryKey: productKeys.detail(identity),
    queryFn: ({ signal }) => getProduct(identity, signal),
  });
}
```

### api/use-product-query.ts

```ts
import { useQuery } from "@tanstack/react-query";
import { productDetailOptions } from "./product.options";
import type { ProductDetailInput } from "./product.types";

export function useProductQuery(input: ProductDetailInput) {
  return useQuery(productDetailOptions(input));
}
```

Let Query infer data/error/result types, preserving any project's registered error type. Do not broaden the return to `unknown` or force an incompatible `UseQueryResult` cast.

### index.ts — merge explicit public exports

```ts
export { useProductQuery } from "./api/use-product-query";
export { productDetailOptions } from "./api/product.options";
export { productKeys } from "./api/product.keys";
export type { Product, ProductDetailInput } from "./api/product.types";
```

Export options/keys only when consumers need them. Keep raw requests private unless their external use is justified. Never replace existing exports or use `export *`.

## Verification and output

- Required parameters must be known before rendering the querying consumer; never call hooks conditionally. For optional prerequisites, design an explicit v5-compatible disabled-query contract without non-null assertions or sentinel resource IDs.
- Select retry/freshness policies from product requirements and the existing transport's typed errors. The template inherits application defaults; do not silently invent retry exclusions or infinite freshness.
- Verify distinct inputs, shared consumers, unsuccessful HTTP responses, invalid payloads, cancellation, and pending/error/empty/background UI where relevant. Use isolated clients and controlled requests, not a live endpoint.
- Run applicable existing type checks, lint, build, and boundary/cycle checks. Every generated source file must stay within 150 physical lines.
- Report `CREATED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`; include files, public contracts, key structure, actual checks, and gaps. Dry runs write nothing. Repeat runs must not duplicate exports or keys.

Reference: [TanStack Query options](https://tanstack.com/query/v5/docs/framework/react/guides/query-options).
