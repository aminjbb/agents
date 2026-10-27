import tempfile
import unittest
from pathlib import Path

from fagent.plans import architect_plan, normalize_architect_response, prepare


class ArchitectPlanEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.request = {"project_root": self.temp.name, "mode": "plan"}

    def task(self):
        return {"id": "T1", "owner": "@architect", "objective": "Plan",
                "deliverable": "Plan", "depends_on": [], "write_scope": [],
                "acceptance_criteria": ["A"]}

    def test_canonical_plan_envelope(self):
        result = {"status": "planned", "plan": {"tasks": [self.task()]}}
        self.assertEqual(architect_plan(result)["tasks"][0]["id"], "T1")
        prepare(architect_plan(result), self.request)

    def test_compatibility_planned_envelope_from_live_architect(self):
        result = {"status": "planned", "planned": {"metadata": {"feature_id": "x"},
                                                       "tasks": [self.task()]}}
        self.assertEqual(architect_plan(result)["tasks"][0]["id"], "T1")
        prepare(architect_plan(result), self.request)

    def test_nested_plan_is_unwrapped(self):
        result = {"status": "planned", "planned": {"plan": {"tasks": [self.task()]}}}
        self.assertEqual(len(architect_plan(result)["tasks"]), 1)

    def test_direct_task_graph_envelope_is_accepted(self):
        result = {"status": "planned", "tasks": [self.task()],
                  "metadata": {"feature_id": "clothing"}, "context": "plan only"}
        self.assertEqual(architect_plan(result)["tasks"][0]["id"], "T1")

    def test_missing_plan_stays_actionable(self):
        with self.assertRaisesRegex(ValueError, "plan"):
            architect_plan({"status": "planned"})

    def test_status_labels_are_normalized_at_protocol_boundary(self):
        self.assertEqual(normalize_architect_response({"status": " PLANNED "})["status"], "planned")
        self.assertEqual(normalize_architect_response({"status": "APPROVED"})["status"], "planned")
        self.assertEqual(normalize_architect_response({"status": "READY"})["status"], "planned")
        self.assertEqual(normalize_architect_response({"status": "NEEDS_INPUT"})["status"], "needs_input")

    def test_task_graph_can_infer_planning_status(self):
        self.assertEqual(normalize_architect_response({"tasks": []})["status"], "planned")

    def test_unknown_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid architect planning status"):
            normalize_architect_response({"status": "done"})

    def test_known_config_scope_families_expand_to_finite_files(self):
        plan = {"tasks": [{**self.task(), "write_scope": ["vite.config.*", "tsconfig*.json"]}]}
        prepared, _ = prepare(plan, self.request)
        self.assertEqual(prepared["tasks"][0]["write_scope"], [
            "vite.config.ts", "vite.config.js", "vite.config.mts",
            "vite.config.mjs", "vite.config.cjs", "tsconfig.json",
            "tsconfig.app.json", "tsconfig.node.json"])
