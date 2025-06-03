#!/usr/bin/env python

"""test_singledispatch_shim.py -- test code for ts2python's singledispatch"""

from __future__ import annotations

# from functools import singledispatch, singledispatchmethod
import os
import sys
from typing import List, Union

scriptpath = os.path.abspath(os.path.dirname(__file__) or '.')
ts2pythonpath = os.path.normpath(os.path.join(scriptpath, '..'))
if ts2pythonpath not in sys.path: sys.path.append(ts2pythonpath)

from ts2python.singledispatch_shim import singledispatch, singledispatchmethod


@singledispatch
def func(arg):
    raise TypeError(f"Possible types for arg are int or str, not {type(arg)}")


@func.register
def _(intarg: int):
    assert isinstance(intarg, int)
    return int


@func.register
def _(strarg: str):
    assert isinstance(strarg, str)
    return str


class TestSingleDispatchShim:
    def test_singledispatch(self):
        assert func(1) is int
        assert func("1") is str
        try:
            func([1, 2, 3])
            assert False, "TypeError expected"
        except TypeError:
            pass


class A:
    @singledispatchmethod
    def func(self, param):
        pass

    @func.register
    def _(self, param: C, a: int):
        return a
    @func.register
    def _(self, b: complex, c: float):
        return b, c


class B:
    @singledispatchmethod
    def func(self, param):
        pass

    @func.register
    def _(self, param: "C", a: int):
        return a
    @func.register
    def _(self, b: complex, c: float):
        return b, c


class C:
    pass


# @A.func.register
# def _(self, param: C, a: int):
#     return a
# @A.func.register
# def _(self, b: complex, c: float):
#     return b, c


class TestForwardReference:
    def test_forward_reference(self):
        a = A()
        assert a.func(C(), 3) == 3
        assert a.func((3 + 2j), 5.0) == ((3 + 2j), 5.0)

    def test_forward_reference_string_notation(self):
        b = B()
        assert b.func(C(), 3) == 3
        assert b.func((3 + 2j), 5.0) == ((3 + 2j), 5.0)


class TestGenericAlias:
    def test_generic_alias(self):
        @singledispatch
        def func(param):
            pass
        @func.register(list)
        def _(param:List['int']):
            pass



if __name__ == "__main__":
    from runner import runner
    runner("", globals())
