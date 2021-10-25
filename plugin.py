# Packages/LSP-gopls/plugin.py

import sublime

from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin
from LSP.plugin.core.typing import Any

from shutil import which
import subprocess
import os

'''
Current version of gopls that the plugin installs
Review gopls settings when updating TAG to see if
new settings exist
'''
TAG = "v0.7.3"
GOPLS_BASE_URL = 'golang.org/x/tools/gopls@{tag}'


class Gopls(AbstractPlugin):

    @classmethod
    def name(cls):
        return "gopls"

    @classmethod
    def basedir(cls) -> str:
        return os.path.join(cls.storage_path(), __package__)

    @classmethod
    def server_version(cls) -> str:
        return TAG

    @classmethod
    def current_server_version(cls) -> str:
        try:
            with open(os.path.join(cls.basedir(), "VERSION"), "r") as fp:
                return fp.read()
        except OSError as ex:
            raise ex

    @classmethod
    def _is_gopls_installed(cls) -> bool:
        gopls_binary = get_setting(
            'command', [os.path.join(cls.basedir(), 'bin', 'gopls')])
        return _is_binary_available(gopls_binary[0])

    @classmethod
    def _is_go_installed(cls) -> bool:
        return _is_binary_available('go')

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        try:
            return not cls._is_gopls_installed() or (cls.server_version() != cls.current_server_version())
        except OSError:
            return True

    @classmethod
    def install_or_update(cls) -> None:
        try:
            if not cls._is_go_installed():
                raise ValueError('go binary not found in $PATH')

            os.makedirs(cls.basedir(), exist_ok=True)

            go_binary = str(which('go'))
            process = subprocess.Popen([go_binary, 'install', GOPLS_BASE_URL.format(tag=TAG)],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       env={
                                       'GO111MODULE': 'on',
                                       'GOPATH': cls.basedir(),
                                       'GOBIN': os.path.join(cls.basedir(), 'bin'),
                                       'GOCACHE': os.path.join(cls.basedir(), 'go-build')
                                       })
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise ValueError(
                    'go installation error', stderr, 'returncode', process.returncode)

            with open(os.path.join(cls.basedir(), "VERSION"), "w") as fp:
                fp.write(cls.server_version())

        except Exception as ex:
            raise ValueError(ex)


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
