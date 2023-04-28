import sublime

import textwrap
from shutil import which
import subprocess
import tempfile

from LSP.plugin import Session
from LSP.plugin.core.typing import Optional
from LSP.plugin.core.typing import Union
from LSP.plugin.core.typing import List
from LSP.plugin.core.typing import Any
from LSP.plugin.core.typing import Tuple

from .constants import SETTINGS


def get_setting(
    session: Session,
    key: str,
    default: Optional[Union[str, bool, List[str]]] = None,
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
    url: Optional[str] = None,
) -> Tuple[str, str, int]:
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


def to_int(value: Optional[str]) -> int:
    if value is None:
        return 0
    return int(value)
