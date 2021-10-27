# ts2python

Python-interoperability for Typescript-Interfaces.
Transpiles TypeScript-Interface-definitions to Python 
data structure definitions, e.g. TypedDict.

## License

ts2python is open source software under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0)

Copyright 2021 Eckhart Arnold <arnold@badw.de>, Bavarian Academy of Sciences and Humanities

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Purpose

When processing JSON data, as for example form a 
[JSON-RPC](https://www.jsonrpc.org/) call, with Python, it would
be helpful to have Python-definitions of the JSON-structures at
hand, in order to solicit IDE-Support, static type checking and,
potentially to enable structural validation at runtime. 

There exist different technologies for defining the structure of
JSON-data. Next to [JSON-schema](http://json-schema.org/), a 
de facto very popular technology for defining JSON-obejcts are
[Typescript-Interfaces](https://www.typescriptlang.org/docs/handbook/2/objects.html). 
For example, the 
[language server protocol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/) 
defines the structure of the JSON-data exchanged between client 
and server with Typescript-Interfaces.

In order to enable structural validation on the Python-side, 
ts2python transpiles the typescript-interface definitions
to Python-data structure definitions, primarily, 
[TypedDicts](https://www.python.org/dev/peps/pep-0589/),
but with some postprocessing it can also be adjusted to
other popular models for records or data structures in
Python, e.g.
[pydantic](https://pydantic-docs.helpmanual.io/)-Classes
and the like.

## Installation

ts2python can be installed from the command line with the command:

    # pip install ts2python

ts2python requires the parsing-expression-grammar-framwork 
[DHParser](https://gitlab.lrz.de/badw-it/DHParser)
which will automatically be installed as a dependency by 
the `pip`-command. ts2python requires at least Python Version 3.8
to run. (If there is any interest, I might backport it to Python 3.6.)
However, the Python-code it produces is backwards compatible 
down to Python 3.6, if the 
[typing extensions](https://pypi.org/project/typing-extensions/) 
have been installed.

For a demonstration how the TypeScript-Interfaces are transpiled
to Python-code, run the `demo.sh`-script (or `demo.bat` on Windows)
in the "demo"-sub-directory or the ts2python-directory. 
Or, run the `tst_ts2python_gramm.py` in the ts2python-directory
and look up the grammar-test-reports in the "REPORT"-sub-directory 
of the "test_grammar"-subdirectory.


## Usage

In order to generate TypedDict-classes from Typescript-Interfaces,
run `ts2python` on the Typescript-Interface definitions:

    # ts2python interfaces.ts

This generates a .py-file in same directory as the source
file that contains the TypedDict-classes and can simpy be 
imported in Python-Code:

    >>> from interface_definitions import *

Other data-representation models than TypedDict can be supported
with the `--base` and `--decorator`-options, e.g.

    >>> ts2python --base pydantic.BaseModel interfaces.ts

or:

    >>> ts2python --decorator attr.s interfaces.ts

Presently, ts2python does only offer very rudimentary support
for other models than TypedDict. So, before it can be used, 
further adjustments to the generated file are necessary when
using data models other than TypedDict.

## Mapping of Typescript-Types to Python-Types

### Mapping of Interfaces

Basically, Typescript-Interfaces are mapped to Python-classes 
and the fields of an interface are mapped to a class attribute.
Thus,

    interface Message {
        jsonrpc: string;
    }

becomes:

    class Message(TypedDict, total=True):
        jsonrpc: str

ts2python uses TypedDict as base class per default and sets the
TypedDict total-paramter to `True`, if no fields are optional
and to `False` otherwise. 

Optional fields of a TypeScript-Interface are mapped to `Optional`-types
in Python or, what amounts to the same to `Union`-types that include 
`None` as one of the alternative types of the union. Thus,

    interface RequestMessage extends Message {
        id: integer | string;
        method: string;
        params?: array | object;
    }

becomes:

    class RequestMessage(Message, TypedDict, total=False):
        id: Union[int, str]
        method: str
        params: Union[List, Dict, None]

Here `Optional`-types are understood as attributes that need
not be present in the dictionary. This runs contrary
the standard semantics of `Optional`-types in Python, which 
requires attributes annotated with `Optional` to always be present
although they may contain the value `None`. In fact, this non-standard 
interpretation of `Optional` implements one of the rejected ways of 
marking individual TypedDict items as not required in PEP 655.

However, since as of Python version 3.9 PEP 655 has not yet been
implemented, abusing `Optional` for this purpose appears to be
a pragmatic solution that in connection with setting the parameter
`total=False` plays well-enough with static type-checkers. Unless
your code using ts2python-transpiled TypedDicts does not assume
attibutes with `Optional` type to be present, there won't be a problem.
(Still, it is possible, to enforce PEP 655 by calling `ts2python`
with the parameter `--p 655`, in which case `NotRequired` will be
used instead of optional.

Since static validation relies on the `total`-parameter it will not
capture missing required attributes in TypedDicts that contian
both required and optional fields. Runtime-Validation by ts2python
will still catch such errors (see Validation, below)

### Mapping of field types

For most field types the mapping is fairly straight forward:

    Typscript type | Python type
    ----------------------------    
    number         | float
    integer        | int
    boolean        | bool
    string         | str
    null           | None
    unknown        | Any
    any            | any
    array          | list
    object         | dict

For some field types, the Python-counterpart is less obvious.
Literal types are naturally converted using `Literal`. For Python-
Versions < 3.8, the `typing_extensions`-module must be present to
provide the `Literal`-type:

    export type ResourceOperationKind = 'create' | 'rename' | 'delete';

will be converted to:

    ResourceOperationKind = Literal['create', 'rename', 'delete']

Enumerations can also more or less directly be transpiled to
Python-Enums. Thus,

    export enum FoldingRangeKind {
        Comment = 'comment',
        Imports = 'imports',
        Region = 'region'
    }

becomes:

    class FoldingRangeKind(Enum):
        Comment = 'comment'
        Imports = 'imports'
        Region = 'region'

Map signatures are simply transpiled to dictionaries, dropping
the identifier of the index signature. Thus,

    export interface WorkspaceEdit {
        changes?: { [uri: DocumentUri]: TextEdit[]; };
    
        documentChanges?: (
            TextDocumentEdit[] |
            (TextDocumentEdit | CreateFile | RenameFile | DeleteFile)[]
        );
    
        changeAnnotations?: {
            [id: string /* ChangeAnnotationIdentifier */]: ChangeAnnotation;
        };
    }

becomes:

    class WorkspaceEdit(TypedDict, total=False):
        changes: Optional[Dict['DocumentUri', List['TextEdit']]]
        documentChanges: Union[
            List['TextDocumentEdit'], 
            List[Union['TextDocumentEdit', 'CreateFile', 'RenameFile', 'DeleteFile']], 
            None]
        changeAnnotations: Optional[Dict[str, 'ChangeAnnotation']]

Likewise, tuple types are transpiled to tuple-types.

Typescript:

    export interface ParameterInformation {
        label: string | [uinteger, uinteger];
        documentation?: string | MarkupContent;
    }

Python:

    class ParameterInformation(TypedDict, total=False):
        label: Union[str, Tuple[int, int]]
        documentation: Union[str, 'MarkupContent', None]

A bit more complicated is the case of anonymous interfaces
in TypeScript: 

    interface InitializeParams extends WorkDoneProgressParams {
        processId: integer | null;
        clientInfo?: {
            name: string;
            version?: string;
        };
        locale?: string;
        rootPath?: string | null;
        rootUri: DocumentUri | null;
        initializationOptions?: any;
        capabilities: ClientCapabilities;
        trace?: TraceValue;
        workspaceFolders?: WorkspaceFolder[] | null;
    }

In order to transfer this to Python a local class is defined
and the fields name with a capitalized first letter and 
appended underscore is used as name for the local class:

    class InitializeParams(WorkDoneProgressParams, TypedDict, total=False):
        class ClientInfo_(TypedDict, total=False):
            name: str
            version: Optional[str]
        processId: Union[int, None]
        clientInfo: Optional[ClientInfo_]
        locale: Optional[str]
        rootPath: Union[str, None]
        rootUri: Union['DocumentUri', None]
        initializationOptions: Optional[Any]
        capabilities: 'ClientCapabilities'
        trace: Optional['TraceValue']
        workspaceFolders: Union[List['WorkspaceFolder'], None]

This works also for nested local interfaces:

    interface SemanticTokensClientCapabilities {
        dynamicRegistration?: boolean;
        requests: {
            range?: boolean | {
            };
            full?: boolean | {
                delta?: boolean;
            };
        };
        tokenTypes: string[];
        tokenModifiers: string[];
        formats: TokenFormat[];
        overlappingTokenSupport?: boolean;
        multilineTokenSupport?: boolean;
    }

becomes:

    class SemanticTokensClientCapabilities(TypedDict, total=False):
        class Requests_(TypedDict, total=False):
            class Range_1(TypedDict, total=True):
                pass
            class Full_1(TypedDict, total=False):
                delta: Optional[bool]
            range: Union[bool, Range_1, None]
            full: Union[bool, Full_1, None]
        dynamicRegistration: Optional[bool]
        requests: Requests_
        tokenTypes: List[str]
        tokenModifiers: List[str]
        formats: List['TokenFormat']
        overlappingTokenSupport: Optional[bool]
        multilineTokenSupport: Optional[bool]

In case of type unions, the local classes will be numbered,
because there could be more than one local interface for the
same field:

    export type TextDocumentContentChangeEvent = {
        range: Range;
        rangeLength?: uinteger;
        text: string;
    } | {
        text: string;
    };

becomes:

    class TextDocumentContentChangeEvent_0(TypedDict, total=False):
        range: Range
        rangeLength: Optional[int]
        text: str
    class TextDocumentContentChangeEvent_1(TypedDict, total=True):
        text: str
    TextDocumentContentChangeEvent = Union[
        TextDocumentContentChangeEvent_0, TextDocumentContentChangeEvent_1]

### Namespaces and Generics

Typescript namespaces are not supported, except for the special case where
they consist entirely of constant definitions. In this case, namespaces
will be transpiled to Enums:

Typescript Namespace:

    export namespace DiagnosticSeverity {
        export const Error: 1 = 1;
        export const Warning: 2 = 2;
        export const Information: 3 = 3;
        export const Hint: 4 = 4;
    }

Resulting Python Enum:

    class DiagnosticSeverity(IntEnum):
        Error = 1
        Warning = 2
        Information = 3
        Hint = 4

For some reason, which I do not know, `typing.TypeDict` does not work
in combination with `typing.Generic`. Thus, interfaces containing
generic types will, for the time being, be transpiled to plain classes:

    interface ProgressParams<T> {
        token: ProgressToken;
        value: T;
    }

becomes:

    T = TypeVar('T')
    class ProgressParams(Generic[T]):
        token: ProgressToken
        value: 'T'

(`TypedDict` can be added to the list of base classes manually,
however, if the `TypedDict`-Shim from the 
`ts2typeddict.validation`-module is used. See below.) 


## Validation

With TypedDict, any static type checker that already supports 
TypedDicts can be leveraged to check the classes generated
by ts2python. However, 