from __future__ import annotations

from typing import Optional
from typing import TypedDict


class GoplsStartDebuggingResponse(TypedDict):
    URLs: list[str]

class GoplsRunTestsArgument(TypedDict):
    URI: str
    Tests: Optional[list[str]]
    Benchmarks: Optional[list[str]]
