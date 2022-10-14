"""singledispatch_shim.py - singledispatch with forward-referenced types

Python's functools.singledispatch does not work with function or
method-signatures where the type of dispatch-parameter is forward-references,
i.e. where the dispatch-parameter is not annotated with a type itself,
but with the string-name of the type. While the module "typing" allows this
kind of annotation as a simple form of forward-referencing,
"functools.singledispatch" raises a name.

singledispatch_shim contains an alternative implementation of
single dispatch that works correctly with forward-referenced types.

Copyright 2022  by Eckhart Arnold (arnold@badw.de)
                Bavarian Academy of Sciences an Humanities (badw.de)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""

import types

from functools import _find_impl, get_cache_token, update_wrapper
from typing import Union
try:
    from typing import GenericAlias, get_args, get_origin, get_type_hints
except ImportError:
    try:
        from typing_extensions import GenericAlias, get_args, get_origin, get_type_hints
    except ImportError:
        from .typing_extensions import GenericAlias, get_args, get_origin, get_type_hints


# The following functions have been copied from the Python
# standard libraries typing-module. They have been adapted
# to allow overloading functions that are annotated with
# forward-referenced-types.


def singledispatch(func):
    """Single-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviours depending upon the type of its first argument. The decorated
    function acts as the default implementation, and additional
    implementations can be registered using the register() attribute of the
    generic function.
    """
    # There are many programs that use functools without singledispatch, so we
    # trade-off making singledispatch marginally slower for the benefit of
    # making start-up of such applications slightly faster.
    import types, weakref

    registry = {}
    dispatch_cache = weakref.WeakKeyDictionary()
    cache_token = None

    def dispatch(cls):
        """generic_func.dispatch(cls) -> <function implementation>

        Runs the dispatch algorithm to return the best available implementation
        for the given *cls* registered on *generic_func*.

        """
        nonlocal cache_token
        if cache_token is not None:
            current_token = get_cache_token()
            if cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token
        try:
            impl = dispatch_cache[cls]
        except KeyError:
            try:
                impl = registry[cls]
            except KeyError:
                if 'postponed' in registry:
                    postponed = registry['postponed']
                    del registry['postponed']
                    for postponed_cls in postponed:
                        register(postponed_cls)
                    if 'postponed' in registry:
                        for f in registry['postponed']:
                            get_type_hints(f)   # provoke NameError
                        raise AssertionError('singledispatch: Internal Error: '
                                             + str(registry['postponed']))
                    try:
                        impl = registry[cls]
                    except KeyError:
                        impl = _find_impl(cls, registry)
                else:
                    impl = _find_impl(cls, registry)
            dispatch_cache[cls] = impl
        return impl

    def _is_union_type(cls):
        try:
            return get_origin(cls) in {Union, types.UnionType}
        except AttributeError:
            # Python 3.7
            return get_origin(cls) in {Union}

    def _is_valid_dispatch_type(cls):
        if isinstance(cls, type):
            return True
        return (_is_union_type(cls) and
                all(isinstance(arg, type) for arg in get_args(cls)))

    def register(cls, func=None):
        """generic_func.register(cls, func) -> func

        Registers a new implementation for the given *cls* on a *generic_func*.

        """
        nonlocal cache_token
        if _is_valid_dispatch_type(cls):
            if func is None:
                return lambda f: register(cls, f)
        else:
            if func is not None:
                raise TypeError(
                    f"Invalid first argument to `register()`. "
                    f"{cls!r} is not a class or union type."
                )
            ann = getattr(cls, '__annotations__', {})
            if not ann:
                raise TypeError(
                    f"Invalid first argument to `register()`: {cls!r}. "
                    f"Use either `@register(some_class)` or plain `@register` "
                    f"on an annotated function."
                )
            func = cls

            # only import typing if annotation parsing is necessary
            try:
                argname, cls = next(iter(get_type_hints(func).items()))
            except NameError:
                registry.setdefault('postponed', []).append(cls)
                return func
            if not _is_valid_dispatch_type(cls):
                if _is_union_type(cls):
                    raise TypeError(
                        f"Invalid annotation for {argname!r}. "
                        f"{cls!r} not all arguments are classes."
                    )
                else:
                    raise TypeError(
                        f"Invalid annotation for {argname!r}. "
                        f"{cls!r} is not a class."
                    )

        if _is_union_type(cls):
            for arg in get_args(cls):
                registry[arg] = func
        else:
            registry[cls] = func
        if cache_token is None and hasattr(cls, '__abstractmethods__'):
            cache_token = get_cache_token()
        dispatch_cache.clear()
        return func

    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f'{funcname} requires at least '
                            '1 positional argument')

        return dispatch(args[0].__class__)(*args, **kw)

    funcname = getattr(func, '__name__', 'singledispatch function')
    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = types.MappingProxyType(registry)
    wrapper._clear_cache = dispatch_cache.clear
    update_wrapper(wrapper, func)
    return wrapper


class singledispatchmethod:
    """Single-dispatch generic method descriptor.

    Supports wrapping existing descriptors and handles non-descriptor
    callables as instance methods.
    """

    def __init__(self, func):
        if not callable(func) and not hasattr(func, "__get__"):
            raise TypeError(f"{func!r} is not callable or a descriptor")

        self.dispatcher = singledispatch(func)
        self.func = func

    def register(self, cls, method=None):
        """generic_method.register(cls, func) -> func

        Registers a new implementation for the given *cls* on a *generic_method*.
        """
        return self.dispatcher.register(cls, func=method)

    def __get__(self, obj, cls=None):
        def _method(*args, **kwargs):
            method = self.dispatcher.dispatch(args[0].__class__)
            return method.__get__(obj, cls)(*args, **kwargs)

        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method.register = self.register
        update_wrapper(_method, self.func)
        return _method

    @property
    def __isabstractmethod__(self):
        return getattr(self.func, '__isabstractmethod__', False)

