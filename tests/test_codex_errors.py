"""Categorized diagnostics must stay useful without forwarding credentials."""
import unittest

from fagent.codex_errors import rpc_error, turn_error


class CodexErrorTests(unittest.TestCase):
    def test_rpc_stage_and_experimental_capability_are_visible(self):
        error = rpc_error("thread/start", {"code": -32600,
                          "message": "ephemeral requires experimentalApi capability secret-token"})
        self.assertIn("thread creation", str(error))
        self.assertIn("experimental API", str(error))
        self.assertNotIn("secret-token", str(error))

    def test_model_auth_and_permission_messages_are_categorized(self):
        for text, expected in (("model is not supported secret", "selected model"),
                               ("Unauthorized secret", "Sign in"),
                               ("sandbox permission error secret", "sandbox conflicts")):
            with self.subTest(text=text):
                error = rpc_error("turn/start", {"message": text})
                self.assertIn(expected, str(error))
                self.assertNotIn("secret", str(error))

    def test_unknown_rpc_details_never_leave_bridge(self):
        error = rpc_error("thread/start", {"code": -123, "message": "secret-key private-provider-url"})
        self.assertIn("-123", str(error))
        self.assertNotIn("secret-key", str(error))
        self.assertNotIn("private-provider-url", str(error))

    def test_structured_turn_failure_reports_network_and_usage(self):
        for info, expected in (({"responseStreamConnectionFailed": {"httpStatusCode": 503}}, "network"),
                               ("usageLimitExceeded", "usage limit"),
                               ("unauthorized", "unauthorized"),
                               ("sandboxError", "sandbox")):
            with self.subTest(info=info):
                error = turn_error({"codexErrorInfo": info, "message": "secret"})
                self.assertIn(expected, str(error))
                self.assertNotIn("secret", str(error))
        self.assertTrue(turn_error({"codexErrorInfo": "serverOverloaded"}).retryable)

    def test_unknown_or_missing_turn_error_remains_safe(self):
        for payload in (None, {}, {"codexErrorInfo": "secret", "message": "key"}):
            error = turn_error(payload)
            self.assertIn("model turn failed", str(error))
            self.assertNotIn("secret", str(error))
