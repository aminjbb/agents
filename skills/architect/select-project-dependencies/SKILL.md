---
name: select-project-dependencies
description: Evaluate whether a React feature needs a new package, compare verified compatible options against installed capabilities and project policies, and record a decision before dependent implementation without installing during planning.
---

# Select Project Dependencies

<inputs>

- Target project, bounded capability requirement/acceptance criteria, and architecture plan or equivalent context.
- Existing package/lockfile, runtime/build/toolchain constraints, accepted stack and installation scope.

This skill produces a decision. Installation is a separate step in an authorized implementation task; a recommendation is not automatic installation or user approval.

</inputs>

<execution_steps>

## 1. Establish whether a new dependency is needed

Inspect actual installed versions, peer dependencies, lockfile/package manager/workspaces, React/TypeScript/Vite setup, existing helpers, and the feature's real gap. Reuse supported built-in or installed capabilities when they meet requirements.

Preserve this project's accepted Query v5, RTK, installed router, RHF/Zod or justified React Actions, and UI-system contracts. Do not introduce competing caches/routers/forms merely because they are popular or appear in copied examples.

If no new package is needed, record the existing capability and stop selection; do not manufacture a comparison or upgrade every tool before coding.

## 2. Verify candidate evidence

For a genuine gap, shortlist only credible fitting options. Verify unstable facts from current primary sources: official docs, package metadata, repository/releases, and actual published compatibility. Record source URLs, evidence date, relevant version/range, and uncertainty.

Assess what matters to this task:

- React/TypeScript/build/runtime and peer-dependency compatibility.
- API/type quality, required browser support, SSR-only constraints versus SPA usage, and framework assumptions.
- Existing design-system/accessibility/locale integration and state/FSD ownership.
- Maintenance/release evidence and migration burden, without equating download counts to quality.
- Bundle/runtime/transitive costs with the source/method and limitations of estimates. Do not invent size/performance numbers.
- License/usage constraints where relevant; report concrete uncertainty rather than declaring legal approval.
- Existing audit/advisory evidence where available and relevant; do not invent a security guarantee or install/execute untrusted package code to evaluate it casually.

If primary sources/network are unavailable, report the compatibility gap and a bounded provisional option. Do not claim verified suitability or unblock dependent code by guessing versions.

## 3. Make the scoped decision

Explain the smallest fitting choice, why reuse or alternatives were insufficient, installation scope, intended owner, required configuration, API contracts, and verification/migration implications.

Do not decide a costly architectural migration hidden inside a package selection. Reuse prior accepted decisions unless requirements/evidence change. Clarify material tradeoffs only when task authorization/context cannot resolve them; do not demand confirmation for every routine package choice already authorized by implementation scope.

```text
Dependency decision / capability:
Existing capabilities and gap:
Candidate/version | Primary evidence/date | Compatibility | Cost/risks
Selected option, or no new dependency:
Rejected alternatives with relevant reason:
FSD owner/public integration contract:
Installation/configuration scope and required checks:
Unverified facts or material decision needed:
```

## 4. Bind implementation without silently installing

In a planning task, return the decision without changing package.json/lockfiles, running installers, importing package code, or executing install scripts.

In an authorized implementation task, subsequent installation must follow the project's package manager/version policy, scoped workspace, permission limits, and actual compatible version. Preserve unrelated dependencies/scripts; no broad upgrade, mixed lockfiles, or unrequested release/deployment.

Before dependent source is written, resolve essential compatibility questions. After actual installation, inspect the lockfile/peer result and run applicable existing type/build/behavior checks; revise the decision if evidence contradicts it. Do not mark recommended packages as installed or tested.

</execution_steps>

<output_contract>

Return `DECIDED`, `NO_NEW_DEPENDENCY`, `NEEDS_INPUT`, or `BLOCKED`, with evidence, recommendation/reuse rationale, contract/installation scope, uncertainties, and remaining verification. DECIDED is a documented sufficiently supported choice, not executed installation or unconditional production approval.

</output_contract>
