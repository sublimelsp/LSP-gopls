from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any
from typing import Callable
import os

from LSP.plugin import LspPlugin
from LSP.plugin import OnPreStartContext
from LSP.plugin import PluginStartError
from LSP.plugin import Promise
from LSP.plugin import ST_STORAGE_PATH
from LSP.plugin import Session
from LSP.plugin import command_handler
from LSP.plugin import parse_uri
import sublime

from .constants import GOPLS_BASE_URL
from .constants import PACKAGE_NAME
from .constants import RE_VER
from .types import GoplsRunTestsArgument
from .utils import get_setting
from .utils import get_settings
from .utils import is_binary_available
from .utils import run_go_command
from .utils import to_int
from .version import VERSION

try:
    import Terminus  # type: ignore
except ImportError:
    Terminus = None


def open_tests_in_terminus(
    session: Session,
    window: sublime.Window | None,
    arguments: list[GoplsRunTestsArgument],
) -> None:
    if not window:
        return

    if (arguments[0]["Tests"] is None) or (not arguments[0]["Tests"]):
        return

    if not (view := window.active_view()):
        return

    uri = arguments[0]["URI"]
    filepath = parse_uri(uri)
    go_test_directory = str(Path(filepath[1]).parent)
    args = [go_test_directory]
    for test_command in arguments[0]["Tests"]:
        command_to_run = ["go", "test"] + args + ["-v", "-count=1", "-run", "^{0}\\$".format(test_command)]
        terminus_args = {
            "title": "Go Test",
            "cmd": command_to_run,
            "cwd": go_test_directory,
            "auto_close": get_setting(session, "closeTestResultsWhenFinished", False),
        }
        if get_setting(session, "runTestsInPanel", True):
            terminus_args["panel_name"] = "Go Test"
        window.run_command("terminus_open", terminus_args)


class Gopls(LspPlugin):
    @classmethod
    def basedir(cls) -> str:
        return os.path.join(ST_STORAGE_PATH, PACKAGE_NAME)

    @classmethod
    def server_version(cls) -> str:
        return VERSION

    @classmethod
    def current_server_version(cls) -> str | None:
        try:
            with open(os.path.join(cls.basedir(), "VERSION"), "r") as fp:
                return fp.read()
        except OSError:
            return None

    @classmethod
    def _is_gopls_installed(cls) -> bool:
        binary = "gopls.exe" if sublime.platform() == "windows" else "gopls"
        command = [os.path.join(cls.basedir(), "bin", binary)]

        gopls_binary = str(sublime.expand_variables(command[0], {"storage_path": cls.basedir()}))

        if sublime.platform() == "windows" and not gopls_binary.endswith(".exe"):
            gopls_binary = gopls_binary + ".exe"

        return is_binary_available(gopls_binary)

    @classmethod
    def _is_go_installed(cls) -> bool:
        return is_binary_available("go")

    @classmethod
    def _get_go_version(cls) -> tuple[int, int, int]:
        stdout, stderr, return_code = run_go_command(sub_command="version", env_vars=cls._set_env_vars())
        if return_code != 0:
            raise ValueError("go version error", stderr, "returncode", return_code)

        if stdout == "":
            return (0, 0, 0)

        matches = RE_VER.search(stdout)
        if matches is None:
            return (0, 0, 0)
        return (
            to_int(matches.group(1)),
            to_int(matches.group(2)),
            to_int(matches.group(3)),
        )

    @classmethod
    def _set_env_vars(cls) -> dict:
        env_vars = dict(os.environ)
        env_vars["GO111MODULE"] = "on"
        env_vars["GOPATH"] = cls.basedir()
        env_vars["GOBIN"] = os.path.join(cls.basedir(), "bin")
        env_vars["GOCACHE"] = os.path.join(cls.basedir(), "go-build")
        return env_vars

    @classmethod
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        is_managed = get_settings().get("settings", {}).get("manageGoplsBinary", True)
        if is_managed and (not cls._is_gopls_installed() or (cls.server_version() != cls.current_server_version())):
            if not cls._is_go_installed():
                raise PluginStartError("go binary not found in $PATH")

            os.makedirs(cls.basedir(), exist_ok=True)

            go_version = cls._get_go_version()
            go_sub_command = "get" if go_version < (1, 16, 0) else "install"
            _, stderr, return_code = run_go_command(
                sub_command=go_sub_command,
                url=GOPLS_BASE_URL.format(tag=VERSION),
                env_vars=cls._set_env_vars(),
            )
            if return_code != 0:
                raise PluginStartError(f"go installation error with return code {return_code}: {stderr}")

            with open(os.path.join(cls.basedir(), "VERSION"), "w") as fp:
                fp.write(cls.server_version())

    @command_handler("gopls.run_tests")
    def on_gopls_run_tests(self, arguments: list[GoplsRunTestsArgument] | None) -> Promise[None]:
        if not Terminus or not arguments:
            return Promise.resolve(None)

        if not (session := self.weaksession()):
            return Promise.resolve(None)
        try:
            return Promise.resolve(open_tests_in_terminus(session, sublime.active_window(), arguments))
        except Exception as ex:
            print("Exception handling `gopls.run_tests` {}: {}".format(ex))

        return Promise.resolve(None)
