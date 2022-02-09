Type Mapping Explained
======================

The following explains, how ``ts2python`` maps Typescript-types,
in particular, `Typescript interfaces`_, to Python types, in particular,
`TypedDicts`_. The mapping is, so far, rich enough to cover all
interfaces from the `Language Server Protocol`_.


Mapping of Interfaces
---------------------

Basically, Typescript-Interfaces are mapped to Python-classes
and the fields of an interface are mapped to a class attribute.
Thus,::

    interface Message {
        jsonrpc: string;
    }

becomes::

    class Message(TypedDict, total=True):
        jsonrpc: str

ts2python uses `TypedDict`_ as base class per default and sets the
TypedDict total-paramter to ``True``, if no fields are optional
and to ``False`` otherwise.

Optional fields of a TypeScript-Interface are mapped to ``Optional``-types
in Python or, what amounts to the same to ``Union``-types that include
``None`` as one of the alternative types of the union. Thus,::

    interface RequestMessage extends Message {
        id: integer | string;
        method: string;
        params?: array | object;
    }

becomes::

    class RequestMessage(Message, TypedDict, total=False):
        id: Union[int, str]
        method: str
        params: Union[List, Dict, None]

Here ``Optional``-types are understood as attributes that need
not be present in the dictionary. This runs contrary
the standard semantics of ``Optional``-types in Python, which
requires attributes annotated with ``Optional`` to always be present
although they may contain the value ``None``. In fact, this non-standard
interpretation of ``Optional`` implements one of the rejected ways of
marking individual TypedDict items as not required in `PEP 655`_.

