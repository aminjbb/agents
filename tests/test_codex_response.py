import json
import unittest

from fagent.codex_errors import CodexOperationError
from fagent.codex_response import AgentResponse
from fagent.outcomes import audit
from helpers import evidence


def completed(text, identity="a", phase="final_answer"):
    return {"method": "item/completed", "params": {"item": {
        "type": "agentMessage", "id": identity, "text": text, "phase": phase}}}


class CodexResponseTests(unittest.TestCase):
    def test_verdict_only_audit_preserves_the_complete_envelope(self):
        for verdict in ("PASS", "FAIL", "INCOMPLETE"):
            expected = evidence(verdict=verdict)
            response = AgentResponse()
            response.observe(completed(json.dumps(expected)))
            self.assertEqual(response.decode(), expected)
            self.assertEqual(audit(response.decode()), verdict)

    def test_decoder_never_promotes_a_nested_check_to_a_response(self):
        response = AgentResponse()
        for payload in ({"checks": [{"status": "PASS"}]},
                        [{"status": "planned"}],
                        {"status": None, "nested": {"status": "planned"}}):
            with self.subTest(payload=payload), self.assertRaises(CodexOperationError):
                response.observe(completed(json.dumps(payload)))
                response.decode()

    def test_operation_selects_the_envelope_field_without_losing_audit_evidence(self):
        response = AgentResponse()
        expected = evidence(verdict="PASS")
        response.observe(completed("Reviewed.\n" + json.dumps(expected) + "\nReady."))
        self.assertEqual(response.decode(operation="review_delivery"), expected)
        with self.assertRaises(CodexOperationError):
            response.decode(operation="plan")
        response.observe(completed('{"status":"approved"}'))
        with self.assertRaises(CodexOperationError):
            response.decode(operation="review_delivery")

    def test_ambiguous_envelopes_and_invalid_parents_are_not_salvaged(self):
        response = AgentResponse()
        for text in ('{"status":"planned"}\n{"status":"blocked"}',
                     'Reply: {"status":"planned","status":"blocked","nested":{"status":"planned"}}',
                     'Reply: [{"status":"planned"}]',
                     'Reply: {"checks":[{"status":"PASS"}]}',
                     'Reply: {"broken": {"status":"planned"}'):
            with self.subTest(text=text), self.assertRaises(CodexOperationError):
                response.observe(completed(text))
                response.decode()

    def test_empty_final_item_does_not_erase_valid_response(self):
        response = AgentResponse()
        response.observe(completed('{"status":"planned"}'))
        response.observe(completed("", "b"))
        response.observe(completed("commentary", "c", "commentary"))
        self.assertEqual(response.decode()["status"], "planned")

    def test_streamed_text_is_used_when_completed_text_is_empty(self):
        response = AgentResponse()
        for delta in ('{"status":', '"planned"}'):
            response.observe({"method": "item/agentMessage/delta", "params": {"itemId": "a", "delta": delta}})
        response.observe(completed(""))
        self.assertEqual(response.decode()["status"], "planned")

    def test_accepts_one_json_fence_but_rejects_mixed_text_and_duplicate_keys(self):
        response = AgentResponse()
        response.observe(completed('```json\n{"status":"planned"}\n```'))
        self.assertEqual(response.decode()["status"], "planned")
        for text in ('{"status":1,"status":2}', '[]'):
            with self.subTest(text=text), self.assertRaises(CodexOperationError):
                response.observe(completed(text))
                response.decode()

    def test_extracts_json_surrounded_by_short_agent_explanation(self):
        response = AgentResponse()
        response.observe(completed('I inspected the request.\n{"status":"planned","plan":{"tasks":[]}}\nThe plan is ready.'))
        self.assertEqual(response.decode()["status"], "planned")

    def test_errors_never_expose_response_or_credential(self):
        response = AgentResponse()
        with self.assertRaises(CodexOperationError):
            response.decode()
        response.observe(completed('{"value":"secret-key"}'))
        with self.assertRaises(CodexOperationError) as caught:
            response.decode("secret-key")
        self.assertNotIn("secret-key", str(caught.exception))
