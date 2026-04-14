from __future__ import annotations

from shutil import which
from typing import Any
import subprocess
import tempfile
import textwrap

from LSP.plugin import Session
import sublime

from .constants import SETTINGS


def get_setting(
    session: Session,
    key: str,
    default: str | bool | list[str] | None = None,
) -> Any:
    value = session.config.settings.get(key)
    if value is None:
        return default
    return value


def get_settings():
    return sublime.load_settings(SETTINGS)


def run_go_command(
    env_vars: dict,
    sub_command: str = "install",
    url: str | None = None,
) -> tuple[str, str, int]:
    startupinfo = None
    if sublime.platform() == "windows":
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW  # type: ignore

    cmd = ["go", sub_command]
    if url is not None:
        cmd.append(url)

    with tempfile.TemporaryDirectory() as tempdir:
        env_vars["GOTMPDIR"] = tempdir
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env_vars,
            universal_newlines=True,
            startupinfo=startupinfo,
        )
        stdout, stderr = process.communicate()
    return (
        stdout,
        stderr,
        process.returncode,
    )


def is_binary_available(path) -> bool:
    return bool(which(path))


def reformat(text: str) -> str:
    return textwrap.dedent(text).strip()


def to_int(value: str | None) -> int:
    if value is None:
        return 0
    return int(value)
