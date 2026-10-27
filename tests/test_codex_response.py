import unittest

from fagent.codex_errors import CodexOperationError
from fagent.codex_response import AgentResponse


def completed(text, identity="a", phase="final_answer"):
    return {"method": "item/completed", "params": {"item": {
        "type": "agentMessage", "id": identity, "text": text, "phase": phase}}}


class CodexResponseTests(unittest.TestCase):
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
