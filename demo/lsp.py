# lsp.py - Language Server Protocol data structures and support functions
#
# Copyright 20w0  by Eckhart Arnold (arnold@badw.de)
#                 Bavarian Academy of Sciences an Humanities (badw.de)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

"""Module lsp.py defines (some of) the constants and data structures from
the Language Server Protocol. See:
<https://microsoft.github.io/language-server-protocol/specifications/specification-current/>

EXPERIMENTAL!!!
"""

from __future__ import annotations

import bisect
from enum import Enum, IntEnum

from typing import Union, List, Tuple, Optional, Dict, Any, \
    Iterator, Iterable, Callable, TypedDict

try:
    from typing_extensions import Generic, TypeVar, Literal, TypeAlias, NotRequired
except ImportError:
    from DHParser.externallibs.typing_extensions import \
        Generic, TypeVar, Literal, TypeAlias, NotRequired

# from DHParser.json_validation import validate_type, type_check, TypedDict


#######################################################################
#
# Language-Server-Protocol functions
#
#######################################################################


# general #############################################################

# def get_lsp_methods(cls: Any, prefix: str= 'lsp_') -> List[str]:
#     """Returns the language-server-protocol-method-names from class ``cls``.
#     Methods are selected based on the prefix and their name converted in
#     accordance with the LSP-specification."""
#     return [gen_lsp_name(fn, prefix) for fn in lsp_candidates(cls, prefix)]


def lsp_candidates(cls: Any, prefix: str = 'lsp_') -> Iterator[str]:
    """Returns an iterator over all method names from a class that either
    have a certain prefix or, if no prefix was given, all non-special and
    non-private-methods of the class."""
    assert not prefix[:1] == '_'
    if prefix:
        # return [fn for fn in dir(cls) if fn.startswith(prefix) and callable(getattr(cls, fn))]
        for fn in dir(cls):
            if fn[:len(prefix)] == prefix and callable(getattr(cls, fn)):
                yield fn
    else:
        # return [fn for fn in dir(cls) if not fn.startswith('_') and callable(getattr(cls, fn))]
        for fn in dir(cls):
            if not fn[:1] == '_' and callable(getattr(cls, fn)):
                yield fn


def gen_lsp_name(func_name: str, prefix: str = 'lsp_') -> str:
    """Generates the name of an lsp-method from a function name,
    e.g. "lsp_S_cancelRequest" -> "$/cancelRequest" """
    assert func_name[:len(prefix)] == prefix
    return func_name[len(prefix):].replace('_', '/').replace('S/', '$/')


def gen_lsp_table(lsp_funcs_or_instance: Union[Iterable[Callable], Any],
                  prefix: str = 'lsp_') -> Dict[str, Callable]:
    """Creates an RPC from a list of functions or from the methods
    of a class that implement the language server protocol.
    The dictionary keys are derived from the function name by replacing an
    underscore _ with a slash / and a single capital S with a $-sign.
    if ``prefix`` is not the empty string only functions or methods that start
    with ``prefix`` will be added to the table. The prefix will be removed
    before converting the functions' name to a dictionary key.

    >>> class LSP:
    ...     def lsp_initialize(self, **kw):
    ...         pass  # return InitializeResult
    ...     def lsp_shutdown(self, **kw):
    ...         pass
    >>> lsp = LSP()
    >>> gen_lsp_table(lsp, 'lsp_').keys()
    dict_keys(['initialize', 'shutdown'])
    """
    if isinstance(lsp_funcs_or_instance, Iterable):
        assert all(callable(func) for func in lsp_funcs_or_instance)
        rpc_table = {gen_lsp_name(func.__name__, prefix): func for func in lsp_funcs_or_instance}
    else:
        # assume lsp_funcs_or_instance is the instance of a class
        cls = lsp_funcs_or_instance
        rpc_table = {gen_lsp_name(fn, prefix): getattr(cls, fn)
                     for fn in lsp_candidates(cls, prefix)}
    return rpc_table


# textDocument/completion #############################################

def shortlist(long_list: List[str], typed: str, lo: int = 0, hi: int = -1) -> Tuple[int, int]:
    if not typed:
        return 0, 0
    if hi < 0:
        hi = len(long_list)
    a = bisect.bisect_left(long_list, typed, lo, hi)
    b = bisect.bisect_left(long_list, typed[:-1] + chr(ord(typed[-1]) + 1), lo, hi)
    return a, b


#######################################################################
#
# Language-Server-Protocol data structures (AUTOGENERATED: Don't edit!)
#
#######################################################################


##### BEGIN OF LSP SPECS



integer = float

uinteger = float

decimal = float

LSPAny = Union['LSPObject', 'LSPArray', str, int, float, bool, None]

LSPObject = Dict[str, LSPAny]

LSPArray = List[LSPAny]


class Message(TypedDict):
    jsonrpc: str


class RequestMessage(Message, TypedDict):
    id: Union[int, str]
    method: str
    params: NotRequired[Union[List, Dict]]


class ResponseMessage(Message, TypedDict):
    id: Union[int, str, None]
    result: NotRequired[LSPAny]
    error: NotRequired['ResponseError']


class ResponseError(TypedDict):
    code: int
    message: str
    data: NotRequired[LSPAny]

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


class NotificationMessage(Message, TypedDict):
    method: str
    params: NotRequired[Union[List, Dict]]


class CancelParams(TypedDict):
    id: Union[int, str]

ProgressToken = Union[int, str]

T = TypeVar('T')

class ProgressParams(Generic[T], TypedDict):
    token: ProgressToken
    value: T


class HoverParams(TypedDict):
    class Position_0(TypedDict):
        line: int
        character: int
    textDocument: str
    position: Position_0


class HoverResult(TypedDict):
    value: str

DocumentUri = str

URI = str


class RegularExpressionsClientCapabilities(TypedDict):
    engine: str
    version: NotRequired[str]

EOL: List[str] = ['\n', '\r\n', '\r']


class Position(TypedDict):
    line: int
    character: int

PositionEncodingKind = str


class Range(TypedDict):
    start: Position
    end: Position


class TextDocumentItem(TypedDict):
    uri: DocumentUri
    languageId: str
    version: int
    text: str


class TextDocumentIdentifier(TypedDict):
    uri: DocumentUri


class VersionedTextDocumentIdentifier(TextDocumentIdentifier, TypedDict):
    version: int


class OptionalVersionedTextDocumentIdentifier(TextDocumentIdentifier, TypedDict):
    version: Union[int, None]


class TextDocumentPositionParams(TypedDict):
    textDocument: TextDocumentIdentifier
    position: Position


class DocumentFilter(TypedDict):
    language: NotRequired[str]
    scheme: NotRequired[str]
    pattern: NotRequired[str]

DocumentSelector = List[DocumentFilter]


class StringValue(TypedDict):
    kind: Literal['snippet']
    value: str


class TextEdit(TypedDict):
    range: Range
    newText: str


class ChangeAnnotation(TypedDict):
    label: str
    needsConfirmation: NotRequired[bool]
    description: NotRequired[str]

ChangeAnnotationIdentifier = str


class AnnotatedTextEdit(TextEdit, TypedDict):
    annotationId: ChangeAnnotationIdentifier


class SnippetTextEdit(TypedDict):
    range: Range
    snippet: StringValue
    annotationId: NotRequired[ChangeAnnotationIdentifier]


class TextDocumentEdit(TypedDict):
    textDocument: OptionalVersionedTextDocumentIdentifier
    edits: List[Union[TextEdit, AnnotatedTextEdit, SnippetTextEdit]]


class Location(TypedDict):
    uri: DocumentUri
    range: Range


class LocationLink(TypedDict):
    originSelectionRange: NotRequired[Range]
    targetUri: DocumentUri
    targetRange: Range
    targetSelectionRange: Range


class Diagnostic(TypedDict):
    range: Range
    severity: NotRequired['DiagnosticSeverity']
    code: NotRequired[Union[int, str]]
    codeDescription: NotRequired['CodeDescription']
    source: NotRequired[str]
    message: Union[str, 'MarkupContent']
    tags: NotRequired[List['DiagnosticTag']]
    relatedInformation: NotRequired[List['DiagnosticRelatedInformation']]
    data: NotRequired[LSPAny]

class DiagnosticSeverity(IntEnum):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4

DiagnosticSeverity = Literal[1, 2, 3, 4]

class DiagnosticTag(IntEnum):
    Unnecessary = 1
    Deprecated = 2

DiagnosticTag = Literal[1, 2]


class DiagnosticRelatedInformation(TypedDict):
    location: Location
    message: str


class CodeDescription(TypedDict):
    href: URI


class Command(TypedDict):
    title: str
    tooltip: NotRequired[str]
    command: str
    arguments: NotRequired[List[LSPAny]]

class MarkupKind(Enum):
    PlainText = 'plaintext'
    Markdown = 'markdown'

MarkupKind = Literal['plaintext', 'markdown']