However, since as of Python version 3.10 `PEP 655`_ has not yet been
implemented, abusing ``Optional`` for this purpose appears to be
a pragmatic solution that in connection with setting the parameter
``total=False`` plays well-enough with static type-checkers. Unless
your code using ts2python-transpiled TypedDicts does not assume
attributes with ``Optional`` type to be present, there won't be a problem.
(Still, it is possible, to enforce `PEP 655`_ by calling ``ts2python``
with the parameter ``--p 655``, in which case ``NotRequired`` will be
used instead of optional. The above Message-interface will then read as::

    class RequestMessage(Message, TypedDict, total=True):
        id: Union[int, str]
        method: str
        params: NoRequired[Union[List, Dict]

Since static validation relies on the ``total``-parameter it will not
capture missing required attributes in TypedDicts that contain
both required and optional fields. Runtime-Validation by ts2python
will still catch such errors (see Validation, below)


Mapping of Field Types
----------------------

For most field types the mapping is fairly straight forward:

    ==============  ============
    Typscript type  Python type
    ==============  ============
    number          float
    integer         int
    boolean         bool
    string          str
    null            None
    unknown         Any
    any             any
    array           list
    object          dict
    ==============  ============


Mapping of Literals
-------------------

For some field types, the Python-counterpart is less obvious.
Literal types are naturally converted using ``Literal``. For Python-
Versions below 3.8, the ``typing_extensions``-module must be present to
provide the ``Literal``-type::

    export type ResourceOperationKind = 'create' | 'rename' | 'delete';

will be converted to::

    ResourceOperationKind = Literal['create', 'rename', 'delete']


Mapping of Enumerations
-----------------------

Enumerations can also more or less directly be transpiled to
Python-Enums. Thus,::

    export enum FoldingRangeKind {
        Comment = 'comment',
        Imports = 'imports',
        Region = 'region'
    }

becomes::

    class FoldingRangeKind(Enum):
        Comment = 'comment'
        Imports = 'imports'
        Region = 'region'

There exist some restrictions regarding enums, though. Other than
Typescript, Python does not really allow strings as keys in enumerations.
Thus, the Typescript enum::

    export enum MilkyWay {
        'from the earth',
        'past the moon',
        'to the stars'
    }

will not be converted to a Python Enum. (Rather, ts2python will complain
about an expected closing quote.) However, in those cases, where the string
content happens to be a valid identifier, ts2python will consider those
strings as identifiers. The Typescript enum ``enum MilkyWay { 'earth', 'moon', 'stars' }``
will be converted to::

    class MilkyWay(IntEnum):
        earth = enum.auto()
        moon = enum.auto()
        stars = enum.auto()

The same Python Enum would be produced by ``enum MilkyWay { earth, moon, stars }`` without
quotation marks.

.. caution:: Observe, that ts2python converts enums without explicit values to
   Python IntEnums, and that, furthermore, Python enums start counting with 1 rather than
   0. (See the documentation of Python's
   [enum-module](https://docs.python.org/3/library/enum.html#functional-api) for the reasons for this.)
   If this leads to problems, the Typescript enum-definitions must be disambiguated by
   adding explicit values before the conversion!


Mapping of Index Signatures
---------------------------

`Index signatures`_ are simply transpiled to dictionaries, dropping
the identifier of the index signature. Thus,::

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

becomes::

    class WorkspaceEdit(TypedDict, total=False):
        changes: Optional[Dict['DocumentUri', List['TextEdit']]]
        documentChanges: Union[
            List['TextDocumentEdit'],
            List[Union['TextDocumentEdit', 'CreateFile', 'RenameFile', 'DeleteFile']],
            None]
        changeAnnotations: Optional[Dict[str, 'ChangeAnnotation']]


Mapping of Tuple Types
----------------------

Likewise, tuple types are transpiled to tuple-types.

Typescript::

    export interface ParameterInformation {
        label: string | [uinteger, uinteger];
        documentation?: string | MarkupContent;
    }

Python::

    class ParameterInformation(TypedDict, total=False):
        label: Union[str, Tuple[int, int]]
        documentation: Union[str, 'MarkupContent', None]


Mapping of Anonymous Interfaces
-------------------------------

A bit more complicated is the case of anonymous interfaces
in TypeScript::

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
appended underscore is used as name for the local class::

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

This works also for nested local interfaces::

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

becomes::

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
same field::

    export type TextDocumentContentChangeEvent = {
        range: Range;
        rangeLength?: uinteger;
        text: string;
    } | {
        text: string;
    };

becomes::

    class TextDocumentContentChangeEvent_0(TypedDict, total=False):
        range: Range
        rangeLength: Optional[int]
        text: str
    class TextDocumentContentChangeEvent_1(TypedDict, total=True):
        text: str
    TextDocumentContentChangeEvent = Union[
        TextDocumentContentChangeEvent_0, TextDocumentContentChangeEvent_1]


Namespaces and Generics
-----------------------

Typescript namespaces are not supported, except for the special case where
they consist entirely of constant definitions. In this case, namespaces
will be transpiled to `Enums`_.

Typescript Namespace::

    export namespace DiagnosticSeverity {
        export const Error: 1 = 1;
        export const Warning: 2 = 2;
        export const Information: 3 = 3;
        export const Hint: 4 = 4;
    }

Resulting Python Enum::

    class DiagnosticSeverity(IntEnum):
        Error = 1
        Warning = 2
        Information = 3
        Hint = 4

For some reason, which I do not know, ``typing.TypeDict`` does not work
in combination with ``typing.Generic``. Thus, interfaces containing
generic types will, for the time being, be transpiled to plain classes::

    interface ProgressParams<T> {
        token: ProgressToken;
        value: T;
    }

becomes::

    T = TypeVar('T')
    class ProgressParams(Generic[T]):
        token: ProgressToken
        value: 'T'

(``TypedDict`` can be added to the list of base classes manually,
however, if the ``TypedDict``-Shim from the
``ts2typeddict.json_validation``-module is used.)


.. _Typescript interfaces: https://www.typescriptlang.org/docs/handbook/2/objects.html
.. _TypedDicts: https://www.python.org/dev/peps/pep-0589/
.. _TypedDict: https://www.python.org/dev/peps/pep-0589/
.. _Language Server Protocol: https://microsoft.github.io/language-server-protocol/
.. _PEP 655: https://www.python.org/dev/peps/pep-0655/
.. _Index signatures: https://www.typescriptlang.org/docs/handbook/2/objects.html#index-signatures
.. _Enums: https://docs.python.org/3/library/enum.html
