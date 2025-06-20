Type Mapping Explained
======================

The following explains, how ``ts2python`` maps Typescript-types and
in particular `Typescript-interfaces`_, to Python types, in particular,
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

    class Message(TypedDict):
        jsonrpc: str

ts2python uses `TypedDict`_ as base class per default. Optional fields of a TypeScript-Interface
are mapped to ``NonRequired``-types in Python. Since the NotRequired-type-qualifier has
only been introduced in with Python version 3.11, NotRequired will be defined as an
alias to ``Optional`` if an older Python version is used. Also, if there are any optional fields, the
total-parameter of the TypedDict-class will be set to to ``False`` in the
compatibility-mode. Since before Python version 3.11 static validation relies
on the ``total``-parameter it will not
capture missing required attributes in TypedDicts that contain
both required and optional fields. Runtime-Validation by ts2python
will still catch such errors (see :ref:`runtime_validation`).

 Thus,::

    interface RequestMessage extends Message {
        id: integer | string;
        method: string;
        params?: array | object;
    }

becomes::

    NotRequired = Optional

    class RequestMessage(Message, TypedDict, total=False):
        id: Union[int, str]
        method: str
        params: NotRequired[Union[List, Dict]]

In the compatibility-mode (for Python versions smaller than 3.11)
``Optional``-types are understood as attributes that need
not be present in the dictionary. This runs contrary
the standard semantics of ``Optional``-types in Python, which
requires attributes annotated with ``Optional`` to always be present
although they may contain the value ``None``. In fact, this non-standard
interpretation of ``Optional`` implements one of the rejected ways of
marking individual TypedDict items as not required in `PEP 655`_.

However, since up to and including Python version 3.10 `PEP 655`_ had not been
implemented, abusing ``Optional`` for this purpose appeared to be
a pragmatic solution that in connection with setting the parameter
``total=False`` plays well-enough with static type-checkers. Unless
your code using ts2python-transpiled TypedDicts does not assume
attributes with ``Optional`` type to be present, there won't be a problem.

For the case that the transpiled code does not need to run with Python-versions
below 3.11, it is possible, to enforce `PEP 655`_ by calling ``ts2python``
with the parameter ``-p 655`` or with ``-c 3.11``, in which case ``NotRequired`` will be
not be redefined as ``Optional``. Also, the ``total``-parameter of the TypedDict-class will
not be set to "False" (and thus keep its default value "True),
which means that all not required fields are required.
The above Message-interface will then read as::

    class RequestMessage(Message, TypedDict):
        id: Union[int, str]
        method: str
        params: NotRequired[List | Dict]


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
about an expected closing quote.) However, in those cases, where the
string-content happens to be a valid identifier, ts2python will consider those
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
        changes: NotRequired[Dict['DocumentUri', List['TextEdit']]]
        documentChanges: Union[
            List['TextDocumentEdit'],
            List[Union['TextDocumentEdit', 'CreateFile', 'RenameFile', 'DeleteFile']],
            None]
        changeAnnotations: NotRequired[Dict[str, 'ChangeAnnotation']]


Mapping of Tuple Types
----------------------

Likewise, Typescript-tuple-types are transpiled to Python-tuple-types.

Typescript::

    export interface ParameterInformation {
        label: string | [uinteger, uinteger];
        documentation?: string | MarkupContent;
    }

Python::

    class ParameterInformation(TypedDict):
        label: Union[str, Tuple[int, int]]
        documentation: NotRequired[Union[str, 'MarkupContent']]


Mapping of Records
------------------

Typescript `Records`_ are simply mapped to parameterized dictionaries.

Typescript::

    export interface Test {
      t: Record<string, number>
    }

Python::

    class Test(TypedDict):
        t: Dict[str, float]


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

In order to transfer this to Python, a local class is defined
and the fields' name with a capitalized first letter and
appended underscore is used as name for the local class. Although,
this use of local-classes within TypedDict-classes is not in "legal"
conformance with the specification of TypedDict-classes (see `PEP 589`_),
it is technically sound and works perfectly well in practice
(see :ref:`toplevel_switch` for how to
enforce "legal" conformance, if needed) ::

    class InitializeParams(WorkDoneProgressParams, TypedDict):
        class ClientInfo_(TypedDict):
            name: str
            version: NotRequired[str]
        processId: Union[int, None]
        clientInfo: NotRequired[ClientInfo_]
        locale: NotRequired[str]
        rootPath: NotRequired[Union[str, None]]
        rootUri: Union['DocumentUri', None]
        initializationOptions: NotRequired[Any]
        capabilities: 'ClientCapabilities'
        trace: NotRequired['TraceValue']
        workspaceFolders: NoRequired[Union[List['WorkspaceFolder'], None]]

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

    class SemanticTokensClientCapabilities(TypedDict):
        class Requests_(TypedDict):
            class Range_1(TypedDict):
                pass
            class Full_1(TypedDict):
                delta: NotRequired[bool]
            range: NotRequired[Union[bool, Range_1]]
            full: NotRequired[Union[bool, Full_1]]
        dynamicRegistration: NotRequired[bool]
        requests: Requests_
        tokenTypes: List[str]
        tokenModifiers: List[str]
        formats: List['TokenFormat']
        overlappingTokenSupport: NotRequired[bool]
        multilineTokenSupport: NotRequired[bool]

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
        rangeLength: NotRequired[int]
        text: str
    class TextDocumentContentChangeEvent_1(TypedDict):
        text: str
    TextDocumentContentChangeEvent = Union[
        TextDocumentContentChangeEvent_0, TextDocumentContentChangeEvent_1]