class MarkupContent(TypedDict):
    kind: MarkupKind
    value: str


class MarkdownClientCapabilities(TypedDict):
    parser: str
    version: NotRequired[str]
    allowedTags: NotRequired[List[str]]


class CreateFileOptions(TypedDict):
    overwrite: NotRequired[bool]
    ignoreIfExists: NotRequired[bool]


class CreateFile(TypedDict):
    kind: Literal['create']
    uri: DocumentUri
    options: NotRequired[CreateFileOptions]
    annotationId: NotRequired[ChangeAnnotationIdentifier]


class RenameFileOptions(TypedDict):
    overwrite: NotRequired[bool]
    ignoreIfExists: NotRequired[bool]


class RenameFile(TypedDict):
    kind: Literal['rename']
    oldUri: DocumentUri
    newUri: DocumentUri
    options: NotRequired[RenameFileOptions]
    annotationId: NotRequired[ChangeAnnotationIdentifier]


class DeleteFileOptions(TypedDict):
    recursive: NotRequired[bool]
    ignoreIfNotExists: NotRequired[bool]


class DeleteFile(TypedDict):
    kind: Literal['delete']
    uri: DocumentUri
    options: NotRequired[DeleteFileOptions]
    annotationId: NotRequired[ChangeAnnotationIdentifier]


class WorkspaceEdit(TypedDict):
    changes: NotRequired[Dict[DocumentUri, List[TextEdit]]]
    documentChanges: NotRequired[Union[List[TextDocumentEdit], List[Union[TextDocumentEdit, CreateFile, RenameFile, DeleteFile]]]]
    changeAnnotations: NotRequired[Dict[str, ChangeAnnotation]]


class WorkspaceEditClientCapabilities(TypedDict):
    class ChangeAnnotationSupport_0(TypedDict):
        groupsOnLabel: NotRequired[bool]
    documentChanges: NotRequired[bool]
    resourceOperations: NotRequired[List['ResourceOperationKind']]
    failureHandling: NotRequired['FailureHandlingKind']
    normalizesLineEndings: NotRequired[bool]
    changeAnnotationSupport: NotRequired[ChangeAnnotationSupport_0]
    metadataSupport: NotRequired[bool]
    snippetEditSupport: NotRequired[bool]

ResourceOperationKind = Literal['create', 'rename', 'delete']


FailureHandlingKind = Literal['abort', 'transactional', 'undo', 'textOnlyTransactional']


class WorkDoneProgressBegin(TypedDict):
    kind: Literal['begin']
    title: str
    cancellable: NotRequired[bool]
    message: NotRequired[str]
    percentage: NotRequired[int]


class WorkDoneProgressReport(TypedDict):
    kind: Literal['report']
    cancellable: NotRequired[bool]
    message: NotRequired[str]
    percentage: NotRequired[int]


class WorkDoneProgressEnd(TypedDict):
    kind: Literal['end']
    message: NotRequired[str]


class WorkDoneProgressParams(TypedDict):
    workDoneToken: NotRequired[ProgressToken]


class WorkDoneProgressOptions(TypedDict):
    workDoneProgress: NotRequired[bool]


class PartialResultParams(TypedDict):
    partialResultToken: NotRequired[ProgressToken]

TraceValue = Literal['off', 'messages', 'verbose']


class InitializeParams(WorkDoneProgressParams, TypedDict):
    class ClientInfo_0(TypedDict):
        name: str
        version: NotRequired[str]
    processId: Union[int, None]
    clientInfo: NotRequired[ClientInfo_0]
    locale: NotRequired[str]
    rootPath: NotRequired[Union[str, None]]
    rootUri: Union[DocumentUri, None]
    initializationOptions: NotRequired[LSPAny]
    capabilities: 'ClientCapabilities'
    trace: NotRequired[TraceValue]
    workspaceFolders: NotRequired[Union[List['WorkspaceFolder'], None]]


class TextDocumentClientCapabilities(TypedDict):
    synchronization: NotRequired['TextDocumentSyncClientCapabilities']
    completion: NotRequired['CompletionClientCapabilities']
    hover: NotRequired['HoverClientCapabilities']
    signatureHelp: NotRequired['SignatureHelpClientCapabilities']
    declaration: NotRequired['DeclarationClientCapabilities']
    definition: NotRequired['DefinitionClientCapabilities']
    typeDefinition: NotRequired['TypeDefinitionClientCapabilities']
    implementation: NotRequired['ImplementationClientCapabilities']
    references: NotRequired['ReferenceClientCapabilities']
    documentHighlight: NotRequired['DocumentHighlightClientCapabilities']
    documentSymbol: NotRequired['DocumentSymbolClientCapabilities']
    codeAction: NotRequired['CodeActionClientCapabilities']
    codeLens: NotRequired['CodeLensClientCapabilities']
    documentLink: NotRequired['DocumentLinkClientCapabilities']
    colorProvider: NotRequired['DocumentColorClientCapabilities']
    formatting: NotRequired['DocumentFormattingClientCapabilities']
    rangeFormatting: NotRequired['DocumentRangeFormattingClientCapabilities']
    onTypeFormatting: NotRequired['DocumentOnTypeFormattingClientCapabilities']
    rename: NotRequired['RenameClientCapabilities']
    publishDiagnostics: NotRequired['PublishDiagnosticsClientCapabilities']
    foldingRange: NotRequired['FoldingRangeClientCapabilities']
    selectionRange: NotRequired['SelectionRangeClientCapabilities']
    linkedEditingRange: NotRequired['LinkedEditingRangeClientCapabilities']
    callHierarchy: NotRequired['CallHierarchyClientCapabilities']
    semanticTokens: NotRequired['SemanticTokensClientCapabilities']
    moniker: NotRequired['MonikerClientCapabilities']
    typeHierarchy: NotRequired['TypeHierarchyClientCapabilities']
    inlineValue: NotRequired['InlineValueClientCapabilities']
    inlayHint: NotRequired['InlayHintClientCapabilities']
    diagnostic: NotRequired['DiagnosticClientCapabilities']
    inlineCompletion: NotRequired['InlineCompletionClientCapabilities']


class NotebookDocumentClientCapabilities(TypedDict):
    synchronization: 'NotebookDocumentSyncClientCapabilities'


class ClientCapabilities(TypedDict):
    class Workspace_0(TypedDict):
        class FileOperations_0(TypedDict):
            dynamicRegistration: NotRequired[bool]
            didCreate: NotRequired[bool]
            willCreate: NotRequired[bool]
            didRename: NotRequired[bool]
            willRename: NotRequired[bool]
            didDelete: NotRequired[bool]
            willDelete: NotRequired[bool]
        applyEdit: NotRequired[bool]
        workspaceEdit: NotRequired[WorkspaceEditClientCapabilities]
        didChangeConfiguration: NotRequired['DidChangeConfigurationClientCapabilities']
        didChangeWatchedFiles: NotRequired['DidChangeWatchedFilesClientCapabilities']
        symbol: NotRequired['WorkspaceSymbolClientCapabilities']
        executeCommand: NotRequired['ExecuteCommandClientCapabilities']
        workspaceFolders: NotRequired[bool]
        configuration: NotRequired[bool]
        semanticTokens: NotRequired['SemanticTokensWorkspaceClientCapabilities']
        codeLens: NotRequired['CodeLensWorkspaceClientCapabilities']
        fileOperations: NotRequired[FileOperations_0]
        inlineValue: NotRequired['InlineValueWorkspaceClientCapabilities']
        inlayHint: NotRequired['InlayHintWorkspaceClientCapabilities']
        diagnostics: NotRequired['DiagnosticWorkspaceClientCapabilities']
    class Window_0(TypedDict):
        workDoneProgress: NotRequired[bool]
        showMessage: NotRequired['ShowMessageRequestClientCapabilities']
        showDocument: NotRequired['ShowDocumentClientCapabilities']
    class General_0(TypedDict):
        class StaleRequestSupport_0(TypedDict):
            cancel: bool
            retryOnContentModified: List[str]
        staleRequestSupport: NotRequired[StaleRequestSupport_0]
        regularExpressions: NotRequired[RegularExpressionsClientCapabilities]
        markdown: NotRequired[MarkdownClientCapabilities]
        positionEncodings: NotRequired[List[PositionEncodingKind]]
    workspace: NotRequired[Workspace_0]
    textDocument: NotRequired[TextDocumentClientCapabilities]
    notebookDocument: NotRequired[NotebookDocumentClientCapabilities]
    window: NotRequired[Window_0]
    general: NotRequired[General_0]
    experimental: NotRequired[LSPAny]


class InitializeResult(TypedDict):
    class ServerInfo_0(TypedDict):
        name: str
        version: NotRequired[str]
    capabilities: 'ServerCapabilities'
    serverInfo: NotRequired[ServerInfo_0]

class InitializeErrorCodes(IntEnum):
    unknownProtocolVersion = 1

