---
name: orchestrate-feature-delivery
description: Decompose a bounded architecture plan into contract-driven tasks, validate dependency/file ownership conflicts, coordinate authorized specialist work, and integrate verified outcomes without implying a running multi-agent system.
---

# Orchestrate Feature Delivery

<inputs>

- Target project, feature brief/accepted behavior, architecture/public/package contracts, and task scope.
- Mode `plan` for decomposition/design/review/dry run; `execute` only within an authorized implementation task.
- Actual host delegation/tool availability and prior task/evidence state.

Creating a task graph does not itself authorize spawning agents, installing packages, or external publication. Keep the package location separate from the target app and preserve unrelated work.

</inputs>

<execution_steps>

## 1. Create cohesive deliverables

Break the requested behavior into independently reviewable outcomes rather than one whole-app task or one task per import. Small changes may need a single task; do not force all agents or skills onto them.

For each task define a stable ID, objective, deliverable, responsible agent, dependencies, exact project-relative write scope, contract inputs/outputs, observable acceptance, relevant checks, and status/evidence. Read-only tasks have an empty write scope.

Use owners by responsibility:

| Owner | Responsibility |
| --- | --- |
| @architect | Requirements, architecture/packages, contracts, integration/acceptance |
| @state-master | Query/API/cache/global-client models and identity lifecycle |
| @ui-crafter | Design interpretation, primitives, component presentation and access mechanics |
| @navigator | Lazy routes, guards, URL/history and navigation integration |
| @form-wizard | Schema, draft lifecycle, form controller/submission |
| @auditor | Independent quality review with read-only default |

The table assigns logical ownership, not proof those agents are executable/available. Delegate only when host/task authorization permits; otherwise complete authorized work serially or return concrete handoffs without claiming agents ran.

## 2. Define contracts and scheduling first

Resolve shared API/schema/props/route contracts before dependent implementation. Assign one writer to shared index/provider/config/package files at a time. Two writers may touch an overlapping scope only with explicit dependency ordering and consumer review.

Parallel tasks require satisfied prerequisites, compatible contracts, and disjoint write scopes. A task depending on another must not start dependent work before its prerequisite output is actually ready. Do not treat a status label alone as implementation evidence.

If contracts change, update affected tasks/consumers and pause only dependent operations. Do not allow a specialist to redefine another owner's interface unilaterally or overwrite concurrent changes.

## 3. Validate a concrete task plan

When a machine-readable plan is useful, use this minimal shape plus any task-specific contracts/check/evidence fields:

```json
{
  "mode": "plan",
  "tasks": [
    {
      "id": "T1",
      "owner": "@architect",
      "objective": "Define product creation contracts",
      "deliverable": "Typed payload and ownership plan",
      "depends_on": [],
      "write_scope": [],
      "acceptance_criteria": ["Every responsibility has a valid FSD owner"],
      "status": "pending"
    }
  ]
}
```

Validate with the included [validate_task_plan.py](scripts/validate_task_plan.py):

```text
python <skill-directory>/scripts/validate_task_plan.py <task-plan.json>
```

Scope paths use forward slashes relative to the target project; directories end in `/`, files do not, and glob/absolute/traversal paths are unsupported. The validator checks unique IDs, recognized owners, required fields, dependency references/cycles, prerequisite status for ready/running/done tasks, and unordered overlapping write scopes. Conservative case-insensitive comparison protects Windows workspaces.

It does not resolve filesystem links, verify contracts, check permissions, prove safe parallelism, or start work. Inspect actual canonical paths/consumers before mutation; a syntactically valid task list is not accepted architecture or an execution grant.

The optional [Python coordinator](../../../fagent/orchestrator.py) reuses this validator with explicit `allow_serialized_writes=True`: it reports unordered scope collisions and serializes them using canonical project paths instead of rejecting every such plan. The standalone validator's default remains strict. See [runtime/adapter protocol](../../../docs/orchestration.md) for actual supported states, JSON transport, clarification/resume, attempt limits, and host sandbox responsibilities. These modes do not bypass dependency or cycle checks.

## 4. Execute only authorized work

Plan mode returns task graph/handoffs without modifying the application, installing dependencies, or launching agents. A request to split tasks does not imply implementation.

In execute mode, check actual prerequisites/authorization, load matching procedures, and complete relevant work. Track pending/ready/running/done/blocked plus evidence; mark done only after its deliverable and required checks are satisfied.

Use the instruction's handoff template with exact scope, public contracts, behavior, checks, and escalation conditions. Include the actual linked specialist instruction/skill paths; do not send messages or spawn agents on the basis of a generated plan alone.

## 5. Integrate and review the complete path

Inspect the combined diff/public consumers, not just individual patches. Resolve conflicts through ownership, update contracts, and verify at least the accepted end-to-end path and relevant failure states. Avoid duplicate stores, routers, submit paths, or unchecked eager imports.

Use [validate-fsd-boundaries](../../validate-fsd-boundaries/SKILL.md) for import/cycle evidence and [review-quality-gate](../../auditor/review-quality-gate/SKILL.md) for the appropriate independent quality review. These relative paths are resolved from this file; neither a boundary PASS nor producer claims replace behavioral evidence.

Specialist review may be performed without spawning a separate agent, but disclose that distinction; do not call it an independent second-agent evaluation. Preserve @auditor's FAIL/INCOMPLETE findings and require correction or explicit unresolved reporting, not silent override.

Architectural acceptance belongs to @architect after applicable gates pass. Implementation authorization is not permission to merge, publish, deploy, or execute real external transactions. Continue authorized work until requested outcomes are fulfilled, or report a precise external/decision blocker with independent progress.

## 6. Return traceable delivery state

Report brief/plan/decision IDs, task owners/statuses/dependency readiness, actual execution/agent availability, changed files/contracts, check results, audit verdicts, unresolved dependencies, and remaining work.

For calibration, use [coordination cases](references/coordination-cases.md). They are static scenarios plus structural-validator fixtures, not proof of actual multi-agent execution or application behavior.

</execution_steps>

<output_contract>

Return `PLANNED`, `DELIVERED`, or `BLOCKED`. PLANNED is a reviewed handoff/schedule, not completed code. DELIVERED requires the requested integrated behavior and applicable evidence/acceptance gates. Report partial progress and unsatisfied gates explicitly; do not mark a blocked task done or an incomplete audit passed.

</output_contract>
