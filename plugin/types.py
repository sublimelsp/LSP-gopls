from __future__ import annotations

from typing import TypedDict

GoplsStartDebuggingResponse = TypedDict(
    "GoplsStartDebuggingResponse",
    {
        "URLs": list[str],
    },
    total=True,
)
