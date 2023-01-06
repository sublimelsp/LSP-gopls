from LSP.plugin.core.protocol import Position
from LSP.plugin.core.typing import TypedDict, List

GoplsVulnStackEntry = TypedDict(
    'GoplsVulnStackEntry',
    {
        'URI': str,
        'Pos': Position,
        'Name': str,
    },
    total=True,
)

GoplsVulnCallStack = List[GoplsVulnStackEntry]

GoplsVulnerability = TypedDict(
    'GoplsVulnerability',
    {
        'Symbol': str,
        'CurrentVersion': str,
        'CallStackSummaries': List[str],
        'Aliases': List[str],
        'Details': str,
        'ModPath': str,
        'PkgPath': str,
        'ID': str,
        'FixedVersion': str,
        'URL': str,
        'CallStacks': List[GoplsVulnCallStack],
    },
    total=True,
)

GoplsVulnerabilities = List[GoplsVulnerability]