InitializeErrorCodes = Literal[1]


class InitializeError(TypedDict):
    retry: bool


class ServerCapabilities(TypedDict):
    class TextDocument_0(TypedDict):
        class Diagnostic_0(TypedDict):
            markupMessageSupport: NotRequired[bool]
        diagnostic: NotRequired[Diagnostic_0]
    class Workspace_0(TypedDict):
        class FileOperations_0(TypedDict):
            didCreate: NotRequired['FileOperationRegistrationOptions']
            willCreate: NotRequired['FileOperationRegistrationOptions']
            didRename: NotRequired['FileOperationRegistrationOptions']
            willRename: NotRequired['FileOperationRegistrationOptions']
            didDelete: NotRequired['FileOperationRegistrationOptions']
            willDelete: NotRequired['FileOperationRegistrationOptions']
        workspaceFolders: NotRequired['WorkspaceFoldersServerCapabilities']
        fileOperations: NotRequired[FileOperations_0]
    positionEncoding: NotRequired[PositionEncodingKind]
    textDocumentSync: NotRequired[Union['TextDocumentSyncOptions', 'TextDocumentSyncKind']]
    notebookDocumentSync: NotRequired[Union['NotebookDocumentSyncOptions', 'NotebookDocumentSyncRegistrationOptions']]
    completionProvider: NotRequired['CompletionOptions']
    hoverProvider: NotRequired[Union[bool, 'HoverOptions']]
    signatureHelpProvider: NotRequired['SignatureHelpOptions']
    declarationProvider: NotRequired[Union[bool, 'DeclarationOptions', 'DeclarationRegistrationOptions']]
    definitionProvider: NotRequired[Union[bool, 'DefinitionOptions']]
    typeDefinitionProvider: NotRequired[Union[bool, 'TypeDefinitionOptions', 'TypeDefinitionRegistrationOptions']]
    implementationProvider: NotRequired[Union[bool, 'ImplementationOptions', 'ImplementationRegistrationOptions']]
    referencesProvider: NotRequired[Union[bool, 'ReferenceOptions']]
    documentHighlightProvider: NotRequired[Union[bool, 'DocumentHighlightOptions']]
    documentSymbolProvider: NotRequired[Union[bool, 'DocumentSymbolOptions']]
    codeActionProvider: NotRequired[Union[bool, 'CodeActionOptions']]
    codeLensProvider: NotRequired['CodeLensOptions']
    documentLinkProvider: NotRequired['DocumentLinkOptions']
    colorProvider: NotRequired[Union[bool, 'DocumentColorOptions', 'DocumentColorRegistrationOptions']]
    documentFormattingProvider: NotRequired[Union[bool, 'DocumentFormattingOptions']]
    documentRangeFormattingProvider: NotRequired[Union[bool, 'DocumentRangeFormattingOptions']]
    documentOnTypeFormattingProvider: NotRequired['DocumentOnTypeFormattingOptions']
    renameProvider: NotRequired[Union[bool, 'RenameOptions']]
    foldingRangeProvider: NotRequired[Union[bool, 'FoldingRangeOptions', 'FoldingRangeRegistrationOptions']]
    executeCommandProvider: NotRequired['ExecuteCommandOptions']
    selectionRangeProvider: NotRequired[Union[bool, 'SelectionRangeOptions', 'SelectionRangeRegistrationOptions']]
    linkedEditingRangeProvider: NotRequired[Union[bool, 'LinkedEditingRangeOptions', 'LinkedEditingRangeRegistrationOptions']]
    callHierarchyProvider: NotRequired[Union[bool, 'CallHierarchyOptions', 'CallHierarchyRegistrationOptions']]
    semanticTokensProvider: NotRequired[Union['SemanticTokensOptions', 'SemanticTokensRegistrationOptions']]
    monikerProvider: NotRequired[Union[bool, 'MonikerOptions', 'MonikerRegistrationOptions']]
    typeHierarchyProvider: NotRequired[Union[bool, 'TypeHierarchyOptions', 'TypeHierarchyRegistrationOptions']]
    inlineValueProvider: NotRequired[Union[bool, 'InlineValueOptions', 'InlineValueRegistrationOptions']]
    inlayHintProvider: NotRequired[Union[bool, 'InlayHintOptions', 'InlayHintRegistrationOptions']]
    diagnosticProvider: NotRequired[Union['DiagnosticOptions', 'DiagnosticRegistrationOptions']]
    workspaceSymbolProvider: NotRequired[Union[bool, 'WorkspaceSymbolOptions']]
    inlineCompletionProvider: NotRequired[Union[bool, 'InlineCompletionOptions']]
    textDocument: NotRequired[TextDocument_0]
    workspace: NotRequired[Workspace_0]
    experimental: NotRequired[LSPAny]


class InitializedParams(TypedDict):
    pass


class Registration(TypedDict):
    id: str
    method: str
    registerOptions: NotRequired[LSPAny]


class RegistrationParams(TypedDict):
    registrations: List[Registration]


class StaticRegistrationOptions(TypedDict):
    id: NotRequired[str]


class TextDocumentRegistrationOptions(TypedDict):
    documentSelector: Union[DocumentSelector, None]


class Unregistration(TypedDict):
    id: str
    method: str


class UnregistrationParams(TypedDict):
    unregisterations: List[Unregistration]


class SetTraceParams(TypedDict):
    value: TraceValue


class LogTraceParams(TypedDict):
    message: str
    verbose: NotRequired[str]

class TextDocumentSyncKind(IntEnum):
    None_ = 0
    Full = 1
    Incremental = 2

TextDocumentSyncKind = Literal[0, 1, 2]


class TextDocumentSyncOptions(TypedDict):
    openClose: NotRequired[bool]
    change: NotRequired[TextDocumentSyncKind]


class DidOpenTextDocumentParams(TypedDict):
    textDocument: TextDocumentItem


class TextDocumentChangeRegistrationOptions(TextDocumentRegistrationOptions, TypedDict):
    syncKind: TextDocumentSyncKind


class DidChangeTextDocumentParams(TypedDict):
    textDocument: VersionedTextDocumentIdentifier
    contentChanges: List['TextDocumentContentChangeEvent']

class TextDocumentContentChangeEvent_0(TypedDict):
    range: Range
    rangeLength: NotRequired[int]
    text: str
class TextDocumentContentChangeEvent_1(TypedDict):
    text: str
TextDocumentContentChangeEvent = Union[TextDocumentContentChangeEvent_0, TextDocumentContentChangeEvent_1]


class WillSaveTextDocumentParams(TypedDict):
    textDocument: TextDocumentIdentifier
    reason: 'TextDocumentSaveReason'

class TextDocumentSaveReason(IntEnum):
    Manual = 1
    AfterDelay = 2
    FocusOut = 3

TextDocumentSaveReason = Literal[1, 2, 3]


class SaveOptions(TypedDict):
    includeText: NotRequired[bool]


class TextDocumentSaveRegistrationOptions(TextDocumentRegistrationOptions, TypedDict):
    includeText: NotRequired[bool]


class DidSaveTextDocumentParams(TypedDict):
    textDocument: TextDocumentIdentifier
    text: NotRequired[str]


class DidCloseTextDocumentParams(TypedDict):
    textDocument: TextDocumentIdentifier


class TextDocumentSyncClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    willSave: NotRequired[bool]
    willSaveWaitUntil: NotRequired[bool]
    didSave: NotRequired[bool]


class TextDocumentSyncOptions(TypedDict):
    openClose: NotRequired[bool]
    change: NotRequired[TextDocumentSyncKind]
    willSave: NotRequired[bool]
    willSaveWaitUntil: NotRequired[bool]
    save: NotRequired[Union[bool, SaveOptions]]


class NotebookDocument(TypedDict):
    uri: URI
    notebookType: str
    version: int
    metadata: NotRequired[LSPObject]
    cells: List['NotebookCell']


class NotebookCell(TypedDict):
    kind: 'NotebookCellKind'
    document: DocumentUri
    metadata: NotRequired[LSPObject]
    executionSummary: NotRequired['ExecutionSummary']

class NotebookCellKind(IntEnum):
    Markup = 1
    Code = 2


class ExecutionSummary(TypedDict):
    executionOrder: int
    success: NotRequired[bool]


class NotebookCellTextDocumentFilter(TypedDict):
    notebook: Union[str, 'NotebookDocumentFilter']
    language: NotRequired[str]

class NotebookDocumentFilter_0(TypedDict):
    notebookType: str
    scheme: NotRequired[str]
    pattern: NotRequired[str]
class NotebookDocumentFilter_1(TypedDict):
    notebookType: NotRequired[str]
    scheme: str
    pattern: NotRequired[str]
class NotebookDocumentFilter_2(TypedDict):
    notebookType: NotRequired[str]
    scheme: NotRequired[str]
    pattern: str
