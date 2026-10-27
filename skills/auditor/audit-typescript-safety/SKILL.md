---
name: audit-typescript-safety
description: Audit authored TypeScript for explicit or implicit any, unsafe value propagation/assertions, unvalidated external boundaries, and public contract mismatches using effective compiler and type-aware lint evidence.
---

# Audit TypeScript Safety

<inputs>

- Target project and bounded files/diff with relevant type/API consumers.
- Effective tsconfig references, installed TypeScript/lint/schema tools, and accepted domain contracts.
- `mode`: `audit` default; `fix` only for authorized corrections.

</inputs>

<execution_steps>

## 1. Establish real coverage

Read instructions, app/build/test tsconfigs, project references/include/exclude, compiler settings, declaration sources, lint parser/project configuration, and actual package versions.

Confirm the reviewed files are included in the intended compiler/type-aware checks. A solution config with references, a transpile-only bundler, or a passing unrelated tsconfig does not establish type safety for these files.

Inspect strict/noImplicitAny/nullability and lint coverage. noImplicitAny detects some implicit any, not explicit any or all any-valued external APIs. No source/config edits, dependency installation, or new suppressions in audit mode.

## 2. Trace unsafe types, not words

Use installed compiler/type-aware tooling where available. Text search may locate candidates but must not report comments, strings, prose, vendor declarations, or identifiers containing any as authored type violations.

Check explicit any in aliases, assertions, signatures, callbacks, generic constraints/defaults, containers, and declarations. Check inferred/propagated any at JSON/library boundaries and its subsequent assignments, calls, member access, arguments, and returns.

The authored no-any rule also applies to tests and local ambient declarations; mocks are not an automatic exemption. Dependency-generated any is external evidence to contain, not permission to propagate unsafely or rewrite node_modules.

## 3. Check meaningful boundary validation

- Unknown external API, URL, storage, event, and FormData values require an explicit validated/narrowed contract before meaningful use.
- Replacing any with unknown is only a boundary improvement; unchecked assertions afterward do not complete validation.
- Review unjustified double casts, non-null assertions, ts-ignore/ts-nocheck/expect-error/lint suppressions, and schema/route/FieldPath casts. Trace actual invariants and intentional negative type tests before declaring a suppression defective.
- Prefer precise native/domain types, discriminated unions, exhaustive handling, and relationship-preserving generics. Do not demand annotations where inference is already safe or replace all types with broad object/records.
- Verify raw schema input, parsed output, request/response shape, action errors, nullable states, and public exports agree with consumers.
- Keep internal type ownership FSD-compliant: no application RootState/router imports into lower slices or circular type dependencies.

Unsafe example, even if noImplicitAny does not reject the external JSON return type:

```ts
const payload = await response.json();
return payload.user.name;
```

Trace the actual response library types before reporting. A safe correction defines an unknown boundary and validates the user/name shape using existing schema or guards; it does not assert a desired type to satisfy the compiler.

Legitimate unknown example:

```ts
function isNamed(value: unknown): value is { name: string } {
  return typeof value === "object" && value !== null &&
    "name" in value && typeof value.name === "string";
}
```

This guards the stated shape only. Do not claim it validates a larger domain contract or requires converting every existing schema into handwritten guards.

## 4. Correct only authorized defects

In fix mode, address the producing contract and actual consumers, reuse installed schemas/native types, and preserve runtime behavior. Keep justified narrow assertions only where invariants are explicit; do not blanket-replace any with unknown/casts or suppress resulting errors.

Do not silently enable stricter settings globally, migrate libraries, disable skip/strict/lint checks, or change generated declarations as a shortcut. For external package limitations provide a safe adapter or report the dependency issue.

Run applicable existing type checks and supported type-aware lint plus relevant behavior tests/build. Explain configuration/tool gaps and pre-existing errors; a transpilation build is not a type-check pass. Keep FSD, no cycles, and 150-line authored source limits.

Use [review cases](../review-quality-gate/references/review-cases.md) to calibrate explicit any, unsafe inferred flow, safe unknown, and text-only false positives. Do not claim actual compiler/lint execution from reading examples.

</execution_steps>

<output_contract>

Return `PASS`, `FAIL`, or `INCOMPLETE` with included-file/config/tool coverage, confirmed type-flow findings and locations, safe remediation, authorized fixes, actual check results, and missing evidence under the auditor contract.

</output_contract>
