"""Installation/home regressions without reading or changing real credentials."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fagent.codex_setup import CodexSetupError, executable_command, existing_home


class CodexSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def touch(self, relative):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return path

    def test_existing_home_uses_windows_profile_without_native_lookup(self):
        home = self.root / ".codex"
        home.mkdir()
        with patch("fagent.codex_setup.sys.platform", "win32"):
            self.assertEqual(existing_home({"USERPROFILE": str(self.root)}), str(home))

    def test_explicit_home_is_honored_and_invalid_override_is_not_ignored(self):
        self.assertEqual(existing_home({"CODEX_HOME": str(self.root)}), str(self.root))
        with self.assertRaisesRegex(CodexSetupError, "CODEX_HOME does not exist"):
            existing_home({"CODEX_HOME": str(self.root / "missing")})

    def test_missing_home_has_login_guidance(self):
        with self.assertRaisesRegex(CodexSetupError, "codex login"):
            existing_home({})

    def test_windows_vscode_extension_when_codex_is_not_on_path(self):
        binary = self.touch(".vscode/extensions/openai.chatgpt-26.1/bin/windows-x86_64/codex.exe")
        with patch.dict(os.environ, {"USERPROFILE": str(self.root)}, clear=True), \
                patch("fagent.codex_setup.sys.platform", "win32"), \
                patch("fagent.codex_setup.platform.machine", return_value="AMD64"), \
                patch("fagent.codex_setup.shutil.which", return_value=None):
            self.assertEqual(executable_command(), [str(binary)])

    def test_explicit_binary_and_missing_binary_guidance(self):
        binary = self.touch("codex.exe")
        with patch.dict(os.environ, {"FAGENT_CODEX_BIN": str(binary)}, clear=True):
            self.assertEqual(executable_command(), [str(binary.resolve())])
        with patch.dict(os.environ, {}, clear=True), \
                patch("fagent.codex_setup.shutil.which", return_value=None):
            with self.assertRaisesRegex(CodexSetupError, "CLI was not found"):
                executable_command()

    def test_npm_windows_shim_runs_node_without_shell(self):
        shim = self.touch("codex.cmd")
        script = self.touch("node_modules/@openai/codex/bin/codex.js")

        def which(name):
            return {"codex": str(shim), "node": "node.exe"}.get(name)
        with patch.dict(os.environ, {}, clear=True), \
                patch("fagent.codex_setup.shutil.which", side_effect=which):
            self.assertEqual(executable_command(), ["node.exe", str(script)])