NotebookDocumentFilter = Union[NotebookDocumentFilter_0, NotebookDocumentFilter_1, NotebookDocumentFilter_2]


class NotebookDocumentSyncClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    executionSummarySupport: NotRequired[bool]


class NotebookDocumentSyncOptions(TypedDict):
    class NotebookSelector_0(TypedDict):
        class Cells_0(TypedDict):
            language: str
        notebook: Union[str, NotebookDocumentFilter]
        cells: NotRequired[List[Cells_0]]
    class NotebookSelector_1(TypedDict):
        class Cells_0(TypedDict):
            language: str
        notebook: NotRequired[Union[str, NotebookDocumentFilter]]
        cells: List[Cells_0]
    notebookSelector: List[Union[NotebookSelector_0, NotebookSelector_1]]
    save: NotRequired[bool]


class NotebookDocumentSyncRegistrationOptions(NotebookDocumentSyncOptions, StaticRegistrationOptions, TypedDict):
    pass


class DidOpenNotebookDocumentParams(TypedDict):
    notebookDocument: NotebookDocument
    cellTextDocuments: List[TextDocumentItem]


class DidChangeNotebookDocumentParams(TypedDict):
    notebookDocument: 'VersionedNotebookDocumentIdentifier'
    change: 'NotebookDocumentChangeEvent'


class VersionedNotebookDocumentIdentifier(TypedDict):
    version: int
    uri: URI


class NotebookDocumentChangeEvent(TypedDict):
    class Cells_0(TypedDict):
        class Structure_0(TypedDict):
            array: 'NotebookCellArrayChange'
            didOpen: NotRequired[List[TextDocumentItem]]
            didClose: NotRequired[List[TextDocumentIdentifier]]
        class TextContent_0(TypedDict):
            document: VersionedTextDocumentIdentifier
            changes: List[TextDocumentContentChangeEvent]
        structure: NotRequired[Structure_0]
        data: NotRequired[List[NotebookCell]]
        textContent: NotRequired[List[TextContent_0]]
    metadata: NotRequired[LSPObject]
    cells: NotRequired[Cells_0]


class NotebookCellArrayChange(TypedDict):
    start: int
    deleteCount: int
    cells: NotRequired[List[NotebookCell]]


class DidSaveNotebookDocumentParams(TypedDict):
    notebookDocument: 'NotebookDocumentIdentifier'


class DidCloseNotebookDocumentParams(TypedDict):
    notebookDocument: 'NotebookDocumentIdentifier'
    cellTextDocuments: List[TextDocumentIdentifier]


class NotebookDocumentIdentifier(TypedDict):
    uri: URI


class DeclarationClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    linkSupport: NotRequired[bool]


class DeclarationOptions(WorkDoneProgressOptions, TypedDict):
    pass


class DeclarationRegistrationOptions(DeclarationOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions, TypedDict):
    pass


class DeclarationParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, TypedDict):
    pass


class DefinitionClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    linkSupport: NotRequired[bool]


class DefinitionOptions(WorkDoneProgressOptions, TypedDict):
    pass


class DefinitionRegistrationOptions(TextDocumentRegistrationOptions, DefinitionOptions, TypedDict):
    pass


class DefinitionParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, TypedDict):
    pass


class TypeDefinitionClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    linkSupport: NotRequired[bool]


class TypeDefinitionOptions(WorkDoneProgressOptions, TypedDict):
    pass


class TypeDefinitionRegistrationOptions(TextDocumentRegistrationOptions, TypeDefinitionOptions, StaticRegistrationOptions, TypedDict):
    pass


class TypeDefinitionParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, TypedDict):
    pass


class ImplementationClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    linkSupport: NotRequired[bool]


class ImplementationOptions(WorkDoneProgressOptions, TypedDict):
    pass


class ImplementationRegistrationOptions(TextDocumentRegistrationOptions, ImplementationOptions, StaticRegistrationOptions, TypedDict):
    pass


class ImplementationParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, TypedDict):
    pass


class ReferenceClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class ReferenceOptions(WorkDoneProgressOptions, TypedDict):
    pass


class ReferenceRegistrationOptions(TextDocumentRegistrationOptions, ReferenceOptions, TypedDict):
    pass


class ReferenceParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, TypedDict):
    context: 'ReferenceContext'


class ReferenceContext(TypedDict):
    includeDeclaration: bool


class CallHierarchyClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class CallHierarchyOptions(WorkDoneProgressOptions, TypedDict):
    pass


class CallHierarchyRegistrationOptions(TextDocumentRegistrationOptions, CallHierarchyOptions, StaticRegistrationOptions, TypedDict):
    pass


class CallHierarchyPrepareParams(TextDocumentPositionParams, WorkDoneProgressParams, TypedDict):
    pass


class CallHierarchyItem(TypedDict):
    name: str
    kind: 'SymbolKind'
    tags: NotRequired[List['SymbolTag']]
    detail: NotRequired[str]
    uri: DocumentUri
    range: Range
    selectionRange: Range
    data: NotRequired[LSPAny]


class CallHierarchyIncomingCallsParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    item: CallHierarchyItem


class CallHierarchyIncomingCall(TypedDict):
    from_: CallHierarchyItem
    fromRanges: List[Range]


class CallHierarchyOutgoingCallsParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    item: CallHierarchyItem


class CallHierarchyOutgoingCall(TypedDict):
    to: CallHierarchyItem
    fromRanges: List[Range]

class TypeHierarchyClientCapabilities_0(TypedDict):
    dynamicRegistration: NotRequired[bool]
TypeHierarchyClientCapabilities = TypeHierarchyClientCapabilities_0


class TypeHierarchyOptions(WorkDoneProgressOptions, TypedDict):
    pass


class TypeHierarchyRegistrationOptions(TextDocumentRegistrationOptions, TypeHierarchyOptions, StaticRegistrationOptions, TypedDict):
    pass


class TypeHierarchyPrepareParams(TextDocumentPositionParams, WorkDoneProgressParams, TypedDict):
    pass


class TypeHierarchyItem(TypedDict):
    name: str
    kind: 'SymbolKind'
    tags: NotRequired[List['SymbolTag']]
    detail: NotRequired[str]
    uri: DocumentUri
    range: Range
    selectionRange: Range
    data: NotRequired[LSPAny]


class TypeHierarchySupertypesParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    item: TypeHierarchyItem


class TypeHierarchySubtypesParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    item: TypeHierarchyItem


class DocumentHighlightClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class DocumentHighlightOptions(WorkDoneProgressOptions, TypedDict):
    pass


class DocumentHighlightRegistrationOptions(TextDocumentRegistrationOptions, DocumentHighlightOptions, TypedDict):
    pass


class DocumentHighlightParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, TypedDict):
    pass


class DocumentHighlight(TypedDict):
    range: Range
    kind: NotRequired['DocumentHighlightKind']

class DocumentHighlightKind(IntEnum):
    Text = 1
    Read = 2
    Write = 3

DocumentHighlightKind = Literal[1, 2, 3]


class DocumentLinkClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    tooltipSupport: NotRequired[bool]


class DocumentLinkOptions(WorkDoneProgressOptions, TypedDict):
    resolveProvider: NotRequired[bool]


class DocumentLinkRegistrationOptions(TextDocumentRegistrationOptions, DocumentLinkOptions, TypedDict):
    pass


class DocumentLinkParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier


class DocumentLink(TypedDict):
    range: Range
    target: NotRequired[URI]
    tooltip: NotRequired[str]
    data: NotRequired[LSPAny]


class HoverClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    contentFormat: NotRequired[List[MarkupKind]]


class HoverOptions(WorkDoneProgressOptions, TypedDict):
    pass


class HoverRegistrationOptions(TextDocumentRegistrationOptions, HoverOptions, TypedDict):
    pass


class HoverParams(TextDocumentPositionParams, WorkDoneProgressParams, TypedDict):
    pass


class Hover(TypedDict):
    contents: Union['MarkedString', List['MarkedString'], MarkupContent]
    range: NotRequired[Range]

class MarkedString_1(TypedDict):
    language: str
    value: str
MarkedString = Union[str, MarkedString_1]


class CodeLensClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    resolveSupport: NotRequired['ClientCodeLensResolveOptions']

class ClientCodeLensResolveOptions_0(TypedDict):
    properties: List[str]
ClientCodeLensResolveOptions = ClientCodeLensResolveOptions_0


class CodeLensOptions(WorkDoneProgressOptions, TypedDict):
    resolveProvider: NotRequired[bool]


class CodeLensRegistrationOptions(TextDocumentRegistrationOptions, CodeLensOptions, TypedDict):
    pass


class CodeLensParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier


class CodeLens(TypedDict):
    range: Range
    command: NotRequired[Command]
    data: NotRequired[LSPAny]


class CodeLensWorkspaceClientCapabilities(TypedDict):
    refreshSupport: NotRequired[bool]


