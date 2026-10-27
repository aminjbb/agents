---
name: scaffold-slice
description: Scaffold a new feature or entity slice with ui, model, api, lib segments and an explicit index.ts public API in a React TypeScript FSD project. Use for new slices, not existing-slice replacement or implementation of unspecified business behavior.
---

# Scaffold Slice

<purpose>

Create a minimal, compilable slice skeleton with explicit ownership and a public API. This skill intentionally creates the four requested segments even before they contain implementation. It does not invent business state, validation, endpoints, or dependencies.

</purpose>

<inputs>

- Required: `project_root` and `slice_type`, exactly `features` or `entities`.
- Required: `slice_name`, for example `auth`, `add-to-cart`, or `product`.
- Optional: `source_root`, inferred from the existing project before defaulting to `src`.
- Optional: `dry_run`, default `false`.

The generated component name is the PascalCase slice name followed by `Scaffold`, such as `AddToCartScaffold` or `ProductScaffold`. This makes its incomplete status explicit and avoids reserving a real domain component name prematurely.

</inputs>

<execution_steps>

## 1. Validate ownership and paths

1. Inspect applicable instructions, source layout, React/TypeScript settings, naming conventions, and relevant public boundaries.
2. Confirm the target is a React TypeScript application. Do not initialize a framework or install dependencies as a side effect.
3. Check semantic placement: features represent actions; entities represent business concepts. Flag a clearly misplaced request and propose the correct owner before scaffolding it.
4. Validate `slice_name` against `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`. Reject separators, traversal, whitespace, absolute paths, reserved filesystem names, and invalid platform filenames. Do not silently rename the user's input.
5. Derive PascalCase deterministically by capitalizing each hyphen-separated token and concatenating. Append `Scaffold` for the component identifier and filename. Confirm the resulting identifier is valid TypeScript.
6. Resolve every destination to an absolute path inside the intended source layer, including any symlink/junction target. Reject paths that escape it.
7. Inspect case-insensitive collisions and every existing target file before writing. Reuse identical scaffold content. If nonidentical files exist, do not overwrite or merge exports automatically: report the collision and leave the slice unchanged. Work on an existing implementation requires an explicit edit task.

## 2. Generate the exact skeleton

For `slice_type=features` and `slice_name=auth`, create:

```text
src/features/auth/
  ui/
    AuthScaffold.tsx
  model/
    .gitkeep
  api/
    .gitkeep
  lib/
    .gitkeep
  index.ts
```

For `slice_type=entities` and `slice_name=product`, create:

```text
src/entities/product/
  ui/
    ProductScaffold.tsx
  model/
    .gitkeep
  api/
    .gitkeep
  lib/
    .gitkeep
  index.ts
```

Substitute the validated source root, layer, slice, and component name. Each `.gitkeep` is an empty file preserving an intentionally empty segment in version control. Do not create fake domain types, empty stores, unused clients, or segment barrels.

Generate `ui/AuthScaffold.tsx` using this template, replacing both component identifiers for other slice names:

```tsx
/** Structural placeholder; implements no user-facing behavior. */
export function AuthScaffold() {
  return null;
}
```

Use the existing JSX runtime convention; add a React import only if required by the project's compiler/lint settings.

Generate the root `index.ts`:

```ts
export { AuthScaffold } from "./ui/AuthScaffold";
```

Do not wire the placeholder into production routes or screens. Do not claim that authentication, a product view, or any other domain behavior is implemented. Replace or remove the placeholder in the later implementation task and review any public-contract change.

## 3. Preserve the architecture

- Only the root `index.ts` is the slice's external entry point.
- Internal implementation imports use relative paths, never the slice's own barrel.
- No sibling-slice or upward dependencies; entity cross-references are forbidden under this project's policy.
- UI remains in `ui`, state and behavior in `model`, request functions in `api`, private supporting utilities in `lib`.
- Keep every authored source file and component within 150 physical lines.
- Do not add network calls, runtime initialization, wildcard exports, or packages.
- Remove a segment's `.gitkeep` when a later implementation adds meaningful tracked content; do not remove another developer's files.

## 4. Verify idempotence and compilation

1. Inspect the tree and generated source, including exact export names and import targets.
2. Check paths for duplicates and ensure no unrelated file changed.
3. Use available boundary/cycle analysis and existing applicable TypeScript, lint, and build commands. Distinguish a scaffold's checks from a complete application audit.
4. A repeated request with identical inputs must produce no changes. Missing scaffold files may be added only when all existing destinations match the expected skeleton; a changed implementation is a collision, not permission to regenerate.
5. In dry-run mode, list planned content and checks without writing files.

</execution_steps>

<output_contract>

Return `CREATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, the normalized target path, exact file tree, public export, checks actually executed and their outcomes, and any collision or remaining work. State explicitly that the generated component is an inert scaffold rather than implemented product behavior.

</output_contract>
