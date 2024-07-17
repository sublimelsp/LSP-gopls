import sublime
import sublime_plugin

from .types import GoplsStartDebuggingResponse
from .constants import SESSION_NAME

from LSP.plugin import LspTextCommand
from LSP.plugin import Request
from LSP.plugin.core.typing import Optional


class GoplsCommand(LspTextCommand):
    session_name = SESSION_NAME


class GoplsOpenFileCommand(sublime_plugin.WindowCommand):
    def run(self, uri: str) -> None:
        self.window.open_file(uri, sublime.ENCODED_POSITION)


class GoplsStartDebuggingCommand(GoplsCommand):
    """
    The GoplsStartDebuggingCommand class is a subclass of GoplsCommand and is
    responsible for starting a debug session for the current Go language server
    session. The command sends a request to the language server to start the
    debugging session and displays a message dialog with the port(s) on which
    the debug session(s) was started. If the debug session(s) was not
    successfully started, a message dialog is displayed saying "No debug session
    started".
    """

    def run(self, _: sublime.Edit) -> None:
        session = self.session_by_name(self.session_name)
        if session is None:
            return

        session.send_request(
            Request(
                "workspace/executeCommand",
                {"command": "gopls.start_debugging", "arguments": [{}]},
            ),
            on_result=lambda x: self.show_results_async(x),
        )

    def show_results_async(
        self, response: Optional[GoplsStartDebuggingResponse]
    ) -> None:
        if response is None or len(response["URLs"]) == 0:
            sublime.message_dialog("No debug session started")
            return

        sublime.message_dialog(
            "Debug session started on port(s):\n{port}".format(
                port="\t{url}\n".join(response["URLs"])
            )
        )
