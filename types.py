from LSP.plugin.core.protocol import Position
from LSP.plugin.core.typing import TypedDict, List

StackEntry = TypedDict(
    "StackEntry",
    {
        "URI": str,
        "Pos": Position,
        "Name": str,
    },
    total=True,
)

CallStack = List[StackEntry]

Vuln = TypedDict(
    "GoplsVulnerability",
    {
        "Symbol": str,
        "CurrentVersion": str,
        "CallStackSummaries": List[str],
        "Aliases": List[str],
        "Details": str,
        "ModPath": str,
        "PkgPath": str,
        "ID": str,
        "FixedVersion": str,
        "URL": str,
        "CallStacks": List[CallStack],
    },
    total=True,
)

Vulnerabilities = List[Vuln]
