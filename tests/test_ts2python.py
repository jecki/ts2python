#!/usr/bin/env python

"""test_ts2python.py -- test code for ts2python.py."""

import os
import subprocess
import sys
from typing import TypeVar, Generic

try:
    from ts2python.ts2pythonParser import compile_src
except ImportError:
    sys.path.append(os.path.abspath(os.path.join('..', '..')))
    from ts2python.ts2pythonParser import compile_src


TEST_DATA = """
type DocumentUri = string;

type URI = string;

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

interface ResponseError {
	code: integer;
	message: string;
	data?: string | number | boolean | array | object | null;
}


interface Position {
    line: uinteger;
    character: uinteger;
}

interface Range {
    start: Position;
    end: Position;
}

interface Location {
    uri: DocumentUri;
    range: Range;
}

export namespace DiagnosticSeverity {
    export const Error: 1 = 1;
    export const Warning: 2 = 2;
    export const Information: 3 = 3;
    export const Hint: 4 = 4;
}

export namespace DiagnosticTag {
    export const Unnecessary: 1 = 1;
    export const Deprecated: 2 = 2;
}

export interface DiagnosticRelatedInformation {
    location: Location;
    message: string;
}

export interface CodeDescription {
    href: URI;
}

export interface Diagnostic {
    range: Range;
    severity?: DiagnosticSeverity;
    code?: integer | string;
    codeDescription?: CodeDescription;
    source?: string;
    message: string;
    tags?: DiagnosticTag[];
    relatedInformation?: DiagnosticRelatedInformation[];
    data?: unknown;
}
"""


# class TestConfigValues:
#     def setup(self):
#         sys.path.append('..')
#
#     def test_different_BaseClass(self):


class TestGenericTypedDictSurrogate:
    def test_generic_typed_dict(self):
        class _GenericTypedDictMeta(type):
            def __new__(cls, name, bases, ns, total=True):
                return type.__new__(_GenericTypedDictMeta, name, (dict,), ns)

        GenericTypedDict = _GenericTypedDictMeta('TypedDict', (dict,), {})
        GenericTypedDict.__module__ = __name__
        T = TypeVar('T')

        class ProgressParams(Generic[T], GenericTypedDict, total=True):
            token: str
            value: 'T'
        pp = ProgressParams(token='tok', value=1)
        assert isinstance(pp, dict)
        assert pp == {'token': 'tok', 'value': 1}


class TestValidation:
    def setup(self):
        self.test_code, err = compile_src(TEST_DATA)
        assert not err
        code = compile(self.test_code, '<string>', 'exec')
        exec(code, globals())

    def test_type_validation(self):
        from ts2python.validation import validate_type
        position = Position(line=1, character=2)
        validate_type(position, Position)
        try:
            validate_type(position, Message)
            assert False, "TypeError expected!"
        except TypeError:
            pass

    def test_type_check(self):
        from ts2python.validation import type_check, validate_type
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


class TestOptions:
    def test_different_settings(self):
        from ts2python import ts2pythonParser
        from DHParser.configuration import set_config_value
        set_config_value('ts2python.UseNotRequired', True, allow_new_key=True)
        code, _ = ts2pythonParser.compile_src(TEST_DATA)
        assert code.find('NotRequired[') >= 0


class TestScriptCall:
    def setup(self):
        with open('testdata.ts', 'w', encoding='utf-8') as f:
            f.write(TEST_DATA)

    def teardown(self):
        if os.path.exists('testdata.ts'):
           os.remove('testdata.ts')
        if os.path.exists('testdata.py'):
            os.remove('testdata.py')

    def test_ts2python_call(self):
        cmd = os.path.abspath(os.path.join('..', 'ts2pythonParser.py'))
        result = subprocess.run(['python', cmd, 'testdata.ts'])
        assert result.returncode == 0
        assert os.path.exists('testdata.py')
        result = subprocess.run(['python', 'testdata.py'])
        assert result.returncode == 0
        # result = subprocess.run(['python', cmd, '-d attr.s', 'testdata.ts'])
        # assert result.returncode == 0
        # result = subprocess.run(['python', cmd, '-b pydantic.BaseModel', 'testdata.ts'])
        # assert result.returncode == 0
        # result = subprocess.run(['python', cmd, 'testdata.ts', '-p 655'])
        # assert result.returncode == 0


if __name__ == "__main__":
    from runner import runner
    runner("", globals())