class FoldingRangeClientCapabilities(TypedDict):
    class FoldingRangeKind_0(TypedDict):
        valueSet: NotRequired[List['FoldingRangeKind']]
    class FoldingRange_0(TypedDict):
        collapsedText: NotRequired[bool]
    dynamicRegistration: NotRequired[bool]
    rangeLimit: NotRequired[int]
    lineFoldingOnly: NotRequired[bool]
    foldingRangeKind: NotRequired[FoldingRangeKind_0]
    foldingRange: NotRequired[FoldingRange_0]


class FoldingRangeOptions(WorkDoneProgressOptions, TypedDict):
    pass


class FoldingRangeRegistrationOptions(TextDocumentRegistrationOptions, FoldingRangeOptions, StaticRegistrationOptions, TypedDict):
    pass


class FoldingRangeParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier

class FoldingRangeKind(Enum):
    Comment = 'comment'
    Imports = 'imports'
    Region = 'region'

FoldingRangeKind = str


class FoldingRange(TypedDict):
    startLine: int
    startCharacter: NotRequired[int]
    endLine: int
    endCharacter: NotRequired[int]
    kind: NotRequired[FoldingRangeKind]
    collapsedText: NotRequired[str]


class FoldingRangeWorkspaceClientCapabilities(TypedDict):
    refreshSupport: NotRequired[bool]


class SelectionRangeClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class SelectionRangeOptions(WorkDoneProgressOptions, TypedDict):
    pass


class SelectionRangeRegistrationOptions(SelectionRangeOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions, TypedDict):
    pass


class SelectionRangeParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier
    positions: List[Position]


class SelectionRange(TypedDict):
    range: Range
    parent: NotRequired['SelectionRange']


class DocumentSymbolClientCapabilities(TypedDict):
    class SymbolKind_0(TypedDict):
        valueSet: NotRequired[List['SymbolKind']]
    class TagSupport_0(TypedDict):
        valueSet: List['SymbolTag']
    dynamicRegistration: NotRequired[bool]
    symbolKind: NotRequired[SymbolKind_0]
    hierarchicalDocumentSymbolSupport: NotRequired[bool]
    tagSupport: NotRequired[TagSupport_0]
    labelSupport: NotRequired[bool]


class DocumentSymbolOptions(WorkDoneProgressOptions, TypedDict):
    label: NotRequired[str]


class DocumentSymbolRegistrationOptions(TextDocumentRegistrationOptions, DocumentSymbolOptions, TypedDict):
    pass


class DocumentSymbolParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier

class SymbolKind(IntEnum):
    File = 1
    Module = 2
    Namespace = 3
    Package = 4
    Class = 5
    Method = 6
    Property = 7
    Field = 8
    Constructor = 9
    Enum = 10
    Interface = 11
    Function = 12
    Variable = 13
    Constant = 14
    String = 15
    Number = 16
    Boolean = 17
    Array = 18
    Object = 19
    Key = 20
    Null = 21
    EnumMember = 22
    Struct = 23
    Event = 24
    Operator = 25
    TypeParameter = 26

SymbolKind = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]

class SymbolTag(IntEnum):
    Deprecated = 1

SymbolTag = Literal[1]

class DocumentSymbol(TypedDict):
    name: str
    detail: NotRequired[str]
    kind: SymbolKind
    tags: NotRequired[List[SymbolTag]]
    deprecated: NotRequired[bool]
    range: Range
    selectionRange: Range
    children: NotRequired[List['DocumentSymbol']]

class SymbolInformation(TypedDict):
    name: str
    kind: SymbolKind
    tags: NotRequired[List[SymbolTag]]
    deprecated: NotRequired[bool]
    location: Location
    containerName: NotRequired[str]

class SemanticTokenTypes(Enum):
    namespace = 'namespace'
    type = 'type'
    class_ = 'class'
    enum = 'enum'
    interface = 'interface'
    struct = 'struct'
    typeParameter = 'typeParameter'
    parameter = 'parameter'
    variable = 'variable'
    property = 'property'
    enumMember = 'enumMember'
    event = 'event'
    function = 'function'
    method = 'method'
    macro = 'macro'
    keyword = 'keyword'
    modifier = 'modifier'
    comment = 'comment'
    string = 'string'
    number = 'number'
    regexp = 'regexp'
    operator = 'operator'
    decorator = 'decorator'

class SemanticTokenModifiers(Enum):
    declaration = 'declaration'
    definition = 'definition'
    readonly = 'readonly'
    static = 'static'
    deprecated = 'deprecated'
    abstract = 'abstract'
    async_ = 'async'
    modification = 'modification'
    documentation = 'documentation'
    defaultLibrary = 'defaultLibrary'

class TokenFormat(Enum):
    Relative = 'relative'

TokenFormat = Literal['relative']


class SemanticTokensLegend(TypedDict):
    tokenTypes: List[str]
    tokenModifiers: List[str]


class SemanticTokensClientCapabilities(TypedDict):
    class Requests_0(TypedDict):
        class Range_1(TypedDict):
            pass
        class Full_1(TypedDict):
            delta: NotRequired[bool]
        range: NotRequired[Union[bool, Range_1]]
        full: NotRequired[Union[bool, Full_1]]
    dynamicRegistration: NotRequired[bool]
    requests: Requests_0
    tokenTypes: List[str]
    tokenModifiers: List[str]
    formats: List[TokenFormat]
    overlappingTokenSupport: NotRequired[bool]
    multilineTokenSupport: NotRequired[bool]
    serverCancelSupport: NotRequired[bool]
    augmentsSyntaxTokens: NotRequired[bool]


class SemanticTokensOptions(WorkDoneProgressOptions, TypedDict):
    class Range_1(TypedDict):
        pass
    class Full_1(TypedDict):
        delta: NotRequired[bool]
    legend: SemanticTokensLegend
    range: NotRequired[Union[bool, Range_1]]
    full: NotRequired[Union[bool, Full_1]]


class SemanticTokensRegistrationOptions(TextDocumentRegistrationOptions, SemanticTokensOptions, StaticRegistrationOptions, TypedDict):
    pass


class SemanticTokensParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier


class SemanticTokens(TypedDict):
    resultId: NotRequired[str]
    data: List[int]


class SemanticTokensPartialResult(TypedDict):
    data: List[int]


class SemanticTokensDeltaParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier
    previousResultId: str


class SemanticTokensDelta(TypedDict):
    resultId: NotRequired[str]
    edits: List['SemanticTokensEdit']


class SemanticTokensEdit(TypedDict):
    start: int
    deleteCount: int
    data: NotRequired[List[int]]


class SemanticTokensDeltaPartialResult(TypedDict):
    edits: List[SemanticTokensEdit]


class SemanticTokensRangeParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier
    range: Range


class SemanticTokensWorkspaceClientCapabilities(TypedDict):
    refreshSupport: NotRequired[bool]


class InlayHintClientCapabilities(TypedDict):
    class ResolveSupport_0(TypedDict):
        properties: List[str]
    dynamicRegistration: NotRequired[bool]
    resolveSupport: NotRequired[ResolveSupport_0]


class InlayHintOptions(WorkDoneProgressOptions, TypedDict):
    resolveProvider: NotRequired[bool]


class InlayHintRegistrationOptions(InlayHintOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions, TypedDict):
    pass


class InlayHintParams(WorkDoneProgressParams, TypedDict):
    textDocument: TextDocumentIdentifier
    range: Range


class InlayHint(TypedDict):
    position: Position
    label: Union[str, List['InlayHintLabelPart']]
    kind: NotRequired['InlayHintKind']
    textEdits: NotRequired[List[TextEdit]]
    tooltip: NotRequired[Union[str, MarkupContent]]
    paddingLeft: NotRequired[bool]
    paddingRight: NotRequired[bool]
    data: NotRequired[LSPAny]


class InlayHintLabelPart(TypedDict):
    value: str
    tooltip: NotRequired[Union[str, MarkupContent]]
    location: NotRequired[Location]
    command: NotRequired[Command]

class InlayHintKind(IntEnum):
    Type = 1
    Parameter = 2

InlayHintKind = Literal[1, 2]


class InlayHintWorkspaceClientCapabilities(TypedDict):
    refreshSupport: NotRequired[bool]


class InlineValueClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class InlineValueOptions(WorkDoneProgressOptions, TypedDict):
    pass


class InlineValueRegistrationOptions(InlineValueOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions, TypedDict):
    pass


class InlineValueParams(WorkDoneProgressParams, TypedDict):
    textDocument: TextDocumentIdentifier
    range: Range
    context: 'InlineValueContext'


class InlineValueContext(TypedDict):
    frameId: int
    stoppedLocation: Range


class InlineValueText(TypedDict):
    range: Range
    text: str


class InlineValueVariableLookup(TypedDict):
    range: Range
    iableName: NotRequired[str]
    caseSensitiveLookup: bool


