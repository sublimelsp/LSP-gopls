from __future__ import annotations

from typing import TypedDict


class GoplsStartDebuggingResponse(TypedDict):
    URLs: list[str]


class GoplsRunTestsArgument(TypedDict):
    URI: str
    Tests: list[str] | None
    Benchmarks: list[str] | None
