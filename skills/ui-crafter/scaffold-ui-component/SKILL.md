---
name: scaffold-ui-component
description: Create or extend a focused typed React UI component in its correct FSD owner, reusing project primitives and preserving semantic, responsive, ref, and public API contracts.
---

# Scaffold UI Component

<inputs>

- Target `project_root`, component responsibility/name, owning layer/slice, required props, and observable behavior.
- Existing design/interaction contract or references when applicable; infer routine conventions from the repository.
- Optional `source_root` and `dry_run` (default false). A dry run writes nothing.

Resolve targets independently of the skill package. Validate identifiers, platform filenames, and canonical destinations, including symlinks/junctions; reject traversal and escapes from the authorized source root.

</inputs>

<execution_steps>

## 1. Establish reuse and ownership

1. Read applicable instructions and inspect actual React/Tailwind versions, primitives, class helpers, tokens, public boundaries, and relevant consumers.
2. Search for an equivalent before creating a new component. Extend a compatible existing contract instead of duplicating it. Preserve customized source and unrelated changes; inspect collisions rather than overwriting files.
3. Place business-independent primitives at the documented `shared/ui` module boundary. Entity/action UI belongs to the owning entity/feature, large justified compositions to widgets, and screen-specific composition to pages. Do not move domain logic into Shared to legalize an import.
4. For supplied designs use [interpret-design-context](../interpret-design-context/SKILL.md); for new or materially changed behavior use [define-interaction-contract](../define-interaction-contract/SKILL.md). Reuse current evidence and accepted decisions.

## 2. Define the component contract

Specify semantic element/primitive, native props, supported variants, local versus externally controlled state, events, ref behavior, and required visible states. Avoid contradictory flags and unrestricted prop bags.

Preserve meaningful native attributes, keyboard semantics, and accessible naming. Use the installed React version's supported ref pattern when consumers/primitives require a ref; do not introduce `forwardRef` or ref-as-prop assumptions blindly.

No authored inline styles, UI transport, global store creation, duplicated validation, or server-state ownership. Shared UI accepts values/callbacks and does not import business hooks. Query/model integrations in higher UI use approved slice APIs.

## 3. Generate only necessary files

Example structure for an approved generic field wrapper:

```text
src/shared/ui/text-field/
  TextField.tsx
  index.ts
```

For a business slice, place the implementation under its `ui/` and merge exports into its root `index.ts`; do not create a competing nested external entry point. Add variant/style/hook files only when their responsibilities warrant extraction.

The following template illustrates accessibility and prop typing; adapt token names, class-helper path, and base control to the actual project. Reuse its Input primitive if one exists. This wrapper displays provided errors; it does not validate or submit a form.

```tsx
import { useId } from "react";
import type { ComponentPropsWithoutRef, ReactNode } from "react";
import { cn } from "@/shared/lib/classnames";

type NativeInputProps = Omit<
  ComponentPropsWithoutRef<"input">,
  "style" | "aria-invalid"
>;

export type TextFieldProps = NativeInputProps & {
  label: ReactNode;
  hint?: string;
  error?: string;
};

export function TextField({
  id,
  label,
  hint,
  error,
  className,
  "aria-describedby": externalDescription,
  ...props
}: TextFieldProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const hintId = `${inputId}-hint`;
  const errorId = `${inputId}-error`;
  const describedBy = [
    externalDescription,
    hint ? hintId : undefined,
    error ? errorId : undefined,
  ].filter(Boolean).join(" ") || undefined;

  return (
    <div className="grid gap-2">
      <label htmlFor={inputId} className="text-sm font-medium">{label}</label>
      <input
        {...props}
        id={inputId}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className={cn(
          "w-full min-w-0 rounded-md border border-input bg-background px-3 py-2",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className,
        )}
      />
      {hint && <p id={hintId} className="text-sm text-muted-foreground">{hint}</p>}
      {error && <p id={errorId} className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
```

The example helper import must resolve to a documented Shared `index.ts`; do not invent that module or add a deep import. Public usage must not supply a `style` override. For this field contract, use visible label text as the naming source; callers must not replace it with a contradictory accessible name. Add ref support when the actual focus/form contract requires it.

```ts
// shared/ui/text-field/index.ts
export { TextField } from "./TextField";
export type { TextFieldProps } from "./TextField";
```

Use explicit exports and merge without erasing others. No layer-wide barrels, wildcard exports, self-barrel imports, upward/sibling dependencies, or type cycles.

## 4. Verify and finish

Every authored source file/component stays within 150 physical lines. Check actual native/form events, ID uniqueness across instances, valid error/description references, required refs, local control ownership, and disabled/pending behavior where applicable.

Execute [audit-responsive-accessibility](../audit-responsive-accessibility/SKILL.md) for relevant component states and existing applicable type/lint/build/interaction checks. For reference-driven work also use [verify-design-implementation](../verify-design-implementation/SKILL.md); share evidence rather than repeating identical checks.

Do not install a new testing stack for a small scaffold or claim visual/keyboard verification without tools. Report unavailable required coverage. Repeated execution must not duplicate components or exports.

</execution_steps>

<output_contract>

Return `CREATED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, with target owner, files, public props/exports, actual verification and remaining work. A generated component is not proof of a verified screen; unresolved mandatory checks prevent a completion claim.

</output_contract>
