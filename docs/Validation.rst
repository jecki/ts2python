Runtime Validation
==================

With ``TypedDict``, any static type checker that already supports
TypedDicts can be leveraged to check the classes generated
by ts2python.

However, there are use-cases where dynamic type checking of
TypedDicts might be relevant. For example, when processing
json-data stemming from an external source which might
happen to provide invalid data.

Also, up to Python 3.10 ``TypedDict`` does not allow marking
individual items as required or not required. (See
`PEP 655`_ for the details.) Static type checkers
that do not evaluate the ``Required`` and ``NotRequired`` annotation
will produce false results for TypedDicts that contain not required
fields.

Module :py:mod:`ts2python.json_validation` provides functions
and function annotations to validate (arbitrarily nested) typed dicts.
In order to use runtime type-checking, :py:mod:`ts2python.json_validation`
provides a TypedDict-shim that should be imported either instead of
or after Python's ``typing.TypedDict`` and before defining any
TypedDict classes. Runtime json-Validation can fail with obscure
error messages, if the TypedDict-classes against which values are
checked at runtime do not derive from
:py:class:`ts2python.json_validation.TypedDict`!


The easiest way to use runtime type checking is by adding the
:py:func:`json_validation.type_check`-annotation to a function
receiving or returning a TypedDict::

    >>> from ts2python.json_validation import TypedDict, type_check
    >>> class Position(TypedDict, total=True):
    ...     line: int
    ...     character: int
    >>> class Range(TypedDict, total=True):
    ...     start: Position
    ...     end: Position
    >>> @type_check
    ... def line_too_long(rng: Range) -> bool:
    ...     return (rng['start']['character'] > 255
    ...             or rng['end']['character'] > 255)
    >>> line_too_long({'start': {'line': 1, 'character': 1},
    ...                'end': {'line': 8, 'character': 17}})
    False
    >>> try:
    ...     line_too_long({'start': {'line': 1, 'character': 1},
    ...                    'end': 256})
    ... except TypeError as e:
    ...     print(e)
    Parameter "rng" of function "line_too_long" failed the type-check, because:
    Type error(s) in dictionary of type <class '__main__.Range'>:
    Field end: '256' is not of <class '__main__.Position'>, but of type <class 'int'>

The :py:func:`json_validation.type_check`-annotation validates
both the arguments of a function and its return value.

TO BE CONTINUED


.. _PEP 655: https://www.python.org/dev/peps/pep-0655/
