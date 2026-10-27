# Chief Architect Coordination Cases

These scenarios calibrate planning and ownership. They are not evidence of actual specialist-agent execution, dependency installation, or browser/runtime verification.

## 1. Ambiguous feature request

Request: "Add product creation with our design."

Expected: inspect the real app/design and accepted contracts; identify missing fields, access, persistence, and completion behavior without inventing endpoints. Ask only material product questions in plain language. A plan request creates no source or packages; independent inspection continues while answers are pending.

Failure signals: generic whole-app scaffold, fabricated API, asking the user to choose internal store types, or treating a Figma image as a complete interaction contract.

## 2. Small edit

Request: "Change the submit label using the existing component."

Expected: inspect the consumer and semantics; one bounded task may be enough. Reuse tokens/components and relevant checks. Do not require all five specialists, new packages, full architecture documents, or a migration.

## 3. Multi-owner private create form

Requirements: approved fields/payload, existing session/Query/router/UI/form stack, private creation route, accepted success destination.

Expected: architect defines ownership/public contracts; state-master owns mutation/cache contract; navigator owns lazy route/guard/URL; form-wizard owns draft/schema/submission; ui-crafter owns approved field/layout integration; auditor independently reviews relevant quality. Actual delegation remains conditional on authorization/capabilities.

Parallelism requires disjoint writes and ready contracts. If several tasks need the same slice index/provider, serialize that file's edits or assign one integration owner. Query data, form draft, and URL facts retain distinct authority.

Final acceptance needs the integrated success/failure/access/draft behavior, not merely individually "done" labels or a passing import scan.

## 4. Dependency decision

Existing capability satisfies the request: record NO_NEW_DEPENDENCY; do not install an alternative.

Real missing capability: verify current primary-source compatibility and scope before dependent coding. A package decision does not mean installed/tested. Planning must leave manifests/lockfiles unchanged; implementation must preserve unrelated versions/scripts.

## 5. Conflicting architecture proposal

Request mentions Bulletproof React in an existing strict-FSD project.

Expected: distinguish a requested migration from an example/preference; keep the active FSD policy until a coherent coordinated change is explicitly in scope. Do not mix direct private imports with required root index APIs or run FSD validation as certification of another profile.

## Structural-validator expectations

| Input case | Expected |
| --- | --- |
| One well-formed task with empty write scope | PASS, structure only |
| Independent tasks with disjoint file scopes | PASS |
| Two writers of the same file with no dependency | FAIL |
| Directory writer and nested-file writer unordered | FAIL |
| Same path with different casing on Windows-like scopes | FAIL unless ordered |
| Ordered writers, including transitive dependency ordering | PASS if status prerequisites are consistent |
| Cycle, self-dependency, missing dependency, duplicate ID | FAIL |
| Ready/running/done task with unfinished prerequisite | FAIL |
| Missing acceptance/deliverable/owner or unknown status | FAIL |
| Absolute, traversal, glob, ambiguous noncanonical scope | FAIL |
| Valid structure, but symlink escape or incompatible real contracts | Structural PASS does not authorize execution; inspect actual paths/contracts |

Verdicts: PLANNED describes task artifacts; DELIVERED requires actual requested behavior and verification; BLOCKED names an essential unmet dependency without discarding independent progress. @auditor FAIL/INCOMPLETE and missing mandatory checks cannot become architectural approval by relabeling tasks.
