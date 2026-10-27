---
name: audit-routing
description: Audit SPA route registration, FSD boundaries, lazy chunks, access ordering, redirect safety, URL contracts, history, and direct-link behavior using bounded evidence. Default to read-only analysis.
---

# Audit Routing

<inputs>

- Target project and route/changed-file scope; use full relevant dependency/consumer context.
- Router/version/mode, accepted behavior, access and URL contracts, available preview/build/hosting tools.
- `mode`: `audit` by default; `fix` only for authorized corrections. An audit request does not authorize package installs, source auto-fixes, hosting edits, or deployment.

</inputs>

<execution_steps>

## 1. Establish scope and evidence

Read applicable instructions and inspect route registration/discovery, generated tree, page exports, app providers, session/query owners, URL codecs, navigation callers, build configuration, and existing tests. Preserve unrelated/uncommitted work.

Record inspected paths/routes, installed router mode/version, environment/base path, fixtures, actual tools/commands, and unavailable coverage. A missing browser permits useful static review but not a runtime pass.

Use syntax-aware/resolved import analysis where necessary; text search discovers candidates, not complete proof. Distinguish authored source from generated/vendor output without ignoring authored dependencies through generated types.

## 2. Run the bounded checklist

### Registration and FSD

- [ ] One stable router; compatible registration/discovery and no manually edited generated tree.
- [ ] No duplicate/ambiguous IDs or unintended nested/index/dynamic/wildcard matches.
- [ ] App-owned wiring and page-owned screens; root slice public APIs and documented Shared boundaries.
- [ ] No upward/sibling/self-barrel imports or cycles, including type edges; no lower app-router/store types disguised through casts or global declarations.
- [ ] Authored files/components at most 150 physical lines; no unrelated router/library migration.

### Lazy pages and recovery

- [ ] Every page implementation has a supported dynamic boundary; critical shell/metadata/recovery is distinguished from eager screens.
- [ ] No eager competing import, layer-wide page barrel, lazy declaration inside render, or unconditional all-page preload.
- [ ] Build/import evidence supports the claimed split. Source dynamic syntax alone is insufficient.
- [ ] Accessible code-pending/error recovery remains usable when the page import rejects; no reload/retry loop.

### Guard and private loading

- [ ] Checking, guest, allow, forbidden, and verification-error states match the accepted contract; no private-content flash.
- [ ] Session is owned by the agreed Query contract, not token presence, a persisted flag, or a duplicate store.
- [ ] Actual loader/action/prefetch execution is gated as required; parent component/loader presence is not assumed to serialize other protected paths.
- [ ] Redirect control flow, safe parsed return destination, login return, fallback, and history replacement work without loops.
- [ ] Logout, expiration, permission/account/tenant changes and late responses cannot resurrect stale protected views/data.
- [ ] Backend authorization is explicitly out of scope or independently evidenced; client guards never prove it.

### URL and navigation

- [ ] Typed validated params, bounds/enums/defaults, repeated-key/encoding policy, and idempotent canonicalization.
- [ ] Supported unrelated params survive; sensitive values are excluded; Query inputs match the validated URL.
- [ ] No committed URL mirror in Redux/local state or router-bypassing window.history writes.
- [ ] Push/replace, rapid/debounced updates, Back/Forward, refresh, new tabs, nested/dynamic/unknown routes, and hashes behave as specified.
- [ ] Base-path and SPA hosting fallback support direct entry without rewriting API/static-asset errors indiscriminately.
- [ ] Semantic links, modifier-click, title/focus/scroll behavior, and relevant dirty-form blocking preserve the accepted experience.

## 3. Exercise critical scenarios

Use isolated router/history/QueryClient fixtures and controlled session/request responses. Start with a private deep link containing valid filters: checking → guest/login → safe return → authorized page → filter change → Back/Forward → logout. Adapt to actual product behavior; do not invent a login requirement for public-only apps.

Add relevant forbidden, failed session verification, invalid return target, invalid URL, chunk failure, and rapid identity/navigation-change scenarios. Record whether checks used actual browser/preview, isolated tests, static inspection, or mocks.

Do not execute real purchases, deletions, messages, or other external effects merely to test navigation. Do not claim server integration, hosting refresh, keyboard behavior, or chunk network ordering from a mocked or static-only check.

## 4. Report findings and authorized corrections

For every finding provide stable ID, severity, route/state and file location where known, violated contract, reproducible evidence, expected/actual behavior, impact, and a concrete correction. Separate confirmed failures from untested hypotheses and pre-existing debt when comparison evidence permits.

Read [validate-fsd-boundaries](../../validate-fsd-boundaries/SKILL.md) before using it for import/cycle analysis. Its verdict does not replace this route behavior audit.

In fix mode, use the relevant [scaffold-route](../scaffold-route/SKILL.md), [implement-route-guard](../implement-route-guard/SKILL.md), or [manage-url-state](../manage-url-state/SKILL.md) procedure within scope, then rerun affected checks. If invoked by one of those skills, return findings to that caller rather than recursively launching another implementation/audit loop.

Run existing applicable type/lint/test/build checks only where consistent with task mode. Do not use auto-fix flags during read-only auditing. Missing required coverage is a gap, not a pass or N/A.

</execution_steps>

<output_contract>

Return overall `PASS`, `FAIL`, or `INCOMPLETE`, preserving separate registration/FSD, lazy-loading, access, URL/history, hosting, and accessibility coverage.

- `PASS`: all applicable checks for the declared bounded scope passed with evidence.
- `FAIL`: at least one confirmed unmet requirement remains; still disclose coverage gaps.
- `INCOMPLETE`: no confirmed remaining violation, but missing tools/access/contracts/evidence prevent a pass.

Use N/A only for justified scope exclusions. Include scope/environment, findings, actual checks/results, changes if authorized, and remaining work. This verdict does not replace @architect's acceptance or backend authorization testing.

</output_contract>
