"""Resolve local Codex installations and emit only credential-safe setup errors."""
import os
from pathlib import Path
import platform
import shutil
import sys

from .protocol import ProtocolError


class CodexSetupError(ProtocolError):
    """Only trusted, fixed diagnostic messages may use this exception type."""


def executable_command():
    explicit = os.environ.get("FAGENT_CODEX_BIN")
    if explicit:
        if not Path(explicit).is_file():
            raise CodexSetupError("FAGENT_CODEX_BIN must point to an existing Codex executable.")
        return [str(Path(explicit).resolve())]
    executable = shutil.which("codex.exe") if sys.platform == "win32" else None
    executable = executable or shutil.which("codex")
    if executable:
        if Path(executable).suffix.lower() not in (".cmd", ".bat", ".ps1"):
            return [executable]
        script = Path(executable).parent / "node_modules/@openai/codex/bin/codex.js"
        node = shutil.which("node")
        if node and script.is_file():
            return [node, str(script)]
    if sys.platform == "win32":
        profile = os.environ.get("USERPROFILE")
        local = os.environ.get("LOCALAPPDATA")
        standalone = Path(local) / "Programs/OpenAI/Codex/bin/codex.exe" if local else None
        if standalone and standalone.is_file():
            return [str(standalone)]
        arch = "aarch64" if platform.machine().lower() in ("arm64", "aarch64") else "x86_64"
        extensions = Path(profile) / ".vscode/extensions" if profile else None
        if extensions and extensions.is_dir():
            candidates = list(extensions.glob(f"openai.chatgpt-*/bin/windows-{arch}/codex.exe"))
            if candidates:
                return [str(max(candidates, key=lambda path: path.stat().st_mtime))]
    raise CodexSetupError("Codex CLI was not found. Install it or set FAGENT_CODEX_BIN, then restart the server.")


def existing_home(env):
    """Supply an explicit existing home when native Windows home lookup fails."""
    configured = env.get("CODEX_HOME")
    if configured:
        if not Path(configured).is_dir():
            raise CodexSetupError("CODEX_HOME does not exist. Correct it and restart the server.")
        return configured
    profile = env.get("USERPROFILE") if sys.platform == "win32" else env.get("HOME")
    home = Path(profile) / ".codex" if profile else None
    if home and home.is_dir():
        return str(home)
    raise CodexSetupError("No Codex home was found. Run codex login in your terminal, or enter an API key.")
