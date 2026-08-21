from __future__ import annotations

from pathlib import Path
import os

from LSP.plugin import LspPlugin
from LSP.plugin import OnPreStartContext
from LSP.plugin import PluginStartError
from LSP.plugin import Promise
from LSP.plugin import Session
from LSP.plugin import command_handler
from LSP.plugin import parse_uri
import sublime

from .constants import GOPLS_BASE_URL
from .constants import RE_VER
from .types import GoplsRunTestsArgument
from .utils import get_setting
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

    if not window.active_view():
        return

    uri = arguments[0]["URI"]
    filepath = parse_uri(uri)
    go_test_directory = str(Path(filepath[1]).parent)
    args = [go_test_directory]
    for test_command in arguments[0]["Tests"]:
        command_to_run = ["go", "test"] + args + ["-v", "-count=1", "-run", f"^{test_command}\\$"]
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
    def server_version(cls) -> str:
        return VERSION

    @classmethod
    def current_server_version(cls) -> str | None:
        try:
            return Path(cls.plugin_storage_path, "VERSION").read_text()
        except OSError:
            return None

    @classmethod
    def _is_gopls_installed(cls) -> bool:
        binary = "gopls.exe" if sublime.platform() == "windows" else "gopls"
        command = str(Path(cls.plugin_storage_path, "bin", binary))
        gopls_binary = str(sublime.expand_variables(command, {"storage_path": str(cls.plugin_storage_path)}))

        if sublime.platform() == "windows" and not gopls_binary.endswith(".exe"):
            gopls_binary = gopls_binary + ".exe"

        return is_binary_available(gopls_binary)

    @classmethod
    def _get_go_version(cls) -> tuple[int, int, int]:
        stdout, stderr, return_code = run_go_command(sub_command="version", env_vars=cls._go_runtime_env_vars())
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
    def _go_runtime_env_vars(cls) -> dict:
        env_vars = dict(os.environ)
        env_vars["GO111MODULE"] = "on"
        env_vars["GOPATH"] = str(cls.plugin_storage_path)
        env_vars["GOBIN"] = str(Path(cls.plugin_storage_path, "bin"))
        env_vars["GOCACHE"] = str(Path(cls.plugin_storage_path, "go-build"))
        return env_vars

    @classmethod
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        is_managed = context.configuration.settings.get("manageGoplsBinary", True)
        if is_managed and (not cls._is_gopls_installed() or (cls.server_version() != cls.current_server_version())):
            if not is_binary_available("go"):
                raise PluginStartError("go binary not found in $PATH")

            os.makedirs(cls.plugin_storage_path, exist_ok=True)

            go_version = cls._get_go_version()
            go_sub_command = "get" if go_version < (1, 16, 0) else "install"
            _, stderr, return_code = run_go_command(
                sub_command=go_sub_command,
                url=GOPLS_BASE_URL.format(tag=VERSION),
                env_vars=cls._go_runtime_env_vars(),
            )
            if return_code != 0:
                raise PluginStartError(f"go installation error with return code {return_code}: {stderr}")

            Path(cls.plugin_storage_path, "VERSION").write_text(cls.server_version())

    @command_handler("gopls.run_tests")
    def on_gopls_run_tests(self, arguments: list[GoplsRunTestsArgument] | None) -> Promise[None]:
        if not Terminus or not arguments:
            return Promise.resolve(None)

        if not (session := self.weaksession()):
            return Promise.resolve(None)
        try:
            return Promise.resolve(open_tests_in_terminus(session, sublime.active_window(), arguments))
        except Exception as ex:
            print(f"Exception handling command `gopls.run_tests`: {ex}")

        return Promise.resolve(None)
