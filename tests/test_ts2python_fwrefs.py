#!/usr/bin/env python

"""test_ts2python_fwrefs.py -- test code for forward referencing and recursive types."""




from enum import IntEnum
import os
import sys
from typing import TypeVar, Generic, Union, Dict, List, Optional


scriptdir = os.path.dirname(os.path.abspath(__file__))
scriptdir_parent = os.path.abspath(os.path.join(scriptdir, '..'))

try:
    import ts2pythonParser
    from ts2pythonParser import compile_src
    from ts2python import json_validation
    from ts2python.json_validation import validate_type, type_check, \
        validate_uniform_sequence
    from ts2python import typeddict_shim
    from ts2python.typeddict_shim import TypedDict
except ImportError:
    if scriptdir_parent not in sys.path:
        sys.path.append(scriptdir_parent)
    import ts2pythonParser
    from ts2pythonParser import compile_src
    from ts2python import json_validation
    from ts2python.json_validation import validate_type, type_check, \
        validate_uniform_sequence
    from ts2python import typeddict_shim
    from ts2python.typeddict_shim import TypedDict


## TEST CLASSES

integer = float

uinteger = float

decimal = float

LSPAny = Union['LSPObject', 'LSPArray', str, int, float, bool, None]

LSPObject = Dict[str, LSPAny]

LSPArray = List[LSPAny]


class Message(TypedDict, total=True):
    jsonrpc: str


class RequestMessage(Message, TypedDict, total=False):
    id: Union[int, str]
    method: str
    params: Union[List, Dict, None]


class ResponseMessage(Message, TypedDict, total=False):
    id: Union[int, str, None]
    result: Optional[LSPAny]
    error: Optional['ResponseError']


class ResponseError(TypedDict, total=False):
    code: int
    message: str
    data: Optional[LSPAny]

class ErrorCodes(IntEnum):
    ParseError = -32700
    InvalidRequest = -32600
    MethodNotFound = -32601
    InvalidParams = -32602
    InternalError = -32603
    jsonrpcReservedErrorRangeStart = -32099
    serverErrorStart = jsonrpcReservedErrorRangeStart
    ServerNotInitialized = -32002
    UnknownErrorCode = -32001
    jsonrpcReservedErrorRangeEnd = -32000
    serverErrorEnd = jsonrpcReservedErrorRangeEnd
    lspReservedErrorRangeStart = -32899
    RequestFailed = -32803
    ServerCancelled = -32802
    ContentModified = -32801
    RequestCancelled = -32800
    lspReservedErrorRangeEnd = -32800

class Position(TypedDict, total=True):
    line: int
    character: int


### END OF TEST-CLASSES


class TestValidation:
    def setup_class(self):
        pass

    def test_type_check(self):
        @type_check
        def type_checked_func(select_test: int, request: RequestMessage, position: Position) \
                -> ResponseMessage:
            validate_type(position, Position)
            if select_test == 1:
                return {'jsonrpc': 'jsonrpc-string',
                        'id': request['id'],
                        'error': {'code': -404, 'message': 'bad mistake'}}
            elif select_test == 2:
                # missing required field 'message' in the contained
                # error object should case an error
                return {'jsonrpc': 'jsonrpc-string',
                        'id': request['id'],
                        'error': {'code': -404}}
            elif select_test == 3:
                return {'jsonrpc': 'Response',
                        'id': request['id'],
                        'result': "All's well that ends well"}
            else:
                # Just a different way of creating the dictionary
                return ResponseMessage(jsonrpc='Response', id=request['id'],
                                       result="All's well that ends well")

        response = type_checked_func(0, {'jsonrpc': '2.0', 'id': 21, 'method': 'check'},
                                     Position(line=21, character=15))
        assert response['id'] == 21
        response = type_checked_func(1, {'jsonrpc': '2.0', 'id': 21, 'method': 'check'},
                                     Position(line=21, character=15))
        assert response['id'] == 21
        response = type_checked_func(3, RequestMessage(jsonrpc='2.0', id=21, method='check'),
                                     {'line': 21, 'character': 15})
        assert response['id'] == 21
        if sys.version_info < (3, 7, 0):
            return
        try:
            _ = type_checked_func(0, {'jsonrpc': '2.0', 'id': 21, 'method': 'check'})
            assert False, "Missing parameter not noticed"
        except TypeError:
            pass
        try:
            _ = type_checked_func(0, {'jsonrpc': '2.0', 'method': 'check'},
                                     Position(line=21, character=15))
            assert False, "Type Error in parameter not detected"
        except KeyError:
            if sys.version_info >= (3, 8):
                assert False, "Type Error in parameter not detected"
        except TypeError:
            pass
        try:
            _ = type_checked_func(2, {'jsonrpc': '2.0', 'id': 21, 'method': 'check'},
                                     Position(line=21, character=15))
            if sys.version_info >= (3, 8):
                assert False, "Type Error in nested return type not detected"
        except TypeError:
            pass


DEFINITION_AFTERT_USAGE_TS = '''
class Range {
    start: Position;
    end: Position;
}

class Position {
    line: number;
    column: number;
}
'''


class TestClassDefinitionOrder:
    def test_class_definition_order(self):
        pycode, err = compile_src(DEFINITION_AFTERT_USAGE_TS)
        exec(pycode)

    def test_recursive_definition(self):
        pass


if __name__ == "__main__":
    from runner import runner
    runner("", globals())
