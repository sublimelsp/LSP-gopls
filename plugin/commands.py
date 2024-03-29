
import os

import sublime
import sublime_plugin

from .types import GoplsVulnerabilities
from .types import GoplsStartDebuggingResponse
from .vulnerabilities import Vulnerabilities
from .constants import SESSION_NAME

from LSP.plugin import LspTextCommand
from LSP.plugin import Request
from LSP.plugin.core.typing import Optional
from LSP.plugin.core.views import uri_from_view

class GoplsCommand(LspTextCommand):
    session_name = SESSION_NAME


class GoplsOpenFileCommand(sublime_plugin.WindowCommand):
    def run(self, uri: str) -> None:
        self.window.open_file(uri, sublime.ENCODED_POSITION)


class GoplsRunVulnCheckCommand(GoplsCommand):
    '''
    The GoplsRunVulnCheckCommand class is a subclass of GoplsCommand and is
    responsible for running a vulnerability check on the workspace folders of a
    Go language server session. If there is only one workspace folder, the
    vulnerability check is run on that folder. If there are multiple workspace
    folders, a quick panel is displayed for the user to choose which folder to
    run the vulnerability check on. If there are no workspace folders, the
    vulnerability check is run on the directory of the current view. The results
    of the vulnerability check are then displayed in a Vulnerabilities object.
    '''
    def run(self, _: sublime.Edit) -> None:
        session = self.session_by_name(self.session_name)
        if session is None:
            return

        view = self.view
        if not view:
            return

        folders = session.get_workspace_folders()
        if len(folders) < 1:
            path = os.path.dirname(uri_from_view(self.view))
            self.run_gopls_vulncheck(path)
        elif len(folders) == 1:
            self.run_gopls_vulncheck(folders[0].uri())
        else:
            window = self.view.window()
            if not window:
                return
            window.show_quick_panel(
                [
                    sublime.QuickPanelItem(folder.name, folder.uri())
                    for folder in folders
                ],
                on_select=lambda x: self.run_gopls_vulncheck(folders[x].uri()) if x != -1 else None,
            )

    def run_gopls_vulncheck(self, path: str) -> None:
        session = self.session_by_name(self.session_name)
        if session is None:
            return

        session.send_request(
            Request(
                'workspace/executeCommand',
                # TODO(@TerminalFi): Investigate other ways to run the vulncheck.
                {'command': 'gopls.run_govulncheck', 'arguments': [{'uri': '{0}/...'.format(path)}]},
            ),
            on_result=lambda x: self.show_results_async(x.get('Vuln')),
        )

    def show_results_async(
        self, vulnerabilities: Optional[GoplsVulnerabilities]
    ) -> None:
        if vulnerabilities is None:
            sublime.message_dialog('No vulnerabilities found')
            return

        Vulnerabilities(
            window=self.view.window(), vulnerabilities=vulnerabilities
        ).show()


class GoplsStartDebuggingCommand(GoplsCommand):
    '''
    The GoplsStartDebuggingCommand class is a subclass of GoplsCommand and is
    responsible for starting a debug session for the current Go language server
    session. The command sends a request to the language server to start the
    debugging session and displays a message dialog with the port(s) on which
    the debug session(s) was started. If the debug session(s) was not
    successfully started, a message dialog is displayed saying "No debug session
    started".
    '''
    def run(self, _: sublime.Edit) -> None:
        session = self.session_by_name(self.session_name)
        if session is None:
            return

        session.send_request(
            Request(
                'workspace/executeCommand',
                {'command': 'gopls.start_debugging', 'arguments': [{}]},
            ),
            on_result=lambda x: self.show_results_async(x),
        )

    def show_results_async(self, response: Optional[GoplsStartDebuggingResponse]) -> None:
        if response is None or len(response['URLs']) == 0:
            sublime.message_dialog('No debug session started')
            return

        sublime.message_dialog(
            'Debug session started on port(s):\n{port}'.format(port='\t{url}\n'.join(response['URLs']))
        )
