"""typeddict_shim.py - A version of typed-dict that supports
   Required / NotRequired -fields across all version of Python
   from 3.6 onward.

Until Python version 3.10, the STL's TypeDict merely supports
classifying all fields of a TypedDict class as either required
or optional. This TypedDict implementation classifies allows
to mark fields as "NotRequired[...]". Presently, "NotRequired"
is implemented as just another name for "Optional" and
"Optional[...]" as well as its synonym "Union[..., None] are
interpreted as allowing to leave a field out. Thins runs
contrary the standard semantics of "Optional" as well as PEP 655,
but should - most of the time - not lead to any problems in
practice.".

Starting with Python 3.11 the NotRequired-marker
provided by the typing-module of the STL will be used.

Starting with Python 3.14 "Optional" will not be interpreted
as a chiffre for NotRequired any more. (This means that
old code produced by ts2python might behave differently.
In particular, objects with not required fields might
consume more memory than necessary, because these fields
will always be present as optional types.

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

import sys

__all__ = ['NotRequired', 'TypedDict', 'GenericTypedDict', '_TypedDictMeta',
           'GenericMeta', 'get_origin', 'get_args', 'Literal', 'is_typeddict',
           'ForwardRef', '_GenericAlias', 'ReadOnly', 'TypeAlias']

if sys.version_info >= (3, 14):
    from typing import (NotRequired, TypedDict, _TypedDictMeta,
                        ForwardRef, _GenericAlias, get_origin, get_args,
                        Literal, is_typeddict, Union, ReadOnly, TypeAlias)
    GenericTypedDict = TypedDict
    GenericMeta = type

else:
    from typing import (Generic, TypeVar, ClassVar, Any, NoReturn, _SpecialForm,
                        _GenericAlias, ForwardRef, Union)

    try:
        from typing import Protocol, Final
    except ImportError:
        Protocol = Generic
        Final = type

    if sys.version_info >= (3, 11):
        from typing import (TypedDict, _TypedDictMeta, get_origin, get_args,
                            NotRequired, Literal, TypeAlias)
        if sys.version_info >= (3,13):
            from typing import ReadOnly
        else:
            ReadOnly = Union
        GenericTypedDict = TypedDict
        GenericMeta = type

    else:
        if sys.version_info >= (3, 10):
            from typing import TypeAlias
        else:
            TypeAlias = Any

        if sys.version_info >= (3, 8):
            from typing import get_args, get_origin, Optional, Literal
        else:
            from typing import Optional
            from DHParser.externallibs.typing_extensions import (get_origin,
                    get_args, Literal)

        NotRequired = Optional
        ReadOnly = Union

        # The following functions have been copied from the Python
        # standard libraries typing-module. They have been adapted
        # to support a more flexible version of TypedDict
        # see also: <https://www.python.org/dev/peps/pep-0655/>

        def _type_convert(arg, module=None):
            """For converting None to type(None), and strings to ForwardRef."""
            if arg is None:
                return type(None)
            if isinstance(arg, str):
                fwref = ForwardRef(arg)
                if hasattr(fwref, '__forward_module__'):
                    fwref.__forward_module__ = module
                return fwref
            return arg


        def _type_check(arg, msg, is_argument=True, module=None):
            """Check that the argument is a type, and return it (internal helper).
            As a special case, accept None and return type(None) instead. Also wrap strings
            into ForwardRef instances. Consider several corner cases. For example, plain
            special forms like Union are not valid, while Union[int, str] is OK, etc.
            The msg argument is a human-readable error message, e.g.::
                "Union[arg, ...]: arg should be a type."
            We append the repr() of the actual value (truncated to 100 chars).
            """
            invalid_generic_forms = (Generic, Protocol)
            if is_argument:
                invalid_generic_forms = invalid_generic_forms + (ClassVar, Final)

            arg = _type_convert(arg, module=module)
            # if (isinstance(arg, _GenericAlias) and
            #         arg.__origin__ in invalid_generic_forms):
            #     raise TypeError(f"{arg} is not valid as type argument")
            if arg in (Any, NoReturn):
                return arg
            if (sys.version_info >= (3, 7) and isinstance(arg, _SpecialForm)) \
                    or arg in (Generic, Protocol):
                raise TypeError(f"Plain {arg} is not valid as type argument")
            if isinstance(arg, (type, TypeVar, ForwardRef)):
                return arg
            if sys.version_info >= (3, 10):
                from types import UnionType
                if isinstance(arg, UnionType):
                    return arg
            if not callable(arg):
                print(sys.version_info, sys.version_info >= (3, 9))
                raise TypeError(f"{msg} Got {arg!r:.100}.")
            return arg


        class _TypedDictMeta(type):
            def __new__(cls, name, bases, ns, total=True):
                """Create new typed dict class object.

                This method is called when TypedDict is subclassed,
                or when TypedDict is instantiated. This way
                TypedDict supports all three syntax forms described in its docstring.
                Subclasses and instances of TypedDict return actual dictionaries.
                """
                for base in bases:
                    if type(base) is not _TypedDictMeta and base is not Generic:
                        raise TypeError('cannot inherit from both a TypedDict type '
                                        'and a non-TypedDict base class')
                tp_dict = type.__new__(_TypedDictMeta, name, (dict,), ns)

                annotations = {}
                own_annotations = ns.get('__annotations__', {})
                # own_annotation_keys = set(own_annotations.keys())
                msg = "TypedDict('Name', {f0: t0, f1: t1, ...}); each t must be a type"
                own_annotations = {
                    n: _type_check(tp, msg, module=tp_dict.__module__)
                    for n, tp in own_annotations.items()
                }
                required_keys = set()
                optional_keys = set()

                for base in bases:
                    annotations.update(base.__dict__.get('__annotations__', {}))
                    required_keys.update(base.__dict__.get('__required_keys__', ()))
                    optional_keys.update(base.__dict__.get('__optional_keys__', ()))

                annotations.update(own_annotations)

                total = True
                for field, field_type in own_annotations.items():
                    field_type_origin = get_origin(field_type)
                    if (field_type_origin is NotRequired
                            or (field_type_origin is Union
                                and type(None) in field_type.__args__)
                            or (isinstance(field_type, ForwardRef)
                                and (field_type.__forward_arg__.startswith('Optional[')
                                     or field_type.__forward_arg__.startswith('NotRequired')
                                     or (field_type.__forward_arg__.startswith('Union[')
                                         and field_type.__forward_arg__.endswith(', None]'))))):
                        optional_keys.add(field)
                        total = False
                    else:
                        required_keys.add(field)

                tp_dict.__annotations__ = annotations
                tp_dict.__required_keys__ = frozenset(required_keys)
                tp_dict.__optional_keys__ = frozenset(optional_keys)
                if not hasattr(tp_dict, '__total__'):
                    tp_dict.__total__ = total
                return tp_dict

            def __getitem__(self, *args, **kwargs):
                pass

            __call__ = dict  # static method

            def __subclasscheck__(cls, other):
                # Typed dicts are only for static structural subtyping.
                raise TypeError('TypedDict does not support instance and class checks')

            __instancecheck__ = __subclasscheck__


        def TypedDict(typename, fields=None, *, total=True, **kwargs):
            """A simple typed namespace. At runtime it is equivalent to a plain dict.

            TypedDict creates a dictionary type that expects all of its
            instances to have a certain set of keys, where each key is
            associated with a value of a consistent type. This expectation
            is not checked at runtime but is only enforced by type checkers.
            Usage::

                class Point2D(TypedDict):
                    x: int
                    y: int
                    label: str

                a: Point2D = {'x': 1, 'y': 2, 'label': 'good'}  # OK
                b: Point2D = {'z': 3, 'label': 'bad'}           # Fails type check

                assert Point2D(x=1, y=2, label='first') == dict(x=1, y=2, label='first')

            The type info can be accessed via the Point2D.__annotations__ dict, and
            the Point2D.__required_keys__ and Point2D.__optional_keys__ frozensets.
            TypedDict supports two additional equivalent forms::

                Point2D = TypedDict('Point2D', x=int, y=int, label=str)
                Point2D = TypedDict('Point2D', {'x': int, 'y': int, 'label': str})

            By default, all keys must be present in a TypedDict. It is possible
            to override this by specifying totality.
            Usage::

                class point2D(TypedDict, total=False):
                    x: int
                    y: int

            This means that a point2D TypedDict can have any of the keys omitted.A type
            checker is only expected to support a literal False or True as the value of
            the total argument. True is the default, and makes all items defined in the
            class body be required.

            The class syntax is only supported in Python 3.6+, while two other
            syntax forms work for Python 2.7 and 3.2+
            """
            if fields is None:
                fields = kwargs
            elif kwargs:
                raise TypeError("TypedDict takes either a dict or keyword arguments,"
                                " but not both")

            ns = {'__annotations__': dict(fields)}
            try:
                # Setting correct module is necessary to make typed dict classes pickleable.
                ns['__module__'] = sys._getframe(1).f_globals.get('__name__', '__main__')
            except (AttributeError, ValueError):
                pass

            return _TypedDictMeta(typename, (), ns, total=total)

        _TypedDict = type.__new__(_TypedDictMeta, 'TypedDict', (), {})
        TypedDict.__mro_entries__ = lambda bases: (_TypedDict,)
        GenericTypedDict = TypedDict
        GenericMeta = type

    try:
        from typing import _TypedDictMeta as _typing_TypedDictMeta
        typing_TDM_flag = True  # _typing_TypedDictMeta is not the same as _TypedDictMeta
    except (ImportError, ModuleNotFoundError):
        _typing_TypedDictMeta = _TypedDictMeta
        typing_TDM_flag = False  # _typing_TypedDictMeta is the same as _TypedDictMeta


    def is_typeddict(typ) -> bool:
        return isinstance(typ, _typing_TypedDictMeta) \
            or (typing_TDM_flag and isinstance(typ, _TypedDictMeta))