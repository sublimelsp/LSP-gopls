from __future__ import annotations

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
    Gopls.register()


def plugin_unloaded():
    Gopls.unregister()
