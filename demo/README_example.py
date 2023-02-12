#!/usr/bin/env python

try:
    from ts2python.json_validation import TypedDict, type_check
except ImportError:
    # seems that this script has been called from the git
    # repository without ts2python having been installed
    import sys, os
    sys.path.append(os.path.join('..', '..'))
    from ts2python.json_validation import TypedDict, type_check


class Position(TypedDict, total=True):
    line: int
    character: int


class Range(TypedDict, total=True):
    start: Position
    end: Position


@type_check
def middle_line(rng: Range) -> Position:
    line = (rng['start']['line'] + rng['end']['line']) // 2
    character = 0
    return Position(line=line, character=character)


rng = {'start': {'line': 1, 'character': 1},
       'end': {'line': 8, 'character': 17}}

assert middle_line(rng) == {'line': 4, 'character': 0}

malformed_rng = {'start': 1, 'end': 8}
try:
    middle_line(malformed_rng)
except TypeError as e:
    print(e)
    # expected:
    # Parameter "rng" of function "middle_line" failed the type-check, because:
    # Type error(s) in dictionary of type <class '__main__.Range'>:
    # Field start: '1' is not of <class '__main__.Position'>, but of type <class 'int'>
    # Field end: '8' is not of <class '__main__.Position'>, but of type <class 'int'>
