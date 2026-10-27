"""Load actual manifests/instructions; all frontend intake starts at the architect."""
import json
from pathlib import Path

from .plans import PACKAGE_ROOT
from .protocol import require


def unique_keys(pairs):
    data = {}
    for key, value in pairs:
        require(key not in data, f"Duplicate JSON key: {key}")
        data[key] = value
    return data


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)


class Registry:
    def __init__(self, root=PACKAGE_ROOT):
        self.root = Path(root).resolve()
        self.entry = load_json(self.root / "frontend.entry.json")
        require(self.entry.get("format") == "fagent.frontend-entry" and
                self.entry.get("format_version") == "1.0.0", "Unsupported frontend entry format")
        require(self.entry.get("intake_agent") == "@architect" and
                self.entry.get("quality_reviewer") == "@auditor" and
                self.entry.get("acceptance_agent") == "@architect", "Invalid frontend entry policy")
        self.agents = {}
        for path in self.root.glob("*.agent.json"):
            manifest = load_json(path)
            name = manifest["metadata"]["name"]
            require(name not in self.agents, "Duplicate agent name")
            self.agents[name] = manifest
        require("@architect" in self.agents and "@auditor" in self.agents,
                "Architect and auditor manifests are required")

    def read(self, relative):
        target = (self.root / relative).resolve()
        require(target.is_relative_to(self.root), "Definition path escapes package")
        return target.read_text(encoding="utf-8")

    def packet(self, owner):
        require(owner in self.agents, f"Agent unavailable: {owner}")
        manifest = self.agents[owner]
        return {"manifest": manifest, "package_root": str(self.root),
                "instruction": self.read(manifest["instruction"]["path"]),
                "skills": [{"id": skill["id"], "path": skill["path"],
                            "definition": self.read(skill["path"])}
                           for skill in manifest["skills"]]}
