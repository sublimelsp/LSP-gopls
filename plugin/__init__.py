
from .commands import GoplsOpenFileCommand
from .commands import GoplsStartDebuggingCommand
from .commands import GoplsRunVulnCheckCommand
from .plugin import Gopls

from LSP.plugin import register_plugin
from LSP.plugin import unregister_plugin


__all__ = (
    # ST: Core
    'plugin_loaded',
    'plugin_unloaded',

    # ST: commands
    'GoplsOpenFileCommand',
    'GoplsStartDebuggingCommand',
    'GoplsRunVulnCheckCommand',
    )

def plugin_loaded():
    register_plugin(Gopls)


def plugin_unloaded():
    unregister_plugin(Gopls)
