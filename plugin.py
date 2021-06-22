# Packages/LSP-gopls/plugin.py

from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin


class Gopls(AbstractPlugin):

    @classmethod
    def name(cls):
        return "gopls"


def plugin_loaded():
    register_plugin(Gopls)


def plugin_unloaded():
    unregister_plugin(Gopls)
