import sys
from typing import Generic, TypeVar, ClassVar, Any, NoReturn, _SpecialForm, ForwardRef
try:
    from typing import Protocol, Final
except ImportError:
    Protocol = Generic
    Final = type

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
    into ForwardRef instances. Consider several corner cases, for example plain
    special forms like Union are not valid, while Union[int, str] is OK, etc.
    The msg argument is a human-readable error message, e.g::
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
            if type(base) is not _TypedDictMeta:
                raise TypeError('cannot inherit from both a TypedDict type '
                                'and a non-TypedDict base class')
        tp_dict = type.__new__(_TypedDictMeta, name, (dict,), ns)

        annotations = {}
        own_annotations = ns.get('__annotations__', {})
        own_annotation_keys = set(own_annotations.keys())
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
        if total:
            required_keys.update(own_annotation_keys)
        else:
            optional_keys.update(own_annotation_keys)

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



T = TypeVar('T')

class Test(TypedDict):
    value: int

class Test2(TypedDict):
    val: Test[T]

