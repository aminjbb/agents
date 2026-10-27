---
name: validate-fsd-boundaries
description: Audit React FSD source imports for layer direction, sibling-slice isolation, public API bypasses, and circular dependencies. Use for workspace audits or modified-file reviews; report findings without editing source unless fixes are separately requested.
---

# Validate FSD Boundaries

<purpose>

Produce an evidence-based architectural import audit for @architect. Default to read-only analysis. Do not rewrite source, add suppressions, or install tooling merely to make an audit pass.

</purpose>

<inputs>

- Required: workspace/project root, inferred from the current task when unambiguous.
- Scope: `workspace` by default, or explicit modified/existing file paths.
- Optional: a Git comparison base for changed-file review. Do not assume a particular default branch exists.
- Context: applicable repository instructions, source roots, FSD policy, resolver configuration, and documented Shared public boundaries.

For changed-file mode, include staged, unstaged, and relevant untracked files, plus rename/deletion effects. Build sufficient dependency context to review their consumers and detect cycles. If a requested Git base is unavailable, report it rather than substituting a misleading comparison.

</inputs>

<execution_steps>

## 1. Inventory boundaries and resolver behavior

1. Locate source files, TypeScript configs and references, Vite aliases/plugins, package exports/imports, and existing architecture tooling.
2. Exclude dependencies, build output, generated code, and vendor directories from authored-source auditing. Keep tests, stories, styles, and declarations in scope when they reference application modules.
3. Assign each source file a layer and owner. The rank order is `app=0`, `pages=1`, `widgets=2`, `features=3`, `entities=4`, `shared=5`.
4. For business layers, identify the owning slice. Respect documented slice groups: groups are organizational only and must not become a shared-code owner or public barrel.
5. `app` and `shared` have segments, not business slices. Inventory their documented public boundaries. Do not guess whether an arbitrary nested `index.ts` is a supported Shared API.
6. Treat the entry module and build/test configuration as infrastructure roots: they may bootstrap or inspect application code. Application modules must not import these roots to escape layer rules. Flag unexplained application code outside recognized layers for classification.

## 2. Extract actual module references

Use an installed parser, compiler API, or architecture analyzer appropriate to the source language. Text search may discover candidates but is not a reliable final import parser.

Collect importer location, source specifier, reference kind, resolved target, and resolution evidence for:

- Static imports, including side-effect and type-only imports.
- Named and wildcard re-exports, including type re-exports.
- Literal dynamic imports and `React.lazy` targets.
- CommonJS `require`, `require.resolve`, and TypeScript import-equals when present.
- Literal TypeScript `import()` type references and module augmentations referencing application modules.
- Stylesheet imports, CSS module composition, and other local module references supported by project tooling.
- Vite glob imports: expand finite globs with the project's glob semantics and audit every resulting application target.

Resolve using the actual application configuration, including aliases, relative paths, extensions, directory entry points, package/workspace mappings, query suffix semantics, and filesystem casing. Canonicalize symlinks to avoid duplicate graph identities or hidden boundary crossings.

Distinguish external packages, platform built-ins, static assets, virtual modules, and application files. A workspace package or package-looking alias that resolves into application source is not automatically an external dependency. Assets owned by another slice are still private unless exposed by a legitimate public contract.

Computed imports, unsupported syntax, unresolved local aliases, parser failures, or ambiguous ownership are explicit coverage gaps. Do not classify them as harmless external packages or silently skip them. A raw asset query does not make private source access legal.

## 3. Evaluate each application edge

Apply all relevant rules; an edge can violate more than one rule:

| Rule ID | Violation |
| --- | --- |
| `FSD001` | Target layer is higher than the importing layer. |
| `FSD002` | Different business slices on the same layer depend on each other, including entity `@x` references. |
| `FSD003` | An external consumer accesses a slice implementation instead of its root `index.ts`, or bypasses a documented Shared public boundary. |
| `FSD004` | A slice imports its own public barrel instead of an internal module. |
| `FSD005` | A dependency cycle exists, including type-only edges. |
| `FSD006` | A required public API is missing, uses wildcard exports, or a layer-wide/proxy barrel hides ownership. |
| `FSD007` | Source ownership or layout is incompatible with the configured six-layer model. |
| `FSD008` | Application code depends on bootstrap/configuration roots to circumvent boundaries. |

For different business slices, target rank must be greater than importer rank and the imported entry must be the target root `index.ts`. A public entry point never legalizes a forbidden layer direction.

Within the same slice, internal direct imports are allowed but self-barrel imports are forbidden. Within `app` and `shared`, cross-segment references are allowed without cycles; external access to documented Shared boundaries still uses their `index.ts`.

Explicit `.../index.ts` and directory imports are equivalent only when the actual resolver selects the same public file. A filename containing `index` does not establish a public boundary. Inspect re-export edges as well as consumer edges to detect laundering of dependencies.

## 4. Inspect the graph

Construct a canonical directed file graph containing value and type dependencies. Include all relevant source context, not just changed files.

Run a cycle algorithm such as strongly connected components. Report self-loops and components with multiple vertices, including a concrete closed import path. Cycles hidden inside slices, public barrels, Shared, or initialization still fail.

In changed-file mode, inspect incoming consumers after public API changes and deleted/renamed targets. Report findings as introduced, pre-existing, or baseline-unknown only when the comparison evidence supports that classification. Never present a partial audit as a whole-workspace result.

## 5. Report actionable evidence

For each finding provide:

- Stable rule ID and severity `error` for confirmed mandatory violations.
- Importer path, line, and column when available.
- Original specifier and resolved target.
- Source and target layer/slice or public boundary.
- Explanation of the violation.
- A compliant remedy based on ownership, composition, or public API access.
- A cycle path when relevant.

Examples:

```text
ERROR FSD001 entities/product/model/product.ts:4:1
  imports: @/features/add-to-cart
  reason: entities cannot depend on features
  remedy: move interaction orchestration to features or a higher composition

ERROR FSD003 pages/catalog/ui/CatalogPage.tsx:3:1
  imports: @/entities/product/model/types
  remedy: export required types from entities/product/index.ts;
          consume @/entities/product after checking contract suitability
```

Do not recommend moving business types into Shared merely to eliminate an error.

</execution_steps>

<output_contract>

Return a Markdown report with:

1. Status: `PASS`, `FAIL`, or `INCOMPLETE`.
2. Scope: roots, selected files/comparison base, graph coverage, exclusions.
3. Findings: ordered by rule and file location, with counts and remedies.
4. Coverage gaps: unresolved references and unsupported analysis.
5. Verification: actual tools/commands, outcomes, and remaining work.

`FAIL` means at least one confirmed violation; still list all coverage gaps. `INCOMPLETE` means no confirmed violation but insufficient evidence for a pass. `PASS` requires no violations and complete coverage of the declared scope. If a real executable wrapper exists, use exit codes 0/1/2 respectively; do not claim a Markdown-only audit emitted an exit code.

This skill audits boundaries and cycles. It does not establish compliance with the 150-line rule, UI transport restrictions, state ownership, accessibility, or functional behavior. Report those separately if observed; never equate boundary PASS with full architectural approval.

</output_contract>
