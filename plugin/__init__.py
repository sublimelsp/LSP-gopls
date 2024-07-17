from LSP.plugin import register_plugin
from LSP.plugin import unregister_plugin

from .commands import GoplsOpenFileCommand
from .commands import GoplsStartDebuggingCommand
from .plugin import Gopls

__all__ = (
    # ST: Core
    "plugin_loaded",
    "plugin_unloaded",
    # ST: commands
    "GoplsOpenFileCommand",
    "GoplsStartDebuggingCommand",
)


def plugin_loaded():
    register_plugin(Gopls)


def plugin_unloaded():
    unregister_plugin(Gopls)