Alternative Representations for Anonymous Interfaces
----------------------------------------------------

Starting with version 0.6.9, anonymous interfaces can also be mapped with
functional syntax::

    interface InitializeResult {
        capabilities: ServerCapabilities;
        serverInfo?: {
            name: string;
            version?: string;
        };
    }

becomes::

    class InitializeResult(TypedDict):
        capabilities: 'ServerCapabilities'
        serverInfo: NotRequired[TypedDict("ServerInfo_0",
                                {"name": str, "version": NotRequired[str]})]

The "functional" representation can be selected by assigning the
value "functional" to the configuration key "ts2python.RenderAnonymous".
Alternatively, it can be selected with the command line option
``--anonymous functional`` or ``-a functional``.

There is also an experimental "type"-syntax, which renders the
anonymous interface in the above example as::

    TypedDict[{"name": str, "version": NotRequired[str]}]

However, this is not (yet) in conformance with the Python-Standard.
(See this post on `inline TypedDict definitions`_). Still, it can be turned
on with ``-a type``.

.. _toplevel_switch:

Finally, with ``--anonymous toplevel`` or ``-a toplevel``,
the definition of classes inside classes
can be avoided completely. This helps to avoid complaints by type-checkers
like mypy or pylance. The result looks like this::

    class InitializeResult_ServerInfo_0(TypedDict):
        name: str
        version: NotRequired[str]

    class InitializeResult(TypedDict):
        capabilities: 'ServerCapabilities'
        serverInfo: NotRequired[InitializeResult_ServerInfo_0]

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

Thus, generic interfaces containing type-parameters will be transpiled to generic typed dicts,
which in the most backward-compatible form (back to Python 3.7) look like this::

    interface ProgressParams<T> {
        token: ProgressToken;
        value: T;
    }


becomes::

    T = TypeVar('T')

    class ProgressParams(Generic[T], GenericTypedDict, total=True):
        token: 'ProgressToken'
        value: T


If the compatibility-level is set to 3.11 or above, TypeVars suffice.
There is no need to derive from ``Generic`` or ``GenericTypedDict``, any more::

    T = TypeVar('T')

    class ProgressParams(TypedDict):
        token: 'ProgressToken'
        value: T


For Python versions higher than 3.12 only the result will be a generic TypedDict-class::

    class ProgressParams[T](TypedDict):
        token: 'ProgressToken'
        value: T


TypeAliases
-----------

The mapping of type aliases depends very much on the compatibility-level.
If the default compatibility all they way down to Python version 3.7 is
selected, Typescript type aliases will be mapped to plain type assignments.
For example,::

    type ProviderResult<T> = T | undefined | null | Thenable<T | undefined | null>;

will become::

    T = TypeVar('T')
    ProviderResult = Union[T, None, Coroutine[Union[T, None]]]

Observe that ``undefined`` and ``null`` are both mapped to the Python ``None``-value
and that redundancies like ``None | None`` are automatically resolved to ``None``.
If the compatibility-level is set to at least Python version 3.10 with the "-c 3.10"
switch which autoselects PEPs 586, 604, 613,  the type assignment will furthermore be
annotated with the TypeAlias-type::

    T = TypeVar('T')
    ProviderResult: TypeAlias = T | None | Coroutine[T | None]

Compatibility levels of 3.12 and above will also include support for PEP 695 and
ultimately yield the arguably most elegant syntax using the ``type``-statement
introduced with Python 3.12::

    type ProviderResult[T] = T | None | Coroutine[T | None]


Imports
-------

Starting from version 0.6.9 TypeScript imports, e.g.
``import {ChangeInfo, CommentRange} from './rest-api';`` will be
parsed and ignored so that they don't cause any parser errors.

Types derived from other Types
------------------------------

ts2Python has only rudimentary support for types that are derived
from other types (see `Creating Types from Types`_ in the Typescript-manual).
While some of these derived types are accepted by ts2python's parser, they
are practically never properly matched to similar Python-types. In many
cases types derived from other types will - for the lack of a deeper semantic
analysis of Typescript-input by ts2python - simply be represented as type
``Any`` on the Python-side.

Because Python's type system isn't as elaborated as that of Typescript, a translation
that keeps all information will often not be feasible, anyway. The main
reason, however, why this is not done is that it would require ts2python to
actually reason about the types it parses, which is something which ts2python
has not been designed for. However, more purely syntactic support for
these constructs can be added in the future, if desired.


.. _Typescript-interfaces: https://www.typescriptlang.org/docs/handbook/2/objects.html
.. _TypedDicts: https://www.python.org/dev/peps/pep-0589/
.. _TypedDict: https://www.python.org/dev/peps/pep-0589/
.. _Language Server Protocol: https://microsoft.github.io/language-server-protocol/
.. _PEP 655: https://www.python.org/dev/peps/pep-0655/
.. _PEP 589: https://peps.python.org/pep-0589/
.. _Index signatures: https://www.typescriptlang.org/docs/handbook/2/objects.html#index-signatures
.. _Enums: https://docs.python.org/3/library/enum.html
.. _inline TypedDict definitions: https://discuss.python.org/t/allow-local-class-type-definitions-inside-typeddict/41611/3
.. _Creating Types from Types: https://www.typescriptlang.org/docs/handbook/2/types-from-types.html
.. _Records: https://www.typescriptlang.org/docs/handbook/utility-types.html#recordkeys-type