class InlineValueEvaluatableExpression(TypedDict):
    range: Range
    expression: NotRequired[str]

InlineValue = Union[InlineValueText, InlineValueVariableLookup, InlineValueEvaluatableExpression]


class InlineValueWorkspaceClientCapabilities(TypedDict):
    refreshSupport: NotRequired[bool]


class MonikerClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class MonikerOptions(WorkDoneProgressOptions, TypedDict):
    pass


class MonikerRegistrationOptions(TextDocumentRegistrationOptions, MonikerOptions, TypedDict):
    pass


class MonikerParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, TypedDict):
    pass

class UniquenessLevel(Enum):
    document = 'document'
    project = 'project'
    group = 'group'
    scheme = 'scheme'
    global_ = 'global'

class MonikerKind(Enum):
    import_ = 'import'
    export = 'export'
    local = 'local'


class Moniker(TypedDict):
    scheme: str
    identifier: str
    unique: UniquenessLevel
    kind: NotRequired[MonikerKind]


class CompletionClientCapabilities(TypedDict):
    class CompletionItem_0(TypedDict):
        class TagSupport_0(TypedDict):
            valueSet: List['CompletionItemTag']
        class ResolveSupport_0(TypedDict):
            properties: List[str]
        class InsertTextModeSupport_0(TypedDict):
            valueSet: List['InsertTextMode']
        snippetSupport: NotRequired[bool]
        commitCharactersSupport: NotRequired[bool]
        documentationFormat: NotRequired[List[MarkupKind]]
        deprecatedSupport: NotRequired[bool]
        preselectSupport: NotRequired[bool]
        tagSupport: NotRequired[TagSupport_0]
        insertReplaceSupport: NotRequired[bool]
        resolveSupport: NotRequired[ResolveSupport_0]
        insertTextModeSupport: NotRequired[InsertTextModeSupport_0]
        labelDetailsSupport: NotRequired[bool]
    class CompletionItemKind_0(TypedDict):
        valueSet: NotRequired[List['CompletionItemKind']]
    class CompletionList_0(TypedDict):
        itemDefaults: NotRequired[List[str]]
    dynamicRegistration: NotRequired[bool]
    completionItem: NotRequired[CompletionItem_0]
    completionItemKind: NotRequired[CompletionItemKind_0]
    contextSupport: NotRequired[bool]
    insertTextMode: NotRequired['InsertTextMode']
    completionList: NotRequired[CompletionList_0]


class CompletionOptions(WorkDoneProgressOptions, TypedDict):
    class CompletionItem_0(TypedDict):
        labelDetailsSupport: NotRequired[bool]
    triggerCharacters: NotRequired[List[str]]
    allCommitCharacters: NotRequired[List[str]]
    resolveProvider: NotRequired[bool]
    completionItem: NotRequired[CompletionItem_0]


class CompletionRegistrationOptions(TextDocumentRegistrationOptions, CompletionOptions, TypedDict):
    pass


class CompletionParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, TypedDict):
    context: NotRequired['CompletionContext']

class CompletionTriggerKind(IntEnum):
    Invoked = 1
    TriggerCharacter = 2
    TriggerForIncompleteCompletions = 3

CompletionTriggerKind = Literal[1, 2, 3]


class CompletionContext(TypedDict):
    triggerKind: CompletionTriggerKind
    triggerCharacter: NotRequired[str]


class CompletionList(TypedDict):
    class ItemDefaults_0(TypedDict):
        class EditRange_1(TypedDict):
            insert: Range
            replace: Range
        commitCharacters: NotRequired[List[str]]
        editRange: NotRequired[Union[Range, EditRange_1]]
        insertTextFormat: NotRequired['InsertTextFormat']
        insertTextMode: NotRequired['InsertTextMode']
        data: NotRequired[LSPAny]
    isIncomplete: bool
    itemDefaults: NotRequired[ItemDefaults_0]
    items: List['CompletionItem']

class InsertTextFormat(IntEnum):
    PlainText = 1
    Snippet = 2

InsertTextFormat = Literal[1, 2]

class CompletionItemTag(IntEnum):
    Deprecated = 1

CompletionItemTag = Literal[1]


class InsertReplaceEdit(TypedDict):
    newText: str
    insert: Range
    replace: Range

class InsertTextMode(IntEnum):
    asIs = 1
    adjustIndentation = 2

InsertTextMode = Literal[1, 2]


class CompletionItemLabelDetails(TypedDict):
    detail: NotRequired[str]
    description: NotRequired[str]


class CompletionItem(TypedDict):
    label: str
    labelDetails: NotRequired[CompletionItemLabelDetails]
    kind: NotRequired['CompletionItemKind']
    tags: NotRequired[List[CompletionItemTag]]
    detail: NotRequired[str]
    documentation: NotRequired[Union[str, MarkupContent]]
    deprecated: NotRequired[bool]
    preselect: NotRequired[bool]
    sortText: NotRequired[str]
    filterText: NotRequired[str]
    insertText: NotRequired[str]
    insertTextFormat: NotRequired[InsertTextFormat]
    insertTextMode: NotRequired[InsertTextMode]
    textEdit: NotRequired[Union[TextEdit, InsertReplaceEdit]]
    textEditText: NotRequired[str]
    additionalTextEdits: NotRequired[List[TextEdit]]
    commitCharacters: NotRequired[List[str]]
    command: NotRequired[Command]
    data: NotRequired[LSPAny]

class CompletionItemKind(IntEnum):
    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18
    Folder = 19
    EnumMember = 20
    Constant = 21
    Struct = 22
    Event = 23
    Operator = 24
    TypeParameter = 25

CompletionItemKind = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]


class PublishDiagnosticsClientCapabilities(TypedDict):
    class TagSupport_0(TypedDict):
        valueSet: List[DiagnosticTag]
    relatedInformation: NotRequired[bool]
    tagSupport: NotRequired[TagSupport_0]
    versionSupport: NotRequired[bool]
    codeDescriptionSupport: NotRequired[bool]
    dataSupport: NotRequired[bool]


class PublishDiagnosticsParams(TypedDict):
    uri: DocumentUri
    version: NotRequired[int]
    diagnostics: List[Diagnostic]


class DiagnosticClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    relatedDocumentSupport: NotRequired[bool]
    markupMessageSupport: NotRequired[bool]


class DiagnosticOptions(WorkDoneProgressOptions, TypedDict):
    identifier: NotRequired[str]
    interFileDependencies: bool
    workspaceDiagnostics: bool


class DiagnosticRegistrationOptions(TextDocumentRegistrationOptions, DiagnosticOptions, StaticRegistrationOptions, TypedDict):
    pass


class DocumentDiagnosticParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier
    identifier: NotRequired[str]
    previousResultId: NotRequired[str]

DocumentDiagnosticReport = Union['RelatedFullDocumentDiagnosticReport', 'RelatedUnchangedDocumentDiagnosticReport']

class DocumentDiagnosticReportKind(Enum):
    Full = 'full'
    Unchanged = 'unchanged'

DocumentDiagnosticReportKind = Literal['full', 'unchanged']


class FullDocumentDiagnosticReport(TypedDict):
    kind: 'DocumentDiagnosticReportKindFull'
    resultId: NotRequired[str]
    items: List[Diagnostic]


class UnchangedDocumentDiagnosticReport(TypedDict):
    kind: 'DocumentDiagnosticReportKindUnchanged'
    resultId: str


class RelatedFullDocumentDiagnosticReport(FullDocumentDiagnosticReport, TypedDict):
    relatedDocuments: NotRequired[Dict[str, Union[FullDocumentDiagnosticReport, UnchangedDocumentDiagnosticReport]]]


class RelatedUnchangedDocumentDiagnosticReport(UnchangedDocumentDiagnosticReport, TypedDict):
    relatedDocuments: NotRequired[Dict[str, Union[FullDocumentDiagnosticReport, UnchangedDocumentDiagnosticReport]]]


class DocumentDiagnosticReportPartialResult(TypedDict):
    relatedDocuments: Dict[str, Union[FullDocumentDiagnosticReport, UnchangedDocumentDiagnosticReport]]


class DiagnosticServerCancellationData(TypedDict):
    retriggerRequest: bool


class WorkspaceDiagnosticParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    identifier: NotRequired[str]
    previousResultIds: List['PreviousResultId']


class PreviousResultId(TypedDict):
    uri: DocumentUri
    value: str


class WorkspaceDiagnosticReport(TypedDict):
    items: List['WorkspaceDocumentDiagnosticReport']


class WorkspaceFullDocumentDiagnosticReport(FullDocumentDiagnosticReport, TypedDict):
    uri: DocumentUri
    version: Union[int, None]


class WorkspaceUnchangedDocumentDiagnosticReport(UnchangedDocumentDiagnosticReport, TypedDict):
    uri: DocumentUri
    version: Union[int, None]

