from LSP.plugin.core.typing import TypedDict, List

GoplsVulnCallStackPosition = TypedDict(
    "GoplsVulnCallStackPosition", {"line": int, "character": int}, total=True
)

GoplsVulnCallStack = TypedDict(
    "GoplsVulnCallStack",
    {"URI": str, "Pos": GoplsVulnCallStackPosition, "Name": str},
    total=True,
)

GoplsVulnCallStacks = List[GoplsVulnCallStack]

GoplsVulnerability = TypedDict(
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
        "CallStacks": List[GoplsVulnCallStacks],
    },
    total=True,
)

GoplsVulnerabilities = List[GoplsVulnerability]
