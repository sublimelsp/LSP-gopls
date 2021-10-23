# Packages/LSP-gopls/plugin.py

import sublime

from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin
from LSP.plugin.core.typing import Any

from shutil import which, rmtree
import subprocess
import os


class Gopls(AbstractPlugin):

    @classmethod
    def name(cls):
        return "gopls"

    @classmethod
    def basedir(cls) -> str:
        return os.path.join(cls.storage_path(), __package__)

    @classmethod
    def _is_gopls_installed(cls) -> bool:
        gopls_binary = get_setting('command', [os.path.join(cls.basedir(), 'bin', 'gopls')])
        return _is_binary_available(gopls_binary[0])

    @classmethod
    def _is_go_installed(cls) -> bool:
        return _is_binary_available('go')

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        try:
            return not cls._is_gopls_installed()
        except OSError:
            return True

    @classmethod
    def install_or_update(cls) -> None:
        try:
            if not cls._is_go_installed():
                sublime.error_message('golang not installed')
                return

            if os.path.isdir(cls.basedir()):
                rmtree(cls.basedir())

            os.makedirs(cls.basedir(), exist_ok=True)

            go_binary = str(which('go'))
            process = subprocess.Popen([go_binary, 'install', "golang.org/x/tools/gopls@latest"],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       env={
                                       'GOPATH': cls.basedir(),
                                       'GOBIN': os.path.join(cls.basedir(), 'bin'),
                                       'GOCACHE': os.path.join(cls.basedir(), 'go-build')
                                       })
            _, stderr = process.communicate()
            if stderr:
                sublime.error_message(str(stderr))
        except Exception:
            rmtree(cls.basedir(), ignore_errors=True)
            raise


def _is_binary_available(path) -> bool:
    return bool(which(path))


def get_setting(key: str, default=None) -> Any:
    settings = sublime.load_settings(
        'LSP-gopls.sublime-settings').get("settings", {})
    return settings.get(key, default)


def plugin_loaded():
    register_plugin(Gopls)


def plugin_unloaded():
    unregister_plugin(Gopls)