WorkspaceDocumentDiagnosticReport = Union[WorkspaceFullDocumentDiagnosticReport, WorkspaceUnchangedDocumentDiagnosticReport]


class WorkspaceDiagnosticReportPartialResult(TypedDict):
    items: List[WorkspaceDocumentDiagnosticReport]


class DiagnosticWorkspaceClientCapabilities(TypedDict):
    refreshSupport: NotRequired[bool]


class SignatureHelpClientCapabilities(TypedDict):
    class SignatureInformation_0(TypedDict):
        class ParameterInformation_0(TypedDict):
            labelOffsetSupport: NotRequired[bool]
        documentationFormat: NotRequired[List[MarkupKind]]
        parameterInformation: NotRequired[ParameterInformation_0]
        activeParameterSupport: NotRequired[bool]
        noActiveParameterSupport: NotRequired[bool]
    dynamicRegistration: NotRequired[bool]
    signatureInformation: NotRequired[SignatureInformation_0]
    contextSupport: NotRequired[bool]


class SignatureHelpOptions(WorkDoneProgressOptions, TypedDict):
    triggerCharacters: NotRequired[List[str]]
    retriggerCharacters: NotRequired[List[str]]


class SignatureHelpRegistrationOptions(TextDocumentRegistrationOptions, SignatureHelpOptions, TypedDict):
    pass


class SignatureHelpParams(TextDocumentPositionParams, WorkDoneProgressParams, TypedDict):
    context: NotRequired['SignatureHelpContext']

class SignatureHelpTriggerKind(IntEnum):
    Invoked = 1
    TriggerCharacter = 2
    ContentChange = 3

SignatureHelpTriggerKind = Literal[1, 2, 3]


class SignatureHelpContext(TypedDict):
    triggerKind: SignatureHelpTriggerKind
    triggerCharacter: NotRequired[str]
    isRetrigger: bool
    activeSignatureHelp: NotRequired['SignatureHelp']


class SignatureHelp(TypedDict):
    signatures: List['SignatureInformation']
    activeSignature: NotRequired[int]
    activeParameter: NotRequired[Union[int, None]]


class SignatureInformation(TypedDict):
    label: str
    documentation: NotRequired[Union[str, MarkupContent]]
    parameters: NotRequired[List['ParameterInformation']]
    activeParameter: NotRequired[Union[int, None]]


class ParameterInformation(TypedDict):
    label: Union[str, Tuple[int, int]]
    documentation: NotRequired[Union[str, MarkupContent]]


class CodeActionClientCapabilities(TypedDict):
    class CodeActionLiteralSupport_0(TypedDict):
        class CodeActionKind_0(TypedDict):
            valueSet: List['CodeActionKind']
        codeActionKind: CodeActionKind_0
    class ResolveSupport_0(TypedDict):
        properties: List[str]
    dynamicRegistration: NotRequired[bool]
    codeActionLiteralSupport: NotRequired[CodeActionLiteralSupport_0]
    isPreferredSupport: NotRequired[bool]
    disabledSupport: NotRequired[bool]
    dataSupport: NotRequired[bool]
    resolveSupport: NotRequired[ResolveSupport_0]
    honorsChangeAnnotations: NotRequired[bool]
    documentationSupport: NotRequired[bool]


class CodeActionKindDocumentation(TypedDict):
    kind: 'CodeActionKind'
    command: Command


class CodeActionOptions(WorkDoneProgressOptions, TypedDict):
    codeActionKinds: NotRequired[List['CodeActionKind']]
    documentation: NotRequired[List[CodeActionKindDocumentation]]
    resolveProvider: NotRequired[bool]


class CodeActionRegistrationOptions(TextDocumentRegistrationOptions, CodeActionOptions, TypedDict):
    pass


class CodeActionParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier
    range: Range
    context: 'CodeActionContext'

CodeActionKind = str


class CodeActionContext(TypedDict):
    diagnostics: List[Diagnostic]
    only: NotRequired[List[CodeActionKind]]
    triggerKind: NotRequired['CodeActionTriggerKind']

class CodeActionTriggerKind(IntEnum):
    Invoked = 1
    Automatic = 2

CodeActionTriggerKind = Literal[1, 2]


class CodeAction(TypedDict):
    class Disabled_0(TypedDict):
        reason: str
    title: str
    kind: NotRequired[CodeActionKind]
    diagnostics: NotRequired[List[Diagnostic]]
    isPreferred: NotRequired[bool]
    disabled: NotRequired[Disabled_0]
    edit: NotRequired[WorkspaceEdit]
    command: NotRequired[Command]
    data: NotRequired[LSPAny]


class DocumentColorClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class DocumentColorOptions(WorkDoneProgressOptions, TypedDict):
    pass


class DocumentColorRegistrationOptions(TextDocumentRegistrationOptions, StaticRegistrationOptions, DocumentColorOptions, TypedDict):
    pass


class DocumentColorParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier


class ColorInformation(TypedDict):
    range: Range
    color: 'Color'


class Color(TypedDict):
    red: float
    green: float
    blue: float
    alpha: float


class ColorPresentationParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    textDocument: TextDocumentIdentifier
    color: Color
    range: Range


class ColorPresentation(TypedDict):
    label: str
    textEdit: NotRequired[TextEdit]
    additionalTextEdits: NotRequired[List[TextEdit]]


class DocumentFormattingClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class DocumentFormattingOptions(WorkDoneProgressOptions, TypedDict):
    pass


class DocumentFormattingRegistrationOptions(TextDocumentRegistrationOptions, DocumentFormattingOptions, TypedDict):
    pass


class DocumentFormattingParams(WorkDoneProgressParams, TypedDict):
    textDocument: TextDocumentIdentifier
    options: 'FormattingOptions'


class FormattingOptions(TypedDict):
    tabSize: int
    insertSpaces: bool
    trimTrailingWhitespace: NotRequired[bool]
    insertFinalNewline: NotRequired[bool]
    trimFinalNewlines: NotRequired[bool]


class DocumentRangeFormattingClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    rangesSupport: NotRequired[bool]


class DocumentRangeFormattingOptions(WorkDoneProgressOptions, TypedDict):
    rangesSupport: NotRequired[bool]


class DocumentRangeFormattingRegistrationOptions(TextDocumentRegistrationOptions, DocumentRangeFormattingOptions, TypedDict):
    pass


class DocumentRangeFormattingParams(WorkDoneProgressParams, TypedDict):
    textDocument: TextDocumentIdentifier
    range: Range
    options: FormattingOptions


class DocumentRangesFormattingParams(WorkDoneProgressParams, TypedDict):
    textDocument: TextDocumentIdentifier
    ranges: List[Range]
    options: FormattingOptions


class DocumentOnTypeFormattingClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class DocumentOnTypeFormattingOptions(TypedDict):
    firstTriggerCharacter: str
    moreTriggerCharacter: NotRequired[List[str]]


class DocumentOnTypeFormattingRegistrationOptions(TextDocumentRegistrationOptions, DocumentOnTypeFormattingOptions, TypedDict):
    pass


class DocumentOnTypeFormattingParams(TypedDict):
    textDocument: TextDocumentIdentifier
    position: Position
    ch: str
    options: FormattingOptions

class PrepareSupportDefaultBehavior(IntEnum):
    Identifier = 1

PrepareSupportDefaultBehavior = Literal[1]


class RenameClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    prepareSupport: NotRequired[bool]
    prepareSupportDefaultBehavior: NotRequired[PrepareSupportDefaultBehavior]
    honorsChangeAnnotations: NotRequired[bool]


class RenameOptions(WorkDoneProgressOptions, TypedDict):
    prepareProvider: NotRequired[bool]


class RenameRegistrationOptions(TextDocumentRegistrationOptions, RenameOptions, TypedDict):
    pass


class RenameParams(TextDocumentPositionParams, WorkDoneProgressParams, TypedDict):
    newName: str


class PrepareRenameParams(TextDocumentPositionParams, WorkDoneProgressParams, TypedDict):
    pass


class LinkedEditingRangeClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class LinkedEditingRangeOptions(WorkDoneProgressOptions, TypedDict):
    pass


class LinkedEditingRangeRegistrationOptions(TextDocumentRegistrationOptions, LinkedEditingRangeOptions, StaticRegistrationOptions, TypedDict):
    pass


class LinkedEditingRangeParams(TextDocumentPositionParams, WorkDoneProgressParams, TypedDict):
    pass


class LinkedEditingRanges(TypedDict):
    ranges: List[Range]
    wordPattern: NotRequired[str]


class InlineCompletionClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class InlineCompletionOptions(WorkDoneProgressOptions, TypedDict):
    pass


class InlineCompletionRegistrationOptions(InlineCompletionOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions, TypedDict):
    pass


class InlineCompletionParams(TextDocumentPositionParams, WorkDoneProgressParams, TypedDict):
    context: 'InlineCompletionContext'


