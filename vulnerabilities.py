import json
import sublime
import textwrap

from .types import GoplsVulnerabilities
from LSP.plugin.core.types import Optional

import mdpopups


class Vulnerabilities:
    PANEL_NAME = 'gopls.vulnerabilities'
    VULN_TEMPLATE = textwrap.dedent(
        '''
        ### [{id}]({url}) {symbol}
        <hr>

        **CurrentVersion**: `{current_version}`
        **FixedVersion**: `{fixed_version}`
        **PkgPath**: `{pkg_path}`
        **Aliases**:

        <ul>
        {aliases}
        </ul>

        **CallStackSummaries**:

        <ul>
        {call_stack_summaries}
        </ul>

        #### Details

        {details}

        #### Call Stacks

        ```json
        {call_stacks}
        ```
        <br>
    '''
    ).strip()

    def __init__(
        self, window: Optional[sublime.Window], vulnerabilities: GoplsVulnerabilities
    ) -> None:
        self.vulnerabilities = vulnerabilities
        self.window = window or sublime.active_window()
        self.panel = self.window.create_output_panel(self.PANEL_NAME, unlisted=True)

    def show(self) -> None:
        content = []
        for vuln in self.vulnerabilities:
            content.append(
                self.VULN_TEMPLATE.format(
                    id=vuln['ID'],
                    url=vuln['URL'],
                    symbol=vuln['Symbol'],
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
                    call_stacks=json.dumps(vuln['CallStacks'], indent=4),
                )
            )
        mdpopups.add_phantom(
            view=self.panel,
            key='gopls.vulnerabilities',
            region=sublime.Region(0, 0),
            content='\n'.join(content),
            layout=sublime.LAYOUT_INLINE,
            md=True,
        )
        self.window.run_command(
            'show_panel', {'panel': 'output.{}'.format(self.PANEL_NAME)}
        )
