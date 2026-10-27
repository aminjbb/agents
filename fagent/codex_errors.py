"""Actionable diagnostics derived from error categories, never raw provider text."""
from .protocol import ProtocolError


class CodexOperationError(ProtocolError):
    def __init__(self, message, retryable=False):
        super().__init__(message)
        self.retryable = retryable


def rpc_error(method, error):
    # Only internally selected method names and numeric codes are interpolated.
    labels = {"initialize": "initialization", "account/read": "authentication check",
              "account/login/start": "sign-in", "thread/start": "thread creation",
              "turn/start": "turn creation"}
    stage = labels.get(method, "request")
    message = str(error.get("message", "")).lower() if isinstance(error, dict) else ""
    if "experimentalapi" in message or "experimental api" in message:
        detail = "The CLI requires experimental API capability for a requested field."
    elif "model" in message and any(word in message for word in ("support", "access", "found", "invalid")):
        detail = "The selected model is unavailable. Clear the model field or select an account-supported model."
    elif any(word in message for word in ("unauthorized", "authentication", "not logged", "401")):
        detail = "Sign in again with codex login or reconnect with a valid API key."
    elif "sandbox" in message or "permission" in message:
        detail = "The requested sandbox conflicts with CLI permissions or managed settings."
    else:
        code = error.get("code") if isinstance(error, dict) else None
        detail = f"RPC error code {code}." if type(code) is int else "The CLI rejected the request."
    return CodexOperationError(f"Codex {stage} failed. {detail}")


def turn_error(error):
    info = error.get("codexErrorInfo") if isinstance(error, dict) else None
    kind = info if isinstance(info, str) else next(iter(info), "") if isinstance(info, dict) else ""
    categories = {
        "contextWindowExceeded": "The request exceeded the model context window. Shorten the request.",
        "usageLimitExceeded": "Account usage limit reached. Check your Codex usage allowance.",
        "serverOverloaded": "The model service is busy. Retry later.",
        "httpConnectionFailed": "The model service could not be reached. Check network or proxy settings.",
        "responseStreamConnectionFailed": "The model connection failed. Check network or proxy settings.",
        "responseStreamDisconnected": "The model connection was interrupted. Retry the planning request.",
        "responseTooManyFailedAttempts": "The model connection failed after retries. Check network or proxy settings.",
        "unauthorized": "Your session is unauthorized. Run codex login and reconnect.",
        "sandboxError": "The CLI could not start the requested sandbox. Check local sandbox setup.",
        "badRequest": "The model rejected the request. Check the selected model and request configuration.",
    }
    detail = categories.get(kind, "The CLI ended the turn without a result. Check model access and local CLI configuration.")
    retryable = kind in {"serverOverloaded", "rateLimitExceeded", "internalServerError",
                         "httpConnectionFailed", "responseStreamConnectionFailed",
                         "responseStreamDisconnected", "responseTooManyFailedAttempts"}
    return CodexOperationError("Codex model turn failed. " + detail, retryable=retryable)