class InlineCompletionContext(TypedDict):
    triggerKind: 'InlineCompletionTriggerKind'
    selectedCompletionInfo: NotRequired['SelectedCompletionInfo']

class InlineCompletionTriggerKind(IntEnum):
    Invoked = 1
    Automatic = 2

InlineCompletionTriggerKind = Literal[1, 2]


class SelectedCompletionInfo(TypedDict):
    range: Range
    text: str


class InlineCompletionList(TypedDict):
    items: List['InlineCompletionItem']


class InlineCompletionItem(TypedDict):
    insertText: Union[str, StringValue]
    filterText: NotRequired[str]
    range: NotRequired[Range]
    command: NotRequired[Command]


class WorkspaceSymbolClientCapabilities(TypedDict):
    class SymbolKind_0(TypedDict):
        valueSet: NotRequired[List[SymbolKind]]
    class TagSupport_0(TypedDict):
        valueSet: List[SymbolTag]
    class ResolveSupport_0(TypedDict):
        properties: List[str]
    dynamicRegistration: NotRequired[bool]
    symbolKind: NotRequired[SymbolKind_0]
    tagSupport: NotRequired[TagSupport_0]
    resolveSupport: NotRequired[ResolveSupport_0]


class WorkspaceSymbolOptions(WorkDoneProgressOptions, TypedDict):
    resolveProvider: NotRequired[bool]


class WorkspaceSymbolRegistrationOptions(WorkspaceSymbolOptions, TypedDict):
    pass


class WorkspaceSymbolParams(WorkDoneProgressParams, PartialResultParams, TypedDict):
    query: str


class WorkspaceSymbol(TypedDict):
    class Location_1(TypedDict):
        uri: DocumentUri
    name: str
    kind: SymbolKind
    tags: NotRequired[List[SymbolTag]]
    containerName: NotRequired[str]
    location: Union[Location, Location_1]
    data: NotRequired[LSPAny]


class ConfigurationParams(TypedDict):
    items: List['ConfigurationItem']


class ConfigurationItem(TypedDict):
    scopeUri: NotRequired[URI]
    section: NotRequired[str]


class DidChangeConfigurationClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class DidChangeConfigurationParams(TypedDict):
    settings: LSPAny


class WorkspaceFoldersServerCapabilities(TypedDict):
    supported: NotRequired[bool]
    changeNotifications: NotRequired[Union[str, bool]]


class WorkspaceFolder(TypedDict):
    uri: URI
    name: str


class DidChangeWorkspaceFoldersParams(TypedDict):
    event: 'WorkspaceFoldersChangeEvent'


class WorkspaceFoldersChangeEvent(TypedDict):
    added: List[WorkspaceFolder]
    removed: List[WorkspaceFolder]


class FileOperationRegistrationOptions(TypedDict):
    filters: List['FileOperationFilter']

class FileOperationPatternKind(Enum):
    file = 'file'
    folder = 'folder'

FileOperationPatternKind = Literal['file', 'folder']


class FileOperationPatternOptions(TypedDict):
    ignoreCase: NotRequired[bool]


class FileOperationPattern(TypedDict):
    glob: str
    matches: NotRequired[FileOperationPatternKind]
    options: NotRequired[FileOperationPatternOptions]


class FileOperationFilter(TypedDict):
    scheme: NotRequired[str]
    pattern: FileOperationPattern


class CreateFilesParams(TypedDict):
    files: List['FileCreate']


class FileCreate(TypedDict):
    uri: str


class RenameFilesParams(TypedDict):
    files: List['FileRename']


class FileRename(TypedDict):
    oldUri: str
    newUri: str


class DeleteFilesParams(TypedDict):
    files: List['FileDelete']


class FileDelete(TypedDict):
    uri: str


class DidChangeWatchedFilesClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]
    relativePatternSupport: NotRequired[bool]


class DidChangeWatchedFilesRegistrationOptions(TypedDict):
    watchers: List['FileSystemWatcher']

Pattern = str


class RelativePattern(TypedDict):
    baseUri: Union[WorkspaceFolder, URI]
    pattern: Pattern

GlobPattern = Union[Pattern, RelativePattern]


class FileSystemWatcher(TypedDict):
    globPattern: GlobPattern
    kind: NotRequired['WatchKind']

class WatchKind(IntEnum):
    Create = 1
    Change = 2
    Delete = 4

WatchKind = int


class DidChangeWatchedFilesParams(TypedDict):
    changes: List['FileEvent']


class FileEvent(TypedDict):
    uri: DocumentUri
    type: 'FileChangeType'

class FileChangeType(IntEnum):
    Created = 1
    Changed = 2
    Deleted = 3

FileChangeType = Literal[1, 2, 3]


class ExecuteCommandClientCapabilities(TypedDict):
    dynamicRegistration: NotRequired[bool]


class ExecuteCommandOptions(WorkDoneProgressOptions, TypedDict):
    commands: List[str]


class ExecuteCommandRegistrationOptions(ExecuteCommandOptions, TypedDict):
    pass


class ExecuteCommandParams(WorkDoneProgressParams, TypedDict):
    command: str
    arguments: NotRequired[List[LSPAny]]


class ApplyWorkspaceEditParams(TypedDict):
    label: NotRequired[str]
    edit: WorkspaceEdit
    metadata: NotRequired['WorkspaceEditMetadata']


class WorkspaceEditMetadata(TypedDict):
    isRefactoring: NotRequired[bool]


class ApplyWorkspaceEditResult(TypedDict):
    applied: bool
    failureReason: NotRequired[str]
    failedChange: NotRequired[int]


class ShowMessageParams(TypedDict):
    type: 'MessageType'
    message: str

class MessageType(IntEnum):
    Error = 1
    Warning = 2
    Info = 3
    Log = 4
    Debug = 5

MessageType = Literal[1, 2, 3, 4, 5]


class ShowMessageRequestClientCapabilities(TypedDict):
    class MessageActionItem_0(TypedDict):
        additionalPropertiesSupport: NotRequired[bool]
    messageActionItem: NotRequired[MessageActionItem_0]


class ShowMessageRequestParams(TypedDict):
    type: MessageType
    message: str
    actions: NotRequired[List['MessageActionItem']]


class MessageActionItem(TypedDict):
    title: str


class ShowDocumentClientCapabilities(TypedDict):
    support: bool


class ShowDocumentParams(TypedDict):
    uri: URI
    external: NotRequired[bool]
    takeFocus: NotRequired[bool]
    selection: NotRequired[Range]


class ShowDocumentResult(TypedDict):
    success: bool


class LogMessageParams(TypedDict):
    type: MessageType
    message: str


class WorkDoneProgressCreateParams(TypedDict):
    token: ProgressToken


class WorkDoneProgressCancelParams(TypedDict):
    token: ProgressToken



##### END OF LSP SPECS


#######################################################################
#
# Language-Server-Protocol methods
#
#######################################################################

class LSPTasks:
    def __init__(self, lsp_data: dict):
        self.lsp_data = lsp_data
        self.lsp_table = gen_lsp_table([], prefix='lsp_')

NO_TASKS = LSPTasks({})

class LSPBase:
    def __init__(self, cpu_bound: LSPTasks=NO_TASKS, blocking: LSPTasks=NO_TASKS):
        self.lsp_data = {
            'processId': 0,
            'rootUri': '',
            'clientCapabilities': {},
            'serverInfo': {"name": self.__class__.__name__, "version": "0.1"},
            'serverCapabilities': {
            }
        }
        self.connection = None
        self.cpu_bound = cpu_bound
        self.blocking = blocking
        self.lsp_table = gen_lsp_table(self, prefix='lsp_')
        self.lsp_fulltable = self.lsp_table.copy()
        assert self.lsp_fulltable.keys().isdisjoint(self.cpu_bound.lsp_table.keys())
        self.lsp_fulltable.update(self.cpu_bound.lsp_table)
        assert self.lsp_fulltable.keys().isdisjoint(self.blocking.lsp_table.keys())
        self.lsp_fulltable.update(self.blocking.lsp_table)

    def connect(self, connection):
        self.connection = connection

    def lsp_initialize(self, **kwargs) -> Dict:
        # InitializeParams -> InitializeResult
        self.lsp_data['processId'] = kwargs['processId']
        self.lsp_data['rootUri'] = kwargs['rootUri']
        self.lsp_data['clientCapabilities'] = kwargs['capabilities']
        return {'capabilities': self.lsp_data['serverCapabilities'],
                'serverInfo': self.lsp_data['serverInfo']}

    def lsp_initialized(self, params: InitializedParams) -> None:
        pass

    def lsp_shutdown(self) -> Dict:
        self.lsp_data['processId'] = 0
        self.lsp_data['rootUri'] = ''
        self.lsp_data['clientCapabilities'] = dict()
        return {}


if __name__ == "__main__":
    print("A small self-test of DHParser.lsp")
    print(DocumentSymbol.__required_keys__)
