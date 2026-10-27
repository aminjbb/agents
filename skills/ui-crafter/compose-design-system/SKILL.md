---
name: compose-design-system
description: Compose or extend existing UI primitives, semantic tokens, and typed variants using Tailwind and the installed Shadcn/Radix stack without duplicating the design system or breaking interaction contracts.
---

# Compose Design System

<inputs>

- Target project, bounded component/pattern request, existing design references or interaction contract.
- Required visual/interaction variants and supported themes, directions, and devices.
- Mode `analyze`, `implement`, or `dry_run`, following the assigned task. Analysis and dry run do not mutate source.

</inputs>

<execution_steps>

## 1. Inventory the real system

Read instructions and inspect tokens, global styles, Tailwind major/configuration, component exports, variant/class helpers, icons, installed primitives, customized Shadcn source, and existing usage.

Confirm the underlying implementation rather than assuming every Shadcn component uses Radix. Inspect source and installed API types before choosing wrappers or composition props. Resolve task paths within the authorized project, preserving customized and uncommitted work.

## 2. Map requirements to existing capabilities

Map each requested state to an existing primitive, variant, semantic token, and public entry point. Distinguish visual choices from interaction behavior.

Use [interpret-design-context](../interpret-design-context/SKILL.md) for external references and [define-interaction-contract](../define-interaction-contract/SKILL.md) for materially new behavior. Reuse current task artifacts.

Choose, in order: reuse an existing component, extend a compatible variant, compose existing primitives, or add a new focused primitive only when needed. Do not introduce a parallel Button/Dialog family or install another library for cosmetic differences.

In analysis/dry-run mode, return the mapping and proposed changes before source mutation. A missing design tool does not prevent inspecting existing code; disclose the reference limitation.

## 3. Implement bounded variants and tokens

- Use semantic project tokens for backgrounds, foregrounds, borders, focus, spacing, typography, radius, and elevation. Verify supported light/dark and disabled/error states.
- Use the existing variant library/helper when present. Do not install one merely to express a small finite class map.
- Use complete statically discoverable Tailwind classes. No runtime class fragments, authored `style` props, CSS-variable style objects, DOM style writes, or injected styles as bypasses.
- Keep responsive and primitive state selectors consistent with the installed Tailwind/primitive version. Do not migrate Tailwind configuration as a side effect.
- Scope justified custom CSS to the owner. Arbitrary values need a real requirement; repeated cross-component values warrant an intentional token decision.
- Do not change a global token to fix one local component. For a genuine shared-token change, inspect all affected consumers and verification scope before editing.

Example bounded class map, only where the project has no existing variant helper. Adapt semantic tokens and names to the actual system:

```ts
export type ActionTone = "primary" | "secondary";
export type ActionSize = "sm" | "md";

const toneClasses = {
  primary: "bg-primary text-primary-foreground hover:bg-primary/90",
  secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
} satisfies Record<ActionTone, string>;

const sizeClasses = {
  sm: "min-h-9 px-3 text-sm",
  md: "min-h-11 px-4 text-base",
} satisfies Record<ActionSize, string>;

export function actionVariantClasses(tone: ActionTone, size: ActionSize) {
  return [toneClasses[tone], sizeClasses[size]].join(" ");
}
```

This map is a visual-contract example, not a reason to generate a new Button. The component still needs the actual project's base, focus, disabled, and pending behavior. Ensure the installed TypeScript version supports used syntax; do not cast away variant errors.

## 4. Preserve primitive behavior

- Preserve titles, descriptions, accessible names, trigger semantics, keyboard models, portals, and focus restoration.
- Verify supported `asChild`/composition requirements: child count/type, props, event composition, refs, and default prevention.
- Avoid nested interactive elements and wrappers that swallow native attributes or event handlers.
- Keep controlled/uncontrolled contracts explicit; do not mirror a primitive's state unnecessarily.
- Preserve dependency-internal positioning styles. The no-inline policy still applies to authored project code, including copied/customized source; report concrete conflicts instead of stripping required behavior or silently exempting it.
- Shared primitives must not import business data/stores. Compose domain behavior in its owning FSD slice and expose it through the root `index.ts`.

## 5. Verify consumers and evidence

Inspect impacted usage, public contracts, finite variant combinations and meaningful compound states, supported themes, long labels, refs, and overlays. Keep source/component files within 150 physical lines and dependency graphs acyclic.

Use [audit-responsive-accessibility](../audit-responsive-accessibility/SKILL.md) for the affected system surface. Use [verify-design-implementation](../verify-design-implementation/SKILL.md) when comparing a supplied reference. Reuse matching evidence and rerun checks only when changes invalidate it.

Run applicable existing type checks, lint, interaction tests, and build. Never overwrite customized files via generators, suppress failures, or claim a library guarantees the composition is accessible.

</execution_steps>

<output_contract>

Return `ANALYZED`, `COMPOSED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, with reuse mapping, changed tokens/variants/public contracts, affected consumers, actual checks, and unresolved gaps. `COMPOSED` requires implemented work and applicable verification; it is not final architectural approval.

</output_contract>
