# from __future__ import annotations


import sys
from enum import Enum, IntEnum

from typing import Union, Optional, Any, Generic, TypeVar, Callable, List, \
    Iterable, Iterator, Tuple, Dict, TypedDict, NotRequired, ReadOnly, Literal
from collections.abc import Coroutine

class SemanticTokensDelta(TypedDict):
    resultId: NotRequired[ReadOnly[str]]
    edits: List[SemanticTokensEdit]


class SemanticTokensEdit(TypedDict):
    start: int
    deleteCount: int
    data: NotRequired[List[int]]
