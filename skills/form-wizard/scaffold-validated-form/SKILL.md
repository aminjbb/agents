---
name: scaffold-validated-form
description: Scaffold or adapt an FSD-owned typed form schema, controller, and UI using RHF with Zod by default or a justified React 19 Action strategy, with explicit draft and submission contracts.
---

# Scaffold Validated Form

<inputs>

- `project_root`, bounded form goal, owning layer/slice, fields/raw values, validation requirements, and initialization contract.
- Known parsed/payload shape, existing mutation command, and accepted completion behavior when submission is in scope.
- `mode`: `plan` for audit/design/dry run; `implement` for authorized changes.

Inspect available context before asking essential questions. Resolve paths within the authorized target, including symlinks/junctions; reject traversal and invalid names. Preserve collisions, existing implementations, and unrelated work.

</inputs>

<execution_steps>

## 1. Inspect and choose ownership

Read instructions and installed React/RHF/Zod/resolver versions, existing schemas/invariants, fields, default sources, mutations, public APIs, and tests. Reuse suitable forms/primitives rather than regenerating them.

Use RHF+Zod for complex/conditional/multi-field work by default. A simple Action-oriented React 19 form may use `useActionState` with explicit decoding/validation and input-preservation behavior. Do not migrate packages or combine two field-value/submission owners without a concrete contract.

Keep action-specific schema/controller/mapping in the owner's `model`, rendering in `ui`, and requests/mutations in `api`. Reuse entity invariants downward through public APIs. Generic fields belong to Shared, not business schemas. No sibling/upward/type cycles or imports of app store/router types.

## 2. Define the transaction before scaffolding

Specify raw input, parsed output, API payload, required/optional/conditional values, validation timing, default/baseline source, record identity, error contract, and pending/edit/reset behavior.

Use [manage-complex-form](../manage-complex-form/SKILL.md) for arrays/steps/draft complexity and [implement-form-submission](../implement-form-submission/SKILL.md) for actual submission. Missing mutation contracts must not be replaced with fake endpoints or simulated success.

In plan mode, return ownership, proposed tree/interfaces, and checks without source/package changes.

## 3. Generate only needed files

Example for an approved create-task form with a required trimmed title of at most 120 characters:

```text
src/features/create-task/
  model/
    create-task.schema.ts
    use-create-task-form.ts
  ui/
    CreateTaskForm.tsx
  index.ts
```

These domain names/limits are illustrative; substitute confirmed requirements. Do not overwrite an existing API or add unused segments.

```ts
// model/create-task.schema.ts
import { z } from "zod";

export const createTaskSchema = z.object({
  title: z.string().trim().min(1, "Enter a title").max(120),
});

export type CreateTaskInput = z.input<typeof createTaskSchema>;
export type CreateTaskValues = z.output<typeof createTaskSchema>;
```

Use supported schema APIs and actual user-language messages. When transforms change types, keep raw defaults/controls typed as input and successful submission typed as output.

```ts
// model/use-create-task-form.ts
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { createTaskSchema } from "./create-task.schema";
import type { CreateTaskInput, CreateTaskValues } from "./create-task.schema";

export function useCreateTaskForm() {
  return useForm<CreateTaskInput, unknown, CreateTaskValues>({
    resolver: zodResolver(createTaskSchema),
    defaultValues: { title: "" },
    mode: "onSubmit",
  });
}
```

This controller template establishes a local form, not a completed submission. Verify resolver/generic compatibility with installed packages; never cast around a mismatch. Adapt edit-form initialization instead of resetting on each Query change.

Implement UI using existing fields with correct registration/ref/name/value/change/blur contracts. Use Controller only where the actual controlled primitive requires it; do not register a field twice. Keep label/error/description IDs, accessible errors and focus, button types, and pending behavior explicit. Avoid nested forms and authored inline styles.

Merge deliberate public exports, for example:

```ts
// index.ts
export { CreateTaskForm } from "./ui/CreateTaskForm";
export type { CreateTaskValues } from "./model/create-task.schema";
```

Export schemas/controllers only when external consumers need them. Internal imports never use the slice's own barrel; external access uses root `index.ts`. No wildcard or layer-wide barrels.

## 4. Verify the integrated result

Verify relevant required/invalid/transformed inputs, initial defaults, repeated instances, keyboard submit, invalid focus, actual submit command/results, and preserved values on failure. No form-local Redux or server cache mirror.

Use [audit-form](../audit-form/SKILL.md) in audit mode with shared evidence. Run existing applicable type/lint/tests/build/import checks and keep each authored source file/component within 150 physical lines. Do not claim schemas compiled or UI worked without the required environment.

Reruns must reuse compatible files/contracts and avoid duplicate exports/fields. A scaffold without the accepted submission or required checks remains partial work.

</execution_steps>

<output_contract>

Return `CREATED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, with versions/strategy, owner, raw/parsed/payload contracts, files/public exports, actual verification, and remaining dependencies. Generated skeletons are not completed product behavior or final architectural acceptance.

</output_contract>
