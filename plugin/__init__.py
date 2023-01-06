
from .commands import (
    GoplsOpenFileCommand,
    GoplsRunVulnCheckCommand,
    )

from LSP.plugin import (
    register_plugin,
    unregister_plugin,
)

from .plugin import Gopls

__all__ = (
    # ST: Core
    'plugin_loaded',
    'plugin_unloaded',

    # ST: commands
    'GoplsOpenFileCommand',
    'GoplsRunVulnCheckCommand',
    )

def plugin_loaded():
    register_plugin(Gopls)


def plugin_unloaded():
    unregister_plugin(Gopls)
