from LSP.plugin.core.typing import TypedDict
from LSP.plugin.core.typing import List


GoplsStartDebuggingResponse = TypedDict(
    "GoplsStartDebuggingResponse",
    {
        "URLs": List[str],
    },
    total=True,
)
