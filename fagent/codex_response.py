"""Collect nonempty final messages and decode the JSON transport envelope."""
import json

from .codex_errors import CodexOperationError
from .registry import unique_keys


class AgentResponse:
    def __init__(self):
        self.deltas, self.answer = {}, None

    def observe(self, event):
        params = event.get("params", {})
        if event.get("method") == "item/agentMessage/delta":
            identity, delta = params.get("itemId"), params.get("delta")
            if isinstance(identity, str) and isinstance(delta, str):
                self.deltas[identity] = self.deltas.get(identity, "") + delta
        elif event.get("method") == "item/completed":
            item = params.get("item", {})
            if item.get("type") != "agentMessage" or item.get("phase") not in (None, "final_answer"):
                return
            text = item.get("text") or self.deltas.get(item.get("id"))
            if isinstance(text, str) and text.strip():
                # An empty trailing item must not erase a previously complete answer.
                self.answer = text

    @staticmethod
    def _objects(text):
        """Yield only top-level containers; never salvage nested checks/envelopes."""
        start, depth, quoted, escaped = None, 0, False, False
        for index, char in enumerate(text):
            if start is None:
                if char in "{[":
                    start, depth = index, 1
                continue
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
                continue
            if char == '"':
                quoted = True
            elif char in "{[":
                depth += 1
            elif char in "}]":
                depth -= 1
                if depth == 0:
                    yield text[start:index + 1]
                    start = None

    def decode(self, api_key=None, operation=None):
        if not isinstance(self.answer, str):
            raise CodexOperationError("Codex completed the turn without a final agent message.")
        if api_key and api_key in self.answer:
            raise CodexOperationError("Codex returned confidential material; the response was discarded.")
        text = self.answer.strip()
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].lower() in ("```", "```json") and lines[-1] == "```":
            text = "\n".join(lines[1:-1])
        try:
            result = json.loads(text, object_pairs_hook=unique_keys)
        except (ValueError, UnicodeError):
            # Permit one complete envelope surrounded by prose, but reject
            # ambiguous objects, duplicate keys, arrays and malformed parents.
            candidates = list(self._objects(text))
            try:
                result = json.loads(candidates[0], object_pairs_hook=unique_keys) if len(candidates) == 1 else None
            except (ValueError, UnicodeError):
                result = None
        fields = ("verdict",) if operation == "review_delivery" else (
            ("status",) if operation else ("status", "verdict"))
        if isinstance(result, dict) and any(isinstance(result.get(key), str) for key in fields):
            return result
        raise CodexOperationError("Codex returned an invalid JSON response. The agent output did not match the protocol.")
