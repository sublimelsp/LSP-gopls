# Packages/LSP-gopls/plugin.py

import sublime

from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin


class Gopls(AbstractPlugin):

    @classmethod
    def name(cls):
        return __package__

    @classmethod
    def configuration(cls):
        basename = "{}.sublime-settings".format(cls.name())
        filepath = "Packages/{}/{}".format(cls.name(), basename)
        return sublime.load_settings(basename), filepath

    # def on_pre_server_command(self, command, done_callback):
    #     name = command["command"]
    #     arguments = command["arguments"]
    #     if name == "foobar":
    #         # ... handle command foobar ...
    #         done_callback()
    #         return True  # we handled this command client-side
    #     return False  # we did not handle this command client-side


def plugin_loaded():
    register_plugin(Gopls)


def plugin_unloaded():
    unregister_plugin(Gopls)
