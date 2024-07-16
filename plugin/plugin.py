# Packages/LSP-gopls/plugin/plugin.py
import os

import sublime

from .version import VERSION
from .constants import GOPLS_BASE_URL
from .constants import RE_VER
from .constants import SESSION_NAME

from .utils import get_setting
from .utils import get_settings
from .utils import to_int
from .utils import is_binary_available
from .utils import run_go_command

from LSP.plugin import AbstractPlugin
from LSP.plugin import Session
from LSP.plugin import parse_uri
from LSP.plugin.core.typing import Any
from LSP.plugin.core.typing import Optional
from LSP.plugin.core.typing import Tuple
from LSP.plugin.core.typing import Mapping
from LSP.plugin.core.typing import Callable
from LSP.plugin.core.typing import List

try:
    import Terminus  # type: ignore
except ImportError:
    Terminus = None


def open_tests_in_terminus(
    session: Session,
    window: Optional[sublime.Window],
    arguments: Tuple[str, List[str], None],
) -> None:
    if not window:
        return

    if len(arguments) < 2:
        return

    if not (view := window.active_view()):
        return

    go_test_directory = os.path.dirname(parse_uri(arguments[0])[1])
    args = [go_test_directory]
    for test_command in arguments[1]:
        command_to_run = (
            ["go", "test"]
            + args
            + ["-v", "-count=1", "-run", "^{0}\\$".format(test_command)]
        )
        terminus_args = {
            "title": "Go Test",
            "cmd": command_to_run,
            "cwd": go_test_directory,
            "auto_close": get_setting(session, "closeTestResultsWhenFinished", False),
        }
        if get_setting(session, "runTestsInPanel", True):
            terminus_args["panel_name"] = "Go Test"
        window.run_command("terminus_open", terminus_args)


class Gopls(AbstractPlugin):
    @classmethod
    def name(cls):
        return SESSION_NAME

    @classmethod
    def basedir(cls) -> str:
        return os.path.join(cls.storage_path(), __package__.split(".")[0])

    @classmethod
    def server_version(cls) -> str:
        return VERSION

    @classmethod
    def current_server_version(cls) -> Optional[str]:
        try:
            with open(os.path.join(cls.basedir(), "VERSION"), "r") as fp:
                return fp.read()
        except OSError:
            return None

    @classmethod
    def _is_gopls_installed(cls) -> bool:
        binary = "gopls.exe" if sublime.platform() == "windows" else "gopls"
        command = [os.path.join(cls.basedir(), "bin", binary)]

        gopls_binary = sublime.expand_variables(
            command[0], {"storage_path": cls.storage_path()}
        )
        if sublime.platform() == "windows" and not gopls_binary.endswith(".exe"):
            gopls_binary = gopls_binary + ".exe"
        return is_binary_available(gopls_binary)

    @classmethod
    def _is_go_installed(cls) -> bool:
        return is_binary_available("go")

    @classmethod
    def _get_go_version(cls) -> Tuple[int, int, int]:
        stdout, stderr, return_code = run_go_command(
            sub_command="version", env_vars=cls._set_env_vars()
        )
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
    def needs_update_or_installation(cls) -> bool:
        is_managed = get_settings().get("settings", {}).get("manageGoplsBinary", True)
        if not is_managed:
            return False
        return not cls._is_gopls_installed() or (
            cls.server_version() != cls.current_server_version()
        )

    @classmethod
    def install_or_update(cls) -> None:
        if not cls._is_go_installed():
            raise ValueError("go binary not found in $PATH")

        os.makedirs(cls.basedir(), exist_ok=True)

        go_version = cls._get_go_version()
        go_sub_command = "get" if go_version < (1, 16, 0) else "install"
        _, stderr, return_code = run_go_command(
            sub_command=go_sub_command,
            url=GOPLS_BASE_URL.format(tag=VERSION),
            env_vars=cls._set_env_vars(),
        )
        if return_code != 0:
            raise ValueError("go installation error", stderr, "returncode", return_code)

        with open(os.path.join(cls.basedir(), "VERSION"), "w") as fp:
            fp.write(cls.server_version())

    def on_pre_server_command(
        self, command: Mapping[str, Any], done_callback: Callable[[], None]
    ) -> bool:
        if not Terminus:
            return False

        command_name = command["command"]
        if command_name in ("gopls.test"):
            if not (session := self.weaksession()):
                return False
            try:
                open_tests_in_terminus(
                    session, sublime.active_window(), command["arguments"]
                )
                done_callback()
                return True
            except Exception as ex:
                print("Exception handling command {}: {}".format(command_name, ex))
        return False
