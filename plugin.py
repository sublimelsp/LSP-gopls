# Packages/LSP-gopls/plugin.py

import sublime

from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin
from LSP.plugin.core.typing import Any, Optional, Tuple, Mapping, Callable, List, Union

from shutil import which
import subprocess
import tempfile
import os
import re

try:
    import Terminus  # type: ignore
except ImportError:
    Terminus = None

# {'command': 'gopls.test', 'arguments': ['file:///Users/zacharyschulze/Library/Application%20Support/Sublime%20Text/Packages/LSP-gopls/test_data/mmath/math_test.go', ['TestAdd'], None], 'workDoneToken': 'wd6'}

'''
Current version of gopls that the plugin installs
Review gopls settings when updating TAG to see if
new settings exist
'''
TAG = '0.8.4'
GOPLS_BASE_URL = 'golang.org/x/tools/gopls@v{tag}'

RE_VER = re.compile(r'go(\d+)\.(\d+)(?:\.(\d+))?')


def open_tests_in_terminus(window: Optional[sublime.Window], arguments: List) -> None:
    if len(arguments) != 3:
        return

    if not window:
        return

    view = window.active_view()
    if not view:
        return

    if not Terminus:
        sublime.error_message(
            'Cannot run executable. You need to install the \'Terminus\' package and then restart Sublime Text')
        return

    go_test_directory = os.path.dirname(arguments[0]).lstrip('file:').replace('%20', ' ')
    args = [go_test_directory]
    for test_command in arguments[1]:
        runnable_args = args
        runnable_args.extend(['-v', '-count=1', '-run', '^{0}$'.format(test_command)])
        command_to_run = ['go', 'test']
        command_to_run.extend(runnable_args)

        terminus_args = {
            'title': 'Go Test',
            'cmd': command_to_run,
            'cwd': go_test_directory,
            'auto_close': get_setting(view, 'gopls.terminusAutoClose', False)
        }
        if get_setting(view, 'gopls.terminusUsePanel', True):
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
        except:
            return None

    @classmethod
    def _is_gopls_installed(cls) -> bool:
        binary = 'gopls.exe' if sublime.platform() == 'windows' else 'gopls'
        command = get_setting(None,
            'command', [os.path.join(cls.basedir(), 'bin', binary)]
        )
        gopls_binary = command[0].replace('${storage_path}', cls.storage_path())
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
        command_name = command['command']
        try:
            session = self.weaksession()
            if not session:
                return False
            if command_name in ('gopls.test'):
                open_tests_in_terminus(sublime.active_window(), command['arguments'])
                done_callback()
                return True
            else:
                return False
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


def to_int(value: Optional[str]) -> int:
    if value is None:
        return 0
    return int(value)


def _is_binary_available(path) -> bool:
    return bool(which(path))

def get_setting(view: sublime.View = None, key: str = '', default: Optional[Union[str, bool, List[str]]] = None) -> Any:
    if view:
        settings = view.settings()
        if settings.has(key):
            return settings.get(key)
    settings = sublime.load_settings('LSP-gopls.sublime-settings').get('settings', {})
    return settings.get(key, default)


def plugin_loaded():
    register_plugin(Gopls)


def plugin_unloaded():
    unregister_plugin(Gopls)
