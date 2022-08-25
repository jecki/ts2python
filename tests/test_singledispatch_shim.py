#!/usr/bin/env python

"""test_singledispatch_shim.py -- test code for ts2python's singledispatch"""


from typing import List, Union
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


class TestForwardReference:
    def test_forward_reference(self):
        @singledispatch
        def func(param):
            pass
        @func.register
        def _(param: 'C'):
            pass
        class C:
            pass


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
