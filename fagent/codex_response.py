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
        """Yield balanced JSON objects embedded in a short prose/Markdown response."""
        starts = [index for index, char in enumerate(text) if char == "{"]
        for start in starts:
            depth, quoted, escaped = 0, False, False
            for index in range(start, len(text)):
                char = text[index]
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
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        yield text[start:index + 1]
                        break

    def decode(self, api_key=None):
        if not isinstance(self.answer, str):
            raise CodexOperationError("Codex completed the turn without a final agent message.")
        if api_key and api_key in self.answer:
            raise CodexOperationError("Codex returned confidential material; the response was discarded.")
        text = self.answer.strip()
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].lower() in ("```", "```json") and lines[-1] == "```":
            text = "\n".join(lines[1:-1])
        candidates = [text, *self._objects(text)]
        for candidate in candidates:
            try:
                result = json.loads(candidate, object_pairs_hook=unique_keys)
            except (ValueError, UnicodeError):
                continue
            if isinstance(result, dict) and isinstance(result.get("status"), str):
                return result
        raise CodexOperationError("Codex returned an invalid JSON response. The agent output did not match the protocol.")
