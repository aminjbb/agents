---
name: implement-route-guard
description: Wire approved session and permission contracts into SPA route access, safe login return navigation, and protected loader/prefetch behavior without creating a second auth store or server cache.
---

# Implement Route Guard and Session Contract

<inputs>

- Target project and protected route/branch scope.
- Accepted access policy, login/forbidden/error behavior, and allowed internal return-destination policy.
- Existing session/permission owner and Query contract, identity lifecycle, router family/version/mode.
- `mode`: `plan` for audits/design/dry runs; `implement` for authorized changes.

Do not invent roles, endpoints, session freshness, or product policies. Inspect existing interfaces first; missing essential contracts block only dependent access implementation.

</inputs>

<execution_steps>

## 1. Establish ownership and the access matrix

Read instructions and existing router/session/provider/query code. @state-master owns server-authoritative session/permission data and freshness; @navigator owns route-to-policy wiring and navigation outcomes in `app`.

Specify behavior for checking, guest, verified authorized, verified forbidden, and verification failure. Do not infer authentication from a stored flag/token alone, present stale cached permissions as newly verified, or treat network failure as guest status.

Keep protected content hidden while access is unknown, without blank indefinite waiting. Define error/retry behavior with the real session owner. Public login and error/recovery paths must not require their own unavailable authentication check.

## 2. Define or adapt a minimal typed contract

Prefer the actual existing contract. If a new adapter is required, agree its semantic shape with @state-master/@architect before implementation. This example defines an imperative decision boundary, not another persisted session model:

```ts
export type AccessDecision =
  | { kind: "allow"; identityKey: string }
  | { kind: "guest" }
  | { kind: "forbidden" }
  | { kind: "unavailable"; retryable: boolean };

export interface AccessPolicy {
  id: string;
}

export interface AccessResolver {
  resolve(
    policy: AccessPolicy,
    signal: AbortSignal,
  ): Promise<AccessDecision>;
}
```

`policy.id` references a confirmed domain policy; it is not a client-invented role or backend authorization guarantee. `identityKey` is a non-secret identity/tenant scope from the owner's contract, never a credential. The pending promise represents checking; do not store a duplicate session snapshot in this adapter.

Place business contract types and verification with their real lower owner and expose required symbols through its `index.ts`. Place router-specific wrappers and dependency injection in `app`. Lower code must not import application RootState/router hooks/instances, even as types. Keep all dependency graphs acyclic.

Document freshness, error semantics, account/tenant identity changes, cancellation, and in-flight behavior. Prevent decisions for an old identity from authorizing a new one; use the existing owner's identity/version contract rather than inventing a competing auth authority.

In plan mode, return the matrix and proposed wiring now without source, package, or external mutations.

## 3. Wire actual execution boundaries

- Declarative React Router: place an appropriate React guard around protected rendering, using approved hooks. Do not claim this gates arbitrary background requests or independent data paths.
- React Router Data/Framework mode: inspect installed loader/action/prefetch ordering. A parent loader is not automatically a sequential auth barrier for child loaders. Apply approved verification to each protected data path or a supported sequencing/middleware mechanism available in that exact version/mode.
- TanStack Router: use supported `beforeLoad` integration and typed injected context, preserving the documented parent/child ordering and redirect semantics. Do not call hooks in `beforeLoad` or loaders.

Imperative checks coordinate the existing QueryClient and exported options/service contract. No direct fetch/Axios/SDK calls in guards/loaders, Redux server mirrors, per-guard QueryClients, or parallel route caches.

Inspect link prefetch and route preload behavior as well as direct navigation. Ensure session/access prerequisites precede protected requests under the chosen contract. Code loading itself is not a privacy boundary.

## 4. Make redirects and identity transitions safe

- Preserve only the permitted internal destination/search/hash. Parse destinations against the trusted origin and base-path policy and validate the resulting target; reject external/protocol-relative URLs, disallowed schemes, credentials, malformed input, and login-return cycles.
- Handle encoded or nested return values with a bounded documented decoding policy, not repeated arbitrary decoding. Never rely solely on `startsWith("/")` or concatenate a user-supplied origin.
- Use an accepted safe fallback. Guard redirects generally replace the dead-end entry; preserve intentional user navigation history.
- Keep redirect control flow distinct from failures. Do not swallow a router redirect in a generic catch block.
- Coordinate logout/expiry/account-switch with protected UI removal, owner-managed cache cancellation/removal, and router revalidation. Test rapidly changing identity and late verification responses.

Backend endpoints must independently authorize requests. State clearly whether backend enforcement was outside scope or actually tested; a SPA guard never proves it.

## 5. Verify the selected paths

Use isolated router/QueryClient fixtures and controlled session responses. Cover initial direct private entry, pending without private flash, guest/login/valid return, forbidden, verification error/retry, intentional redirect propagation, invalid return targets, logout/expiry, and relevant identity switches.

Observe protected loaders/actions/prefetches under guest and forbidden states; do not infer request ordering from a hidden screen. Avoid real payments/deletions or messaging merely to verify access.

Use [audit-routing](../audit-routing/SKILL.md) in read-only mode for relevant integration coverage, sharing evidence and avoiding recursive fix calls. Check FSD, public APIs, cycles, source limits, and existing applicable type/lint/test/build commands. Every authored source file/component is at most 150 physical lines.

</execution_steps>

<output_contract>

Return `IMPLEMENTED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`. Include session/policy owners and typed contract, route access matrix, actual ordering protections, redirect policy, changed files, checks/results, and coverage gaps. Report partial progress honestly when mandatory verification is unavailable; do not claim backend protection or completed access enforcement from rendering alone.

</output_contract>
