Basic Usage
===========

Generating TypeDict-classes from Typescript-Interfaces
------------------------------------------------------

TypedDict-classes can be generated from Typescript-Interfaces,
by running the ``ts2python``-command from the command line on
the Typescript-Interface definitions::

    $ ts2python interfaces.ts

This generates a .py-file in same directory as the source
file that contains the TypedDict-classes and can simpy be
imported in Python-Code::

    from interfaces import *

Typescript Interfaces are transformed to Python TypedDicts
in a straight-forward way. The following Typescript-code::

    interface Message {
        jsonrpc: string;
    }
    interface RequestMessage extends Message {
        id: integer | string;
        method: string;
        params?: array | object;
    }
    interface ResponseMessage extends Message {
        id: integer | string | null;
        result?: string | number | boolean | object | null;
        error?: ResponseError;
    }

will become::

    class Message(TypedDict, total=True):
        jsonrpc: str

    class RequestMessage(Message, TypedDict):
        id: Union[int, str]
        method: str
        params: NotRequired[Union[List, Dict]]

    class ResponseMessage(Message, TypedDict):
        id: Union[int, str, None]
        result: NotRequired[Union[str, float, bool, Dict, None]]
        error: NotRequired['ResponseError']


Type-checking Input and Return-Values
-------------------------------------

In order to allow static type-checking with `mypy`_ or another
Python type-checker, `type-annotations`_ should be used in the source
code, e.g.::

    def process_request(request: RequestMessage) -> ResponseMessage:
        ...
        return ResponseMessage(id = request.id)

There are some cases where static type-checking on the Python-side might
not suffice to catch all type errors. For example, if the input data
stems from a JSON-RPC call and is de-serialized via::

    import json
    request_msg: RequestMessage = json.loads(input_data)

Type-conformance can now be checked at runtime with:

    from ts2python.json_validation import validate_type
    validate_type(request_msg, RequestMessage)

``validate_type`` will raise a TypeError, if the type is incorrect.
Alternatively, both the call parameters and the return value of a Python
function can be validated at runtime against their annotated types by
adding the ``type_check``-decorator to the function, e.g.::

    from ts2python.json_validation import type_check
    @type_check
    def process_request(request: RequestMessage) -> ResponseMessage:
        ...
        return ResponseMessage(id = request.id)

Mind that runtime-type validation consumes time. Depending on the
application case, you might consider using it only during development
or for debugging.

.. _mypy: http://mypy-lang.org/
.. _type-annotations: https://www.python.org/dev/peps/pep-0484/