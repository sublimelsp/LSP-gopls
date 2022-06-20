# Packages/LSP-gopls/plugin.py

import sublime

from LSP.plugin import AbstractPlugin, Session, parse_uri, register_plugin, unregister_plugin
from LSP.plugin.core.typing import Any, Optional, Tuple, Mapping, Callable, List, Union
from LSP.plugin.core.registry import LspTextCommand
from LSP.plugin.core.views import uri_from_view
from LSP.plugin import Request

from shutil import which
import subprocess
import tempfile
import os
import re

try:
    import Terminus  # type: ignore
except ImportError:
    Terminus = None

'''
Current version of gopls that the plugin installs
Review gopls settings when updating TAG to see if
new settings exist
'''
TAG = '0.8.4'
GOPLS_BASE_URL = 'golang.org/x/tools/gopls@v{tag}'

RE_VER = re.compile(r'go(\d+)\.(\d+)(?:\.(\d+))?')

SESSION_NAME = 'gopls'

def open_tests_in_terminus(
    session: Session, window: Optional[sublime.Window], arguments: Tuple[str, List[str], None]
) -> None:
    if not window:
        return

    if len(arguments) < 2:
        return

    view = window.active_view()
    if not view:
        return

    go_test_directory = os.path.dirname(parse_uri(arguments[0])[1])
    args = [go_test_directory]
    for test_command in arguments[1]:
        command_to_run = ['go', 'test'] + args + ['-v', '-count=1', '-run', '^{0}\\$'.format(test_command)]
        terminus_args = {
            'title': 'Go Test',
            'cmd': command_to_run,
            'cwd': go_test_directory,
            'auto_close': get_setting(session, 'closeTestResultsWhenFinished', False)
        }
        if get_setting(session, 'runTestsInPanel', True):
            terminus_args['panel_name'] = 'Go Test'
        window.run_command('terminus_open', terminus_args)


class Gopls(AbstractPlugin):
    @classmethod
    def name(cls):
        return 'gopls'

    @classmethod
    def basedir(cls) -> str:
        return os.path.join(cls.storage_path(), __package__)

    @classmethod
    def server_version(cls) -> str:
        return TAG

    @classmethod
    def current_server_version(cls) -> Optional[str]:
        try:
            with open(os.path.join(cls.basedir(), 'VERSION'), 'r') as fp:
                return fp.read()
        except OSError:
            return None

    @classmethod
    def _is_gopls_installed(cls) -> bool:
        binary = 'gopls.exe' if sublime.platform() == 'windows' else 'gopls'
        command = [os.path.join(cls.basedir(), 'bin', binary)]

        gopls_binary = sublime.expand_variables(command[0], {'storage_path': cls.storage_path()})
        if sublime.platform() == 'windows' and not gopls_binary.endswith('.exe'):
            gopls_binary = gopls_binary + '.exe'
        return _is_binary_available(gopls_binary)

    @classmethod
    def _is_go_installed(cls) -> bool:
        return _is_binary_available('go')

    @classmethod
    def _get_go_version(cls) -> Tuple[int, int, int]:
        stdout, stderr, return_code = run_go_command(
            sub_command='version',
            env_vars=cls._set_env_vars())
        if return_code != 0:
            raise ValueError(
                'go version error', stderr, 'returncode', return_code)

        if stdout == '':
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
        env_vars['GO111MODULE'] = 'on'
        env_vars['GOPATH'] = cls.basedir()
        env_vars['GOBIN'] = os.path.join(cls.basedir(), 'bin')
        env_vars['GOCACHE'] = os.path.join(cls.basedir(), 'go-build')
        return env_vars

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        return not cls._is_gopls_installed() or (
            cls.server_version() != cls.current_server_version()
        )

    @classmethod
    def install_or_update(cls) -> None:
        if not cls._is_go_installed():
            raise ValueError('go binary not found in $PATH')

        os.makedirs(cls.basedir(), exist_ok=True)

        go_version = cls._get_go_version()
        go_sub_command = 'get' if go_version < (1, 16, 0) else 'install'
        _, stderr, return_code = run_go_command(
            sub_command=go_sub_command,
            url=GOPLS_BASE_URL.format(tag=TAG),
            env_vars=cls._set_env_vars(),
        )
        if return_code != 0:
            raise ValueError(
                'go installation error', stderr, 'returncode', return_code)

        with open(os.path.join(cls.basedir(), 'VERSION'), 'w') as fp:
            fp.write(cls.server_version())

    def on_pre_server_command(self, command: Mapping[str, Any], done_callback: Callable[[], None]) -> bool:
        if not Terminus:
            return False

        command_name = command['command']
        if command_name in ('gopls.test'):
            session = self.weaksession()
            if not session:
                return False
            try:
                open_tests_in_terminus(session, sublime.active_window(), command['arguments'])
                done_callback()
                return True
            except Exception as ex:
                print('Exception handling command {}: {}'.format(command_name, ex))
        return False


def run_go_command(
    env_vars: dict,
    sub_command: str = 'install',
    url: Optional[str] = None,
) -> Tuple[str, str, int]:
    startupinfo = None
    if sublime.platform() == 'windows':
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW  # type: ignore

    cmd = ['go', sub_command]
    if url is not None:
        cmd.append(url)

    with tempfile.TemporaryDirectory() as tempdir:
        env_vars['GOTMPDIR'] = tempdir
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


class GoplsCommand(LspTextCommand):
    session_name = SESSION_NAME


class GoplsRunVulnCheckCommand(GoplsCommand):
    def run(self, edit: sublime.Edit, workspace: bool = False) -> None:
        self.edit = edit
        session = self.session_by_name(self.session_name)
        if session is None:
            return

        view = self.view
        if not view:
            return

        if workspace:
            window = self.view.window()
            if not window:
                return

            folders = session.get_workspace_folders()
            window.show_quick_panel(
                [
                    sublime.QuickPanelItem(folder.name, folder.uri()) for folder in folders
                ], on_select=lambda x: self.run_gopls_vulncheck(folders[x].uri()) if x != -1 else None)
        else:
            path = os.path.dirname(uri_from_view(self.view))
            self.run_gopls_vulncheck(path)

    def run_gopls_vulncheck(self, path: str) -> None:
        session = self.session_by_name(self.session_name)
        if session is None:
            return

        session.send_request(Request('workspace/executeCommand',
            {'command': 'gopls.run_vulncheck_exp','arguments': [{'dir': path}]}
            ), on_result=lambda x: self.show_results_async(x.get('Vuln')))

    def show_results_async(self, content: str) -> None:
        window = self.view.window()
        if not window:
            # default to console
            print(content)
            return

        if content is not None:
            self.panel = window.create_output_panel('gopls.command_results')
            self.panel.insert(self.edit, 0, content)
            self.panel.set_read_only(True)
            window.run_command('show_panel', { 'panel': 'gopls.command_results' })


def to_int(value: Optional[str]) -> int:
    if value is None:
        return 0
    return int(value)


def _is_binary_available(path) -> bool:
    return bool(which(path))


def get_setting(session: Session, key: str, default: Optional[Union[str, bool, List[str]]] = None) -> Any:
    value = session.config.settings.get(key)
    if value is None:
        return default

    return value


def plugin_loaded():
    register_plugin(Gopls)


def plugin_unloaded():
    unregister_plugin(Gopls)
