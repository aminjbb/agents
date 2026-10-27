---
name: scaffold-route
description: Add or adapt an FSD-owned SPA route with lazy page loading, public API imports, intentional pending/error boundaries, and verified registration using the installed React Router v7 or TanStack Router.
---

# Scaffold Route and Lazy Page

<inputs>

- `project_root`, bounded route path/ID, page owner/export, parent layout, and observable navigation behavior.
- Access policy: public, authenticated, or permission-scoped, obtained from actual requirements.
- Optional source root, accepted URL contract, and `mode`: `plan` for design/audit/dry run, `implement` for authorized changes.

Inspect available context before asking for essential missing decisions. Resolve all destination paths within the authorized project, including through symlinks/junctions. Reject invalid names/traversal and inspect collisions before writing.

</inputs>

<execution_steps>

## 1. Inspect the actual routing system

Read instructions, package/lockfile versions, React Router mode or TanStack registration mode, discovery plugins, route graph, aliases, stable providers, existing pages, public APIs, pending/error UI, base path, and build/test commands.

Reuse the installed router and compatible routes. Do not install a second router, upgrade versions, change routing modes, run overwrite-prone generators, or initialize a React application as a side effect. Missing infrastructure is a named prerequisite, not permission for an unrequested migration.

Inspect parent/index/dynamic/wildcard matches and route IDs for conflicts. Define unknown path and resource-not-found behavior separately. In plan mode, return the proposed registration and verification without mutation.

## 2. Assign FSD owners

Keep route registration, router instance, layouts, and wiring in application infrastructure. Keep screen implementation in its `pages` slice, exposed through root `index.ts`. Lower layers MUST NOT import application route objects, registered router types, app hooks, or siblings.

Typical code-based layout, adapted to existing conventions:

```text
src/
  app/router/
    router.tsx
    routes/product.route.tsx
    ui/RoutePending.tsx
    ui/RouteFailure.tsx
  pages/product/
    ui/ProductPage.tsx
    index.ts
```

Generate only missing files actually required by the task; reuse established shell/recovery UI. For file-based routing, keep thin discovery adapters in the configured application infrastructure and regenerate the route tree with the existing command. Do not hand-edit generated files or introduce an undocumented seventh layer.

## 3. Connect a lazy public page

Merge the explicit page export without replacing existing contracts:

```ts
// pages/product/index.ts
export { ProductPage } from "./ui/ProductPage";
```

Choose one supported mechanism, not overlapping wrappers:

- React Router v7 Declarative mode: declare `React.lazy` at module scope and place an appropriate `Suspense` plus rejection-handling error boundary in application composition.
- React Router v7 Data mode: use supported route lazy modules and router pending/error handling. Inspect the installed minor version before adopting granular lazy APIs or middleware.
- React Router Framework mode: preserve the existing SPA configuration and supported route-module splitting; do not introduce server-only code into a client SPA.
- TanStack Router: use its supported lazy route/component APIs or verified automatic splitting. Keep path matching, search validation, and required access checks available when needed.

Declarative-mode import example, inside the application adapter:

```tsx
const ProductPage = lazy(() =>
  import("@/pages/product").then(({ ProductPage }) => ({
    default: ProductPage,
  })),
);
```

Data-mode route fragment, only when this installed router supports the shown contract:

```tsx
const productRoute = {
  path: "products/:productId",
  lazy: async () => {
    const { ProductPage } = await import("@/pages/product");
    return { Component: ProductPage };
  },
};
```

Adapt parent nesting and parameter handling to the actual contract. These fragments do not implement the provider, pending/error handling, or access policy by themselves. Never import `pages/product/ui/ProductPage` from outside the slice or eagerly import the same implementation elsewhere.

## 4. Complete integration

Use [implement-route-guard](../implement-route-guard/SKILL.md) for private access and [manage-url-state](../manage-url-state/SKILL.md) for relevant URL contracts. Do not scaffold either responsibility when the route does not need it.

Keep a stable router and QueryClient at application assembly. Loader prefetching uses the owning Query contract rather than direct transport or a competing route cache. Do not call React hooks in loaders.

Provide distinct accessible states for code loading, session checking, data pending, and errors. Reuse existing recovery UI; a failed lazy chunk must not prevent its own fallback from loading. Avoid unconditional reload/retry loops.

Preserve semantic navigation, modifier-click, titles/focus/scroll behavior, base-path links, and existing consumers. Coordinate presentation with @ui-crafter. No authored inline styles, wildcard/layer barrels, invalid upward/sibling imports, or cycles. Every authored source file/component stays within 150 physical lines.

## 5. Verify actual splitting and navigation

Inspect eager imports/barrels and available production chunk evidence. Dynamic syntax alone does not prove the page is excluded from the entry bundle; do not impose an invented chunk-size threshold.

Use [audit-routing](../audit-routing/SKILL.md) in audit mode for the changed route, sharing current evidence and avoiding recursive scaffolding. Verify direct entry, nested navigation, refresh, Back/Forward, unknown routes, pending and rejected imports, and applicable guard/URL states.

Run existing relevant type/lint/test/build checks. Record unavailable browser/hosting/build coverage. A rerun must reuse compatible registration and exports rather than duplicate them.

</execution_steps>

<output_contract>

Return `CREATED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, with router/version/mode, route/page ownership, changed files/public APIs, lazy/pending/error strategy, actual checks, and remaining work. A route skeleton is not proof of completed product behavior; unresolved mandatory checks remain explicit.

</output_contract>
