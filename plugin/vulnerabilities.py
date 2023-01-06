import sublime

from .types import GoplsVulnerabilities, GoplsVulnCallStack
from .utils import reformat
from LSP.plugin.core.typing import Optional, List
from LSP.plugin import parse_uri

import mdpopups


class Vulnerabilities:
    PANEL_NAME = 'gopls.vulnerabilities'
    CSS = reformat(
        '''
        strong {
            color: var(--yellowish)
        }
        .call {
            color: var(--greenish)
        }

        h4 {
            color: var(--purplish)
        }
        '''
    )
    VULN_HEADER = reformat(
        '''
        <h4 style="color: var(--redish);" >Found {vuln_count} known vulnerabilities</h4>
        <br>
    '''
    )
    VULN_TEMPLATE = reformat(
        '''
        <h2><a title="Open vulnerability details" href="{url}">{id}</a></h2>
        <br>
        {details}
        <br>


        <strong>Package</strong>: `{pkg_path}`
        <strong>Found in Version</strong>: <a href="https://pkg.go.dev/{pkg_path}@{current_version}">{pkg_path}@{current_version}</a>
        <strong>Fixed Version</strong>: <a href="https://pkg.go.dev/{pkg_path}@{fixed_version}">{pkg_path}@{fixed_version}</a>
        <strong>Aliases</strong>:

        <ul>
        {aliases}
        </ul>

        <strong>CallStack Summaries</strong>
        <ul>
        {call_stack_summaries}
        </ul>


        <h4>Call Stacks</h4>
        {call_stacks}
        <br>
    '''
    )

    def __init__(
        self, window: Optional[sublime.Window], vulnerabilities: GoplsVulnerabilities
    ) -> None:
        self.vulnerabilities = vulnerabilities
        self.window = window or sublime.active_window()
        self.panel = self.window.create_output_panel(self.PANEL_NAME, unlisted=True)

    def show(self) -> None:
        mdpopups.erase_phantoms(self.panel, 'gopls.vulnerabilities')
        content = [
            self.VULN_HEADER.format(
                dir='temp', time='temp', vuln_count=len(self.vulnerabilities)
            )
        ]
        for vuln in self.vulnerabilities:
            content.append(
                self.VULN_TEMPLATE.format(
                    id=vuln['ID'],
                    url=vuln['URL'],
                    current_version=vuln['CurrentVersion'],
                    fixed_version=vuln['FixedVersion'],
                    pkg_path=vuln['PkgPath'],
                    aliases='\n'.join(
                        ['<li>{}</li>'.format(alias) for alias in vuln['Aliases']]
                    ),
                    call_stack_summaries='\n'.join(
                        [
                            '<li>{}</li>'.format(stack)
                            for stack in vuln['CallStackSummaries']
                        ]
                    ),
                    details=vuln['Details'],
                    call_stacks=self.call_stacks_to_markdown(vuln['CallStacks']),
                )
            )
        mdpopups.add_phantom(
            view=self.panel,
            key='gopls.vulnerabilities',
            region=sublime.Region(0, 0),
            content='\n'.join(content),
            layout=sublime.LAYOUT_INLINE,
            md=True,
            css=self.CSS,
        )
        self.panel.set_read_only(True)
        self.panel.set_scratch(True)
        self.panel.settings().set('gutter', False)
        self.window.run_command(
            'show_panel', {'panel': 'output.{}'.format(self.PANEL_NAME)}
        )

    def call_stacks_to_markdown(self, call_stacks: List[GoplsVulnCallStack]) -> str:
        call_stack = ''
        for stack in call_stacks:
            call_info = []  # type List[Dict]
            for call in stack:
                info = {'name': call['Name']}
                uri = parse_uri(call['URI'])[1]
                if uri != "":
                    uri = '{uri}:{line}:{character}'.format(
                        uri=uri,
                        line=call['Pos']['line'],
                        character=call['Pos']['character'],
                    )
                    info['uri'] = uri

                call_info.append(info)
            call_stack += '<h6 class="call" >▼ <i>'
            call_stack += ' calls '.join([link['name'] for link in call_info])
            call_stack += '</i></h6>\n<ul>'
            call_stack += '\n'.join(
                [
                    '''<li><a href='{command}'>{name}</a></li>'''.format(
                        command=sublime.command_url(
                            'gopls_open_file', {"uri": call['uri']}
                        ),
                        name=call['name'],
                    )
                    if call.get('uri', None) is not None
                    else ""
                    for call in call_info
                ]
            )
            call_stack += '</ul>\n'
        return call_stack
