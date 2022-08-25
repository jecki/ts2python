#!/usr/bin/env python

"""test_ts2python.py -- test code for ts2python.py."""

import sys


import os
import subprocess
import sys
from typing import TypeVar, Generic


scriptdir = os.path.dirname(os.path.abspath(__file__))
scriptdir_parent = os.path.abspath(os.path.join(scriptdir, '..'))

try:
    import ts2pythonParser
    from ts2pythonParser import compile_src
    from ts2python import json_validation
    from ts2python.json_validation import validate_type, type_check, \
        validate_uniform_sequence
except ImportError:
    if scriptdir_parent not in sys.path:
        sys.path.append(scriptdir_parent)
    import ts2pythonParser
    from ts2pythonParser import compile_src
    from ts2python import json_validation
    from ts2python.json_validation import validate_type, type_check, \
        validate_uniform_sequence

#
# def load_tests(loader, tests, ignore):
#     tests.addTests(doctest.DocTestSuite(json_validation))
#     return tests


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

export namespace SymbolKind {
	export const File = 1;
	export const Module = 2;
	export const Namespace = 3;
	export const Package = 4;
	export const Class = 5;
	export const Method = 6;
	export const Property = 7;
	export const Field = 8;
	export const Constructor = 9;
	export const Enum = 10;
	export const Interface = 11;
	export const Function = 12;
	export const Variable = 13;
	export const Constant = 14;
	export const String = 15;
	export const Number = 16;
	export const Boolean = 17;
	export const Array = 18;
	export const Object = 19;
	export const Key = 20;
	export const Null = 21;
	export const EnumMember = 22;
	export const Struct = 23;
	export const Event = 24;
	export const Operator = 25;
	export const TypeParameter = 26;
}

export namespace SymbolTag {
	export const Deprecated: 1 = 1;
}

export type SymbolTag = 1;

export interface DocumentSymbol {
	name: string;
	detail?: string;
	kind: SymbolKind;
	tags?: SymbolTag[];
	deprecated?: boolean;
	range: Range;
	selectionRange: Range;
	children?: DocumentSymbol[];
}

export enum FoldingRangeKind {
	Comment = 'comment',
	Imports = 'imports',
	Region = 'region'
}
"""


# class TestConfigValues:
#     def setup(self):
#         sys.path.append('..')
#
#     def test_different_BaseClass(self):


class TestGenericTypedDictSurrogate:
    def test_generic_typed_dict(self):
        if sys.version_info >= (3, 7, 0):
            GenericMeta = type
        else:
            from typing import GenericMeta
        class _GenericTypedDictMeta(GenericMeta):
            def __new__(cls, name, bases, ns, total=True):
                return type.__new__(_GenericTypedDictMeta, name, (dict,), ns)
            __call__ = dict
        GenericTypedDict = _GenericTypedDictMeta('TypedDict', (dict,), {})
        GenericTypedDict.__module__ = __name__
        T = TypeVar('T')

        class ProgressParams(Generic[T], GenericTypedDict, total=True):
            token: str
            value: 'T'
        pp = ProgressParams(token='tok', value=1)
        assert isinstance(pp, dict)
        assert pp == {'token': 'tok', 'value': 1}


PATH_FIX = f'''
import sys
fix1 = "{os.path.abspath(os.path.join(scriptdir, '..'))}"
fix2 = "{os.path.abspath(os.path.join(scriptdir, '..', '..'))}"
if fix1 not in sys.path:  sys.path.append(fix1)
if fix2 not in sys.path:  sys.path.append(fix2)
'''

class TestValidation:
    def setup(self):
        self.test_code, err = compile_src(TEST_DATA)
        self.test_code = PATH_FIX + self.test_code
        assert not err
        code = compile(self.test_code, '<string>', 'exec')
        exec(code, globals())

    def test_type_json_validation(self):
        position = Position(line=1, character=2)
        validate_type(position, Position)
        try:
            validate_type(position, Message)
            assert False, "TypeError expected!"
        except TypeError:
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

    def test_int_enum(self):
        try:
            validate_type(5, SymbolKind)
        except TypeError:
            assert False, "member of enum not identified"
        try:
            validate_type(100000, SymbolKind)
            assert False, "illegal member of enum did not raise a value error"
        except ValueError:
            pass

    def test_str_enum(self):
        try:
            validate_type('region', FoldingRangeKind)
        except TypeError:
            assert False, "member of enum not identified"
        try:
            validate_type('nothing', FoldingRangeKind)
            assert False, "illegal member of enum did not raise a value error"
        except ValueError:
            pass

    def test_nested_sequence(self):
        # data-snippet from the Medieval-Latin-Dictionary https://mlw.badw.de
        documentSymbols = [{
            "name": "LEMMA",
            "detail": "*satinus",
            "kind": 5,
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 15}},
            "selectionRange": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 15}},
            "children": [{
                "name": "GRAMMATIK",
                "detail": "",
                "kind": 8,
                "range": {
                    "start": {"line": 2, "character": 0},
                    "end": {"line": 2, "character": 9}},
                "selectionRange": {
                    "start": {"line": 2, "character": 0},
                    "end": {"line": 2, "character": 9}},
                "children": []}, {
                "name": "BEDEUTUNG",
                "detail": "pars tricesima secunda ponderis -- der zweiunddreißigste Teil eines Gewichtes, 'Satin'; de nummo ((* {de re cf.} B. Hilliger, Studien zu mittelalterlichen Maßen und Gewichten. HistVjSchr. 3. 1900.; p. 191sq.)):",
                "kind": 5,
                "range": {
                    "start": {"line": 12, "character": 0},
                    "end": {"line": 12, "character": 220}},
                "selectionRange": {
                    "start": {"line": 12, "character": 0},
                    "end": {"line": 12, "character": 220}},
                "children": []}]}]
        try:
            validate_uniform_sequence(documentSymbols, DocumentSymbol)
        except TypeError as e:
            assert False, "Validation failed inspite of correct data: " + str(e)


class TestOptions:
    def test_different_settings(self):
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
        pythonpath = os.environ.get('PYTHONPATH', '') + os.pathsep + scriptdir_parent
        os.environ['PYTHONPATH'] = pythonpath
        cmd = os.path.abspath(os.path.join(scriptdir, '..', 'ts2pythonParser.py'))
        result = subprocess.run(['python', cmd, 'testdata.ts'])
        assert result.returncode == 0
        assert os.path.exists('testdata.py')
        result = subprocess.run(['python', 'testdata.py'])
        assert result.returncode == 0
        with open('testdata.py', 'r', encoding='utf-8') as f:
            script = PATH_FIX + f.read()
        with open('testdata.py', 'w', encoding='utf-8') as f:
            f.write(script)
        result = subprocess.run(['python', 'testdata.py'])
        assert result.returncode == 0





if __name__ == "__main__":
    from runner import runner
    runner("", globals())
