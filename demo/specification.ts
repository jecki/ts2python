

/**
 * Defines an integer number in the range of -2^31 to 2^31 - 1.
 */
export type integer = number;

/**
 * Defines an unsigned integer number in the range of 0 to 2^31 - 1.
 */
export type uinteger = number;

/**
 * Defines a decimal number. Since decimal numbers are very
 * rare in the language server specification, we denote the
 * exact range with every decimal using the mathematics
 * interval notation (e.g., [0, 1] denotes all decimals d with
 * 0 <= d <= 1.)
 */
export type decimal = number;

/**
 * The LSP any type.
 *
 * @since 3.17.0
 */
export type LSPAny = LSPObject | LSPArray | string | integer | uinteger |
	decimal | boolean | null;

/**
 * LSP object definition.
 *
 * @since 3.17.0
 */
export type LSPObject = { [key: string]: LSPAny };

/**
 * LSP arrays.
 *
 * @since 3.17.0
 */
export type LSPArray = LSPAny[];

interface Message {
	jsonrpc: string;
}

interface RequestMessage extends Message {

	/**
	 * The request id.
	 */
	id: integer | string;

	/**
	 * The method to be invoked.
	 */
	method: string;

	/**
	 * The method's params.
	 */
	params?: array | object;
}

interface ResponseMessage extends Message {
	/**
	 * The request id.
	 */
	id: integer | string | null;

	/**
	 * The result of a request. This member is REQUIRED on success.
	 * This member MUST NOT exist if there was an error invoking the method.
	 */
	result?: LSPAny;

	/**
	 * The error object in case a request fails.
	 */
	error?: ResponseError;
}

interface ResponseError {
	/**
	 * A number indicating the error type that occurred.
	 */
	code: integer;

	/**
	 * A string providing a short description of the error.
	 */
	message: string;

	/**
	 * A primitive or structured value that contains additional
	 * information about the error. Can be omitted.
	 */
	data?: LSPAny;
}

export namespace ErrorCodes {
	// Defined by JSON-RPC
	export const ParseError: integer = -32700;
	export const InvalidRequest: integer = -32600;
	export const MethodNotFound: integer = -32601;
	export const InvalidParams: integer = -32602;
	export const InternalError: integer = -32603;

	/**
	 * This is the start range of JSON-RPC reserved error codes.
	 * It doesn't denote a real error code. No LSP error codes should
	 * be defined between the start and end range. For backwards
	 * compatibility the `ServerNotInitialized` and the `UnknownErrorCode`
	 * are left in the range.
	 *
	 * @since 3.16.0
	 */
	export const jsonrpcReservedErrorRangeStart: integer = -32099;
	/** @deprecated use jsonrpcReservedErrorRangeStart */
	export const serverErrorStart: integer = jsonrpcReservedErrorRangeStart;

	/**
	 * Error code indicating that a server received a notification or
	 * request before the server received the `initialize` request.
	 */
	export const ServerNotInitialized: integer = -32002;
	export const UnknownErrorCode: integer = -32001;

	/**
	 * This is the end range of JSON-RPC reserved error codes.
	 * It doesn't denote a real error code.
	 *
	 * @since 3.16.0
	 */
	export const jsonrpcReservedErrorRangeEnd = -32000;
	/** @deprecated use jsonrpcReservedErrorRangeEnd */
	export const serverErrorEnd: integer = jsonrpcReservedErrorRangeEnd;

	/**
	 * This is the start range of LSP reserved error codes.
	 * It doesn't denote a real error code.
	 *
	 * @since 3.16.0
	 */
	export const lspReservedErrorRangeStart: integer = -32899;

	/**
	 * A request failed but it was syntactically correct, e.g the
	 * method name was known and the parameters were valid. The error
	 * message should contain human readable information about why
	 * the request failed.
	 *
	 * @since 3.17.0
	 */
	export const RequestFailed: integer = -32803;

	/**
	 * The server cancelled the request. This error code should
	 * only be used for requests that explicitly support being
	 * server cancellable.
	 *
	 * @since 3.17.0
	 */
	export const ServerCancelled: integer = -32802;

	/**
	 * The server detected that the content of a document got
	 * modified outside normal conditions. A server should
	 * NOT send this error code if it detects a content change
	 * in its unprocessed messages. The result even computed
	 * on an older state might still be useful for the client.
	 *
	 * If a client decides that a result is not of any use anymore
	 * the client should cancel the request.
	 */
	export const ContentModified: integer = -32801;

	/**
	 * The client has canceled a request and a server has detected
	 * the cancel.
	 */
	export const RequestCancelled: integer = -32800;

	/**
	 * This is the end range of LSP reserved error codes.
	 * It doesn't denote a real error code.
	 *
	 * @since 3.16.0
	 */
	export const lspReservedErrorRangeEnd: integer = -32800;
}

interface NotificationMessage extends Message {
	/**
	 * The method to be invoked.
	 */
	method: string;

	/**
	 * The notification's params.
	 */
	params?: array | object;
}

interface CancelParams {
	/**
	 * The request id to cancel.
	 */
	id: integer | string;
}

type ProgressToken = integer | string;

interface ProgressParams<T> {
	/**
	 * The progress token provided by the client or server.
	 */
	token: ProgressToken;

	/**
	 * The progress data.
	 */
	value: T;
}

interface HoverParams {
	textDocument: string; /** The text document's URI in string form */
	position: { line: uinteger; character: uinteger; };
}

interface HoverResult {
	value: string;
}


/* source file: "types/uri.md" */





type DocumentUri = string;

type URI = string;


/* source file: "types/regexp.md" */

/**
 * Client capabilities specific to regular expressions.
 */
export interface RegularExpressionsClientCapabilities {
	/**
	 * The engine's name.
	 */
	engine: string;

	/**
	 * The engine's version.
	 */
	version?: string;
}


/* source file: "types/enumerations.md" */


/* source file: "types/textDocuments.md" */

export const EOL: string[] = ['\n', '\r\n', '\r'];


/* source file: "types/position.md" */

interface Position {
	/**
	 * Line position in a document (zero-based).
	 */
	line: uinteger;

	/**
	 * Character offset on a line in a document (zero-based). The meaning of this
	 * offset is determined by the negotiated `PositionEncodingKind`.
	 *
	 * If the character value is greater than the line length it defaults back
	 * to the line length.
	 */
	character: uinteger;
}

/**
 * A type indicating how positions are encoded,
 * specifically what column offsets mean.
 *
 * @since 3.17.0
 */
export type PositionEncodingKind = string;

/**
 * A set of predefined position encoding kinds.
 *
 * @since 3.17.0
 */
export namespace PositionEncodingKind {

	/**
	 * Character offsets count UTF-8 code units (i.e. bytes).
	 */
	export const UTF8: PositionEncodingKind = 'utf-8';

	/**
	 * Character offsets count UTF-16 code units.
	 *
	 * This is the default and must always be supported
	 * by servers.
	 */
	export const UTF16: PositionEncodingKind = 'utf-16';

	/**
	 * Character offsets count UTF-32 code units.
	 *
	 * Implementation note: these are the same as Unicode code points,
	 * so this `PositionEncodingKind` may also be used for an
	 * encoding-agnostic representation of character offsets.
	 */
	export const UTF32: PositionEncodingKind = 'utf-32';
}


/* source file: "types/range.md" */


interface Range {
	/**
	 * The range's start position.
	 */
	start: Position;

	/**
	 * The range's end position.
	 */
	end: Position;
}


/* source file: "types/textDocumentItem.md" */

interface TextDocumentItem {
	/**
	 * The text document's URI.
	 */
	uri: DocumentUri;

	/**
	 * The text document's language identifier.
	 */
	languageId: string;

	/**
	 * The version number of this document (it will increase after each
	 * change, including undo/redo).
	 */
	version: integer;

	/**
	 * The content of the opened text document.
	 */
	text: string;
}


/* source file: "types/textDocumentIdentifier.md" */

interface TextDocumentIdentifier {
	/**
	 * The text document's URI.
	 */
	uri: DocumentUri;
}


/* source file: "types/versionedTextDocumentIdentifier.md" */

interface VersionedTextDocumentIdentifier extends TextDocumentIdentifier {
	/**
	 * The version number of this document.
	 *
	 * The version number of a document will increase after each change,
	 * including undo/redo. The number doesn't need to be consecutive.
	 */
	version: integer;
}

interface OptionalVersionedTextDocumentIdentifier extends TextDocumentIdentifier {
	/**
	 * The version number of this document. If an optional versioned text document
	 * identifier is sent from the server to the client and the file is not
	 * open in the editor (the server has not received an open notification
	 * before) the server can send `null` to indicate that the version is
	 * known and the content on disk is the master (as specified with document
	 * content ownership).
	 *
	 * The version number of a document will increase after each change,
	 * including undo/redo. The number doesn't need to be consecutive.
	 */
	version: integer | null;
}


/* source file: "types/textDocumentPositionParams.md" */

interface TextDocumentPositionParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The position inside the text document.
	 */
	position: Position;
}


/* source file: "types/patterns.md" */

/**
 * The pattern to watch relative to the base path. Glob patterns can have
 * the following syntax:
 * - `*` to match zero or more characters in a path segment
 * - `?` to match on one character in a path segment
 * - `**` to match any number of path segments, including none
 * - `{}` to group conditions (e.g. `**​/*.{ts,js}` matches all TypeScript
 *   and JavaScript files)
 * - `[]` to declare a range of characters to match in a path segment
 *   (e.g., `example.[0-9]` to match on `example.0`, `example.1`, …)
 * - `[!...]` to negate a range of characters to match in a path segment
 *   (e.g., `example.[!0-9]` to match on `example.a`, `example.b`,
 *   but not `example.0`)
 *
 * @since 3.17.0
 */
export type Pattern = string;

/**
 * A relative pattern is a helper to construct glob patterns that are matched
 * relatively to a base URI. The common value for a `baseUri` is a workspace
 * folder root, but it can be another absolute URI as well.
 *
 * @since 3.17.0
 */
export interface RelativePattern {
	/**
	 * A workspace folder or a base URI to which this pattern will be matched
	 * against relatively.
	 */
	baseUri: WorkspaceFolder | URI;

	/**
	 * The actual pattern;
	 */
	pattern: Pattern;
}

/**
 * The glob pattern. Either a string pattern or a relative pattern.
 *
 * @since 3.17.0
 */
export type GlobPattern = Pattern | RelativePattern;


/* source file: "types/documentFilter.md" */


export interface DocumentFilter {
	/**
	 * A language id, like `typescript`.
	 */
	language?: string;

	/**
	 * A Uri scheme, like `file` or `untitled`.
	 */
	scheme?: string;

	/**
	 * A pattern, like `*.{ts,js}` or a pattern relative to a workspace folders.
	 *
	 * See GlobPattern.
	 *
	 * Whether clients support relative patterns depends on the client
	 * capability `textDocuments.filters.relativePatternSupport`.
	 */
	pattern?: GlobPattern;
}

export type DocumentSelector = DocumentFilter[];


/* source file: "types/stringValue.md" */

/**
 * A string value used as a snippet is a template which allows to insert text
 * and to control the editor cursor when insertion happens.
 *
 * A snippet can define tab stops and placeholders with `$1`, `$2`
 * and `${3:foo}`. `$0` defines the final tab stop, it defaults to
 * the end of the snippet. Variables are defined with `$name` and
 * `${name:default value}`.
 * 
 * @since 3.18.0
 */
export interface StringValue {
	/**
	 * The kind of string value.
	 */
	kind: 'snippet';

	/**
	 * The snippet string.
	 */
	value: string;
}


/* source file: "types/textEdit.md" */

interface TextEdit {
	/**
	 * The range of the text document to be manipulated. To insert
	 * text into a document, create a range where start === end.
	 */
	range: Range;

	/**
	 * The string to be inserted. For delete operations, use an
	 * empty string.
	 */
	newText: string;
}

/**
 * Additional information that describes document changes.
 *
 * @since 3.16.0
 */
export interface ChangeAnnotation {
	/**
	 * A human-readable string describing the actual change. The string
	 * is rendered prominently in the user interface.
	 */
	label: string;

	/**
	 * A flag which indicates that user confirmation is needed
	 * before applying the change.
	 */
	needsConfirmation?: boolean;

	/**
	 * A human-readable string which is rendered less prominently in
	 * the user interface.
	 */
	description?: string;
}

/**
 * An identifier referring to a change annotation managed by a workspace
 * edit.
 *
 * @since 3.16.0.
 */
export type ChangeAnnotationIdentifier = string;

/**
 * A special text edit with an additional change annotation.
 *
 * @since 3.16.0.
 */
export interface AnnotatedTextEdit extends TextEdit {
	/**
	 * The actual annotation identifier.
	 */
	annotationId: ChangeAnnotationIdentifier;
}

/**
 * An interactive text edit.
 *
 * @since 3.18.0
 */
export interface SnippetTextEdit {
	/**
	 * The range of the text document to be manipulated.
	 */
	range: Range;

	/**
	 * The snippet to be inserted.
	 */
	snippet: StringValue;

	/**
	 * The actual identifier of the snippet edit.
	 */
	annotationId?: ChangeAnnotationIdentifier;
}


/* source file: "types/textEditArray.md" */


/* source file: "types/textDocumentEdit.md" */

export interface TextDocumentEdit {
	/**
	 * The text document to change.
	 */
	textDocument: OptionalVersionedTextDocumentIdentifier;

	/**
	 * The edits to be applied.
	 *
	 * @since 3.16.0 - support for AnnotatedTextEdit. This is guarded by the
	 * client capability `workspace.workspaceEdit.changeAnnotationSupport`
	 * 
	 * @since 3.18.0 - support for SnippetTextEdit. This is guarded by the
	 * client capability `workspace.workspaceEdit.snippetEditSupport`
	 */
	edits: (TextEdit | AnnotatedTextEdit | SnippetTextEdit)[];
}


/* source file: "types/location.md" */

interface Location {
	uri: DocumentUri;
	range: Range;
}


/* source file: "types/locationLink.md" */

interface LocationLink {

	/**
	 * Span of the origin of this link.
	 *
	 * Used as the underlined span for mouse interaction. Defaults to the word
	 * range at the mouse position.
	 */
	originSelectionRange?: Range;

	/**
	 * The target resource identifier of this link.
	 */
	targetUri: DocumentUri;

	/**
	 * The full target range of this link. If the target is, for example, a
	 * symbol, then the target range is the range enclosing this symbol not
	 * including leading/trailing whitespace but everything else like comments.
	 * This information is typically used to highlight the range in the editor.
	 */
	targetRange: Range;

	/**
	 * The range that should be selected and revealed when this link is being
	 * followed, e.g., the name of a function. Must be contained by the
	 * `targetRange`. See also `DocumentSymbol#range`
	 */
	targetSelectionRange: Range;
}


/* source file: "types/diagnostic.md" */

export interface Diagnostic {
	/**
	 * The range at which the message applies.
	 */
	range: Range;

	/**
	 * The diagnostic's severity. To avoid interpretation mismatches when a
	 * server is used with different clients it is highly recommended that
	 * servers always provide a severity value. If omitted, it’s recommended
	 * for the client to interpret it as an Error severity.
	 */
	severity?: DiagnosticSeverity;

	/**
	 * The diagnostic's code, which might appear in the user interface.
	 */
	code?: integer | string;

	/**
	 * An optional property to describe the error code.
	 *
	 * @since 3.16.0
	 */
	codeDescription?: CodeDescription;

	/**
	 * A human-readable string describing the source of this
	 * diagnostic, e.g. 'typescript' or 'super lint'.
	 */
	source?: string;

	/**
	 * The diagnostic's message.
	 *
	 * @since 3.18.0 - support for MarkupContent. This is guarded by the client
	 * capability `textDocument.diagnostic.markupMessageSupport`.
	 */
	message: string | MarkupContent;

	/**
	 * Additional metadata about the diagnostic.
	 *
	 * @since 3.15.0
	 */
	tags?: DiagnosticTag[];

	/**
	 * An array of related diagnostic information, e.g. when symbol-names within
	 * a scope collide all definitions can be marked via this property.
	 */
	relatedInformation?: DiagnosticRelatedInformation[];

	/**
	 * A data entry field that is preserved between a
	 * `textDocument/publishDiagnostics` notification and
	 * `textDocument/codeAction` request.
	 *
	 * @since 3.16.0
	 */
	data?: LSPAny;
}

export namespace DiagnosticSeverity {
	/**
	 * Reports an error.
	 */
	export const Error: 1 = 1;
	/**
	 * Reports a warning.
	 */
	export const Warning: 2 = 2;
	/**
	 * Reports information.
	 */
	export const Information: 3 = 3;
	/**
	 * Reports a hint.
	 */
	export const Hint: 4 = 4;
}

export type DiagnosticSeverity = 1 | 2 | 3 | 4;

/**
 * The diagnostic tags.
 *
 * @since 3.15.0
 */
export namespace DiagnosticTag {
	/**
	 * Unused or unnecessary code.
	 *
	 * Clients are allowed to render diagnostics with this tag faded out
	 * instead of having an error squiggle.
	 */
	export const Unnecessary: 1 = 1;
	/**
	 * Deprecated or obsolete code.
	 *
	 * Clients are allowed to render diagnostics with this tag strike through.
	 */
	export const Deprecated: 2 = 2;
}

export type DiagnosticTag = 1 | 2;

/**
 * Represents a related message and source code location for a diagnostic.
 * This should be used to point to code locations that cause or are related to
 * a diagnostic, e.g. when duplicating a symbol in a scope.
 */
export interface DiagnosticRelatedInformation {
	/**
	 * The location of this related diagnostic information.
	 */
	location: Location;

	/**
	 * The message of this related diagnostic information.
	 */
	message: string;
}

/**
 * Structure to capture a description for an error code.
 *
 * @since 3.16.0
 */
export interface CodeDescription {
	/**
	 * A URI to open with more information about the diagnostic error.
	 */
	href: URI;
}


/* source file: "types/command.md" */

interface Command {
	/**
	 * Title of the command, like `save`.
	 */
	title: string;

	/**
	 * An optional tooltip.
	 */
	tooltip?: string;

	/**
	 * The identifier of the actual command handler.
	 */
	command: string;

	/**
	 * Arguments that the command handler should be
	 * invoked with.
	 */
	arguments?: LSPAny[];
}


/* source file: "types/markupContent.md" */

/**
 * Describes the content type that a client supports in various
 * result literals like `Hover`, `ParameterInfo` or `CompletionItem`.
 *
 * Please note that `MarkupKinds` must not start with a `$`. These kinds
 * are reserved for internal usage.
 */
export namespace MarkupKind {
	/**
	 * Plain text is supported as a content format.
	 */
	export const PlainText: 'plaintext' = 'plaintext';

	/**
	 * Markdown is supported as a content format.
	 */
	export const Markdown: 'markdown' = 'markdown';
}
export type MarkupKind = 'plaintext' | 'markdown';

/**
 * A `MarkupContent` literal represents a string value whose content is
 * interpreted based on its kind flag. Currently, the protocol supports
 * `plaintext` and `markdown` as markup kinds.
 *
 * If the kind is `markdown` then the value can contain fenced code blocks like
 * in GitHub issues.
 *
 * Here is an example how such a string can be constructed using
 * JavaScript / TypeScript:
 * ```typescript
 * let markdown: MarkdownContent = {
 * 	kind: MarkupKind.Markdown,
 * 	value: [
 * 		'# Header',
 * 		'Some text',
 * 		'```typescript',
 * 		'someCode();',
 * 		'```'
 * 	].join('\n')
 * };
 * ```
 *
 * *Please Note* that clients might sanitize the returned markdown. A client
 * could decide to remove HTML from the markdown to avoid script execution.
 */
export interface MarkupContent {
	/**
	 * The type of the Markup.
	 */
	kind: MarkupKind;

	/**
	 * The content itself.
	 */
	value: string;
}

/**
 * Client capabilities specific to the used markdown parser.
 *
 * @since 3.16.0
 */
export interface MarkdownClientCapabilities {
	/**
	 * The name of the parser.
	 */
	parser: string;

	/**
	 * The version of the parser.
	 */
	version?: string;

	/**
	 * A list of HTML tags that the client allows / supports in
	 * Markdown.
	 *
	 * @since 3.17.0
	 */
	allowedTags?: string[];
}


/* source file: "types/resourceChanges.md" */

/**
 * Options to create a file.
 */
export interface CreateFileOptions {
	/**
	 * Overwrite existing file. Overwrite wins over `ignoreIfExists`.
	 */
	overwrite?: boolean;

	/**
	 * Ignore if exists.
	 */
	ignoreIfExists?: boolean;
}

/**
 * Create file operation
 */
export interface CreateFile {
	/**
	 * This is a create operation.
	 */
	kind: 'create';

	/**
	 * The resource to create.
	 */
	uri: DocumentUri;

	/**
	 * Additional options.
	 */
	options?: CreateFileOptions;

	/**
	 * An optional annotation identifier describing the operation.
	 *
	 * @since 3.16.0
	 */
	annotationId?: ChangeAnnotationIdentifier;
}

/**
 * Rename file options
 */
export interface RenameFileOptions {
	/**
	 * Overwrite target if existing. Overwrite wins over `ignoreIfExists`.
	 */
	overwrite?: boolean;

	/**
	 * Ignores if target exists.
	 */
	ignoreIfExists?: boolean;
}

/**
 * Rename file operation
 */
export interface RenameFile {
	/**
	 * This is a rename operation.
	 */
	kind: 'rename';

	/**
	 * The old (existing) location.
	 */
	oldUri: DocumentUri;

	/**
	 * The new location.
	 */
	newUri: DocumentUri;

	/**
	 * Rename options.
	 */
	options?: RenameFileOptions;

	/**
	 * An optional annotation identifier describing the operation.
	 *
	 * @since 3.16.0
	 */
	annotationId?: ChangeAnnotationIdentifier;
}

/**
 * Delete file options
 */
export interface DeleteFileOptions {
	/**
	 * Delete the content recursively if a folder is denoted.
	 */
	recursive?: boolean;

	/**
	 * Ignore the operation if the file doesn't exist.
	 */
	ignoreIfNotExists?: boolean;
}

/**
 * Delete file operation
 */
export interface DeleteFile {
	/**
	 * This is a delete operation.
	 */
	kind: 'delete';

	/**
	 * The file to delete.
	 */
	uri: DocumentUri;

	/**
	 * Delete options.
	 */
	options?: DeleteFileOptions;

	/**
	 * An optional annotation identifier describing the operation.
	 *
	 * @since 3.16.0
	 */
	annotationId?: ChangeAnnotationIdentifier;
}


/* source file: "types/workspaceEdit.md" */

export interface WorkspaceEdit {
	/**
	 * Holds changes to existing resources.
	 */
	changes?: { [uri: DocumentUri]: TextEdit[]; };

	/**
	 * Depending on the client capability
	 * `workspace.workspaceEdit.resourceOperations` document changes are either
	 * an array of `TextDocumentEdit`s to express changes to n different text
	 * documents where each text document edit addresses a specific version of
	 * a text document. Or it can contain above `TextDocumentEdit`s mixed with
	 * create, rename and delete file / folder operations.
	 *
	 * Whether a client supports versioned document edits is expressed via
	 * `workspace.workspaceEdit.documentChanges` client capability.
	 *
	 * If a client neither supports `documentChanges` nor
	 * `workspace.workspaceEdit.resourceOperations` then only plain `TextEdit`s
	 * using the `changes` property are supported.
	 */
	documentChanges?: (
		TextDocumentEdit[] |
		(TextDocumentEdit | CreateFile | RenameFile | DeleteFile)[]
	);

	/**
	 * A map of change annotations that can be referenced in
	 * `AnnotatedTextEdit`s or create, rename and delete file / folder
	 * operations.
	 *
	 * Whether clients honor this property depends on the client capability
	 * `workspace.changeAnnotationSupport`.
	 *
	 * @since 3.16.0
	 */
	changeAnnotations?: {
		[id: string /* ChangeAnnotationIdentifier */]: ChangeAnnotation;
	};
}

export interface WorkspaceEditClientCapabilities {
	/**
	 * The client supports versioned document changes in `WorkspaceEdit`s.
	 */
	documentChanges?: boolean;

	/**
	 * The resource operations the client supports. Clients should at least
	 * support 'create', 'rename', and 'delete' for files and folders.
	 *
	 * @since 3.13.0
	 */
	resourceOperations?: ResourceOperationKind[];

	/**
	 * The failure handling strategy of a client if applying the workspace edit
	 * fails.
	 *
	 * @since 3.13.0
	 */
	failureHandling?: FailureHandlingKind;

	/**
	 * Whether the client normalizes line endings to the client specific
	 * setting.
	 * If set to `true`, the client will normalize line ending characters
	 * in a workspace edit to the client specific new line character(s).
	 *
	 * @since 3.16.0
	 */
	normalizesLineEndings?: boolean;

	/**
	 * Whether the client in general supports change annotations on text edits,
	 * create file, rename file, and delete file changes.
	 *
	 * @since 3.16.0
	 */
	changeAnnotationSupport?: {
		/**
		 * Whether the client groups edits with equal labels into tree nodes,
		 * for instance all edits labelled with "Changes in Strings" would
		 * be a tree node.
		 */
		groupsOnLabel?: boolean;
	};

	/**
	 * Whether the client supports `WorkspaceEditMetadata` in `WorkspaceEdit`s.
	 *
	 * @since 3.18.0
	 * @proposed
	 */
	metadataSupport?: boolean;

	/**
	 * Whether the client supports snippets as text edits.
	 *
	 * @since 3.18.0
	 * @proposed
	 */
	snippetEditSupport?: boolean;
}

/**
 * The kind of resource operations supported by the client.
 */
export type ResourceOperationKind = 'create' | 'rename' | 'delete';

export namespace ResourceOperationKind {

	/**
	 * Supports creating new files and folders.
	 */
	export const Create: ResourceOperationKind = 'create';

	/**
	 * Supports renaming existing files and folders.
	 */
	export const Rename: ResourceOperationKind = 'rename';

	/**
	 * Supports deleting existing files and folders.
	 */
	export const Delete: ResourceOperationKind = 'delete';
}

export type FailureHandlingKind = 'abort' | 'transactional' | 'undo'
	| 'textOnlyTransactional';

export namespace FailureHandlingKind {

	/**
	 * Applying the workspace change is simply aborted if one of the changes
	 * provided fails. All operations executed before the failing operation
	 * stay executed.
	 */
	export const Abort: FailureHandlingKind = 'abort';

	/**
	 * All operations are executed transactionally. That means they either all
	 * succeed or no changes at all are applied to the workspace.
	 */
	export const Transactional: FailureHandlingKind = 'transactional';


	/**
	 * If the workspace edit contains only textual file changes they are
	 * executed transactionally. If resource changes (create, rename or delete
	 * file) are part of the change the failure handling strategy is abort.
	 */
	export const TextOnlyTransactional: FailureHandlingKind
		= 'textOnlyTransactional';

	/**
	 * The client tries to undo the operations already executed. But there is no
	 * guarantee that this is succeeding.
	 */
	export const Undo: FailureHandlingKind = 'undo';
}


/* source file: "types/workDoneProgress.md" */

export interface WorkDoneProgressBegin {

	kind: 'begin';

	/**
	 * Mandatory title of the progress operation. Used to briefly inform about
	 * the kind of operation being performed.
	 *
	 * Examples: "Indexing" or "Linking dependencies".
	 */
	title: string;

	/**
	 * Controls if a cancel button should be shown to allow the user to cancel
	 * the long running operation. Clients that don't support cancellation are
	 * allowed to ignore the setting.
	 */
	cancellable?: boolean;

	/**
	 * Optional, more detailed associated progress message. Contains
	 * complementary information to the `title`.
	 *
	 * Examples: "3/25 files", "project/src/module2", "node_modules/some_dep".
	 * If unset, the previous progress message (if any) is still valid.
	 */
	message?: string;

	/**
	 * Optional progress percentage to display (value 100 is considered 100%).
	 * If not provided infinite progress is assumed and clients are allowed
	 * to ignore the `percentage` value in subsequent report notifications.
	 *
	 * The value should be steadily rising. Clients are free to ignore values
	 * that are not following this rule. The value range is [0, 100].
	 */
	percentage?: uinteger;
}

export interface WorkDoneProgressReport {

	kind: 'report';

	/**
	 * Controls enablement state of a cancel button. This property is only valid
	 * if a cancel button got requested in the `WorkDoneProgressBegin` payload.
	 *
	 * Clients that don't support cancellation or don't support controlling the
	 * button's enablement state are allowed to ignore the setting.
	 */
	cancellable?: boolean;

	/**
	 * Optional, more detailed associated progress message. Contains
	 * complementary information to the `title`.
	 *
	 * Examples: "3/25 files", "project/src/module2", "node_modules/some_dep".
	 * If unset, the previous progress message (if any) is still valid.
	 */
	message?: string;

	/**
	 * Optional progress percentage to display (value 100 is considered 100%).
	 * If not provided infinite progress is assumed and clients are allowed
	 * to ignore the `percentage` value in subsequent report notifications.
	 *
	 * The value should be steadily rising. Clients are free to ignore values
	 * that are not following this rule. The value range is [0, 100].
	 */
	percentage?: uinteger;
}

export interface WorkDoneProgressEnd {

	kind: 'end';

	/**
	 * Optional, a final message indicating, for example,
     * the outcome of the operation.
	 */
	message?: string;
}


export interface WorkDoneProgressParams {
	/**
	 * An optional token that a server can use to report work done progress.
	 */
	workDoneToken?: ProgressToken;
}



export interface WorkDoneProgressOptions {
	workDoneProgress?: boolean;
}

	/**
	 * Window specific client capabilities.
	 */
	window?: {
		/**
		 * Whether client supports server initiated progress using the
		 * `window/workDoneProgress/create` request.
		 */
		workDoneProgress?: boolean;
	};


/* source file: "types/partialResults.md" */



/* source file: "types/partialResultParams.md" */

export interface PartialResultParams {
	/**
	 * An optional token that a server can use to report partial results (e.g.
	 * streaming) to the client.
	 */
	partialResultToken?: ProgressToken;
}


/* source file: "types/traceValue.md" */

export type TraceValue = 'off' | 'messages' | 'verbose';


/* source file: "general/initialize.md" */

interface InitializeParams extends WorkDoneProgressParams {
	/**
	 * The process Id of the parent process that started the server. Is null if
	 * the process has not been started by another process. If the parent
	 * process is not alive then the server should exit (see exit notification)
	 * its process.
	 */
	processId: integer | null;

	/**
	 * Information about the client
	 *
	 * @since 3.15.0
	 */
	clientInfo?: {
		/**
		 * The name of the client as defined by the client.
		 */
		name: string;

		/**
		 * The client's version as defined by the client.
		 */
		version?: string;
	};

	/**
	 * The locale the client is currently showing the user interface
	 * in. This must not necessarily be the locale of the operating
	 * system.
	 *
	 * Uses IETF language tags as the value's syntax
	 * (See https://en.wikipedia.org/wiki/IETF_language_tag)
	 *
	 * @since 3.16.0
	 */
	locale?: string;

	/**
	 * The rootPath of the workspace. Is null
	 * if no folder is open.
	 *
	 * @deprecated in favour of `rootUri`.
	 */
	rootPath?: string | null;

	/**
	 * The rootUri of the workspace. Is null if no
	 * folder is open. If both `rootPath` and `rootUri` are set
	 * `rootUri` wins.
	 *
	 * @deprecated in favour of `workspaceFolders`
	 */
	rootUri: DocumentUri | null;

	/**
	 * User provided initialization options.
	 */
	initializationOptions?: LSPAny;

	/**
	 * The capabilities provided by the client (editor or tool)
	 */
	capabilities: ClientCapabilities;

	/**
	 * The initial trace setting. If omitted trace is disabled ('off').
	 */
	trace?: TraceValue;

	/**
	 * The workspace folders configured in the client when the server starts.
	 * This property is only available if the client supports workspace folders.
	 * It can be `null` if the client supports workspace folders but none are
	 * configured.
	 *
	 * @since 3.6.0
	 */
	workspaceFolders?: WorkspaceFolder[] | null;
}

/**
 * Text document specific client capabilities.
 */
export interface TextDocumentClientCapabilities {

	/**
	 * Defines which synchronization capabilities the client supports.
	 */
	synchronization?: TextDocumentSyncClientCapabilities;

	/**
	 * Defines which filters the client supports.
	 *
	 * @since 3.18.0
	 */
	filters?: TextDocumentFilterClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/completion` request.
	 */
	completion?: CompletionClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/hover` request.
	 */
	hover?: HoverClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/signatureHelp` request.
	 */
	signatureHelp?: SignatureHelpClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/declaration` request.
	 *
	 * @since 3.14.0
	 */
	declaration?: DeclarationClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/definition` request.
	 */
	definition?: DefinitionClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/typeDefinition` request.
	 *
	 * @since 3.6.0
	 */
	typeDefinition?: TypeDefinitionClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/implementation` request.
	 *
	 * @since 3.6.0
	 */
	implementation?: ImplementationClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/references` request.
	 */
	references?: ReferenceClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/documentHighlight` request.
	 */
	documentHighlight?: DocumentHighlightClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/documentSymbol` request.
	 */
	documentSymbol?: DocumentSymbolClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/codeAction` request.
	 */
	codeAction?: CodeActionClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/codeLens` request.
	 */
	codeLens?: CodeLensClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/documentLink` request.
	 */
	documentLink?: DocumentLinkClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/documentColor` and the
	 * `textDocument/colorPresentation` request.
	 *
	 * @since 3.6.0
	 */
	colorProvider?: DocumentColorClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/formatting` request.
	 */
	formatting?: DocumentFormattingClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/rangeFormatting` and
	 * `textDocument/rangesFormatting requests.
	 */
	rangeFormatting?: DocumentRangeFormattingClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/onTypeFormatting` request.
	 */
	onTypeFormatting?: DocumentOnTypeFormattingClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/rename` request.
	 */
	rename?: RenameClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/publishDiagnostics`
	 * notification.
	 */
	publishDiagnostics?: PublishDiagnosticsClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/foldingRange` request.
	 *
	 * @since 3.10.0
	 */
	foldingRange?: FoldingRangeClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/selectionRange` request.
	 *
	 * @since 3.15.0
	 */
	selectionRange?: SelectionRangeClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/linkedEditingRange` request.
	 *
	 * @since 3.16.0
	 */
	linkedEditingRange?: LinkedEditingRangeClientCapabilities;

	/**
	 * Capabilities specific to the various call hierarchy requests.
	 *
	 * @since 3.16.0
	 */
	callHierarchy?: CallHierarchyClientCapabilities;

	/**
	 * Capabilities specific to the various semantic token requests.
	 *
	 * @since 3.16.0
	 */
	semanticTokens?: SemanticTokensClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/moniker` request.
	 *
	 * @since 3.16.0
	 */
	moniker?: MonikerClientCapabilities;

	/**
	 * Capabilities specific to the various type hierarchy requests.
	 *
	 * @since 3.17.0
	 */
	typeHierarchy?: TypeHierarchyClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/inlineValue` request.
	 *
	 * @since 3.17.0
	 */
	inlineValue?: InlineValueClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/inlayHint` request.
	 *
	 * @since 3.17.0
	 */
	inlayHint?: InlayHintClientCapabilities;

	/**
	 * Capabilities specific to the diagnostic pull model.
	 *
	 * @since 3.17.0
	 */
	diagnostic?: DiagnosticClientCapabilities;

	/**
	 * Capabilities specific to the `textDocument/inlineCompletion` request.
	 *
	 * @since 3.18.0
	 */
	inlineCompletion?: InlineCompletionClientCapabilities;
}

export interface TextDocumentFilterClientCapabilities {

	/**
	 * The client supports Relative Patterns.
	 *
	 * @since 3.18.0
	 */
	relativePatternSupport?: boolean;
}

/**
 * Capabilities specific to the notebook document support.
 *
 * @since 3.17.0
 */
export interface NotebookDocumentClientCapabilities {
	/**
	 * Capabilities specific to notebook document synchronization
	 *
	 * @since 3.17.0
	 */
	synchronization: NotebookDocumentSyncClientCapabilities;
}

interface ClientCapabilities {
	/**
	 * Workspace specific client capabilities.
	 */
	workspace?: {
		/**
		 * The client supports applying batch edits
		 * to the workspace by supporting the request
		 * 'workspace/applyEdit'
		 */
		applyEdit?: boolean;

		/**
		 * Capabilities specific to `WorkspaceEdit`s
		 */
		workspaceEdit?: WorkspaceEditClientCapabilities;

		/**
		 * Capabilities specific to the `workspace/didChangeConfiguration`
		 * notification.
		 */
		didChangeConfiguration?: DidChangeConfigurationClientCapabilities;

		/**
		 * Capabilities specific to the `workspace/didChangeWatchedFiles`
		 * notification.
		 */
		didChangeWatchedFiles?: DidChangeWatchedFilesClientCapabilities;

		/**
		 * Capabilities specific to the `workspace/symbol` request.
		 */
		symbol?: WorkspaceSymbolClientCapabilities;

		/**
		 * Capabilities specific to the `workspace/executeCommand` request.
		 */
		executeCommand?: ExecuteCommandClientCapabilities;

		/**
		 * The client has support for workspace folders.
		 *
		 * @since 3.6.0
		 */
		workspaceFolders?: boolean;

		/**
		 * The client supports `workspace/configuration` requests.
		 *
		 * @since 3.6.0
		 */
		configuration?: boolean;

		/**
		 * Capabilities specific to the semantic token requests scoped to the
		 * workspace.
		 *
		 * @since 3.16.0
		 */
		 semanticTokens?: SemanticTokensWorkspaceClientCapabilities;

		/**
		 * Capabilities specific to the code lens requests scoped to the
		 * workspace.
		 *
		 * @since 3.16.0
		 */
		codeLens?: CodeLensWorkspaceClientCapabilities;

		/**
		 * The client has support for file requests/notifications.
		 *
		 * @since 3.16.0
		 */
		fileOperations?: {
			/**
			 * Whether the client supports dynamic registration for file
			 * requests/notifications.
			 */
			dynamicRegistration?: boolean;

			/**
			 * The client has support for sending didCreateFiles notifications.
			 */
			didCreate?: boolean;

			/**
			 * The client has support for sending willCreateFiles requests.
			 */
			willCreate?: boolean;

			/**
			 * The client has support for sending didRenameFiles notifications.
			 */
			didRename?: boolean;

			/**
			 * The client has support for sending willRenameFiles requests.
			 */
			willRename?: boolean;

			/**
			 * The client has support for sending didDeleteFiles notifications.
			 */
			didDelete?: boolean;

			/**
			 * The client has support for sending willDeleteFiles requests.
			 */
			willDelete?: boolean;
		};

		/**
		 * Client workspace capabilities specific to inline values.
		 *
		 * @since 3.17.0
		 */
		inlineValue?: InlineValueWorkspaceClientCapabilities;

		/**
		 * Client workspace capabilities specific to inlay hints.
		 *
		 * @since 3.17.0
		 */
		inlayHint?: InlayHintWorkspaceClientCapabilities;

		/**
		 * Client workspace capabilities specific to diagnostics.
		 *
		 * @since 3.17.0.
		 */
		diagnostics?: DiagnosticWorkspaceClientCapabilities;
	};

	/**
	 * Text document specific client capabilities.
	 */
	textDocument?: TextDocumentClientCapabilities;

	/**
	 * Capabilities specific to the notebook document support.
	 *
	 * @since 3.17.0
	 */
	notebookDocument?: NotebookDocumentClientCapabilities;

	/**
	 * Window specific client capabilities.
	 */
	window?: {
		/**
		 * It indicates whether the client supports server initiated
		 * progress using the `window/workDoneProgress/create` request.
		 *
		 * The capability also controls Whether client supports handling
		 * of progress notifications. If set servers are allowed to report a
		 * `workDoneProgress` property in the request specific server
		 * capabilities.
		 *
		 * @since 3.15.0
		 */
		workDoneProgress?: boolean;

		/**
		 * Capabilities specific to the showMessage request
		 *
		 * @since 3.16.0
		 */
		showMessage?: ShowMessageRequestClientCapabilities;

		/**
		 * Client capabilities for the show document request.
		 *
		 * @since 3.16.0
		 */
		showDocument?: ShowDocumentClientCapabilities;
	};

	/**
	 * General client capabilities.
	 *
	 * @since 3.16.0
	 */
	general?: {
		/**
		 * Client capability that signals how the client
		 * handles stale requests (e.g. a request
		 * for which the client will not process the response
		 * anymore since the information is outdated).
		 *
		 * @since 3.17.0
		 */
		staleRequestSupport?: {
			/**
			 * The client will actively cancel the request.
			 */
			cancel: boolean;

			/**
			 * The list of requests for which the client
			 * will retry the request if it receives a
			 * response with error code `ContentModified``
			 */
			 retryOnContentModified: string[];
		}

		/**
		 * Client capabilities specific to regular expressions.
		 *
		 * @since 3.16.0
		 */
		regularExpressions?: RegularExpressionsClientCapabilities;

		/**
		 * Client capabilities specific to the client's markdown parser.
		 *
		 * @since 3.16.0
		 */
		markdown?: MarkdownClientCapabilities;

		/**
		 * The position encodings supported by the client. Client and server
		 * have to agree on the same position encoding to ensure that offsets
		 * (e.g. character position in a line) are interpreted the same on both
		 * side.
		 *
		 * To keep the protocol backwards compatible the following applies: if
		 * the value 'utf-16' is missing from the array of position encodings
		 * servers can assume that the client supports UTF-16. UTF-16 is
		 * therefore a mandatory encoding.
		 *
		 * If omitted it defaults to ['utf-16'].
		 *
		 * Implementation considerations: since the conversion from one encoding
		 * into another requires the content of the file / line the conversion
		 * is best done where the file is read which is usually on the server
		 * side.
		 *
		 * @since 3.17.0
		 */
		positionEncodings?: PositionEncodingKind[];
	};

	/**
	 * Experimental client capabilities.
	 */
	experimental?: LSPAny;
}

interface InitializeResult {
	/**
	 * The capabilities the language server provides.
	 */
	capabilities: ServerCapabilities;

	/**
	 * Information about the server.
	 *
	 * @since 3.15.0
	 */
	serverInfo?: {
		/**
		 * The name of the server as defined by the server.
		 */
		name: string;

		/**
		 * The server's version as defined by the server.
		 */
		version?: string;
	};
}

/**
 * Known error codes for an `InitializeErrorCodes`;
 */
export namespace InitializeErrorCodes {

	/**
	 * If the protocol version provided by the client can't be handled by
	 * the server.
	 *
	 * @deprecated This initialize error got replaced by client capabilities.
	 * There is no version handshake in version 3.0x
	 */
	export const unknownProtocolVersion: 1 = 1;
}

export type InitializeErrorCodes = 1;

interface InitializeError {
	/**
	 * Indicates whether the client execute the following retry logic:
	 * (1) show the message provided by the ResponseError to the user
	 * (2) user selects retry or cancel
	 * (3) if user selected retry the initialize method is sent again.
	 */
	retry: boolean;
}

interface ServerCapabilities {

	/**
	 * The position encoding the server picked from the encodings offered
	 * by the client via the client capability `general.positionEncodings`.
	 *
	 * If the client didn't provide any position encodings the only valid
	 * value that a server can return is 'utf-16'.
	 *
	 * If omitted it defaults to 'utf-16'.
	 *
	 * @since 3.17.0
	 */
	positionEncoding?: PositionEncodingKind;

	/**
	 * Defines how text documents are synced. Is either a detailed structure
	 * defining each notification or for backwards compatibility the
	 * TextDocumentSyncKind number. If omitted it defaults to
	 * `TextDocumentSyncKind.None`.
	 */
	textDocumentSync?: TextDocumentSyncOptions | TextDocumentSyncKind;

	/**
	 * Defines how notebook documents are synced.
	 *
	 * @since 3.17.0
	 */
	notebookDocumentSync?: NotebookDocumentSyncOptions
		| NotebookDocumentSyncRegistrationOptions;

	/**
	 * The server provides completion support.
	 */
	completionProvider?: CompletionOptions;

	/**
	 * The server provides hover support.
	 */
	hoverProvider?: boolean | HoverOptions;

	/**
	 * The server provides signature help support.
	 */
	signatureHelpProvider?: SignatureHelpOptions;

	/**
	 * The server provides go to declaration support.
	 *
	 * @since 3.14.0
	 */
	declarationProvider?: boolean | DeclarationOptions
		| DeclarationRegistrationOptions;

	/**
	 * The server provides goto definition support.
	 */
	definitionProvider?: boolean | DefinitionOptions;

	/**
	 * The server provides goto type definition support.
	 *
	 * @since 3.6.0
	 */
	typeDefinitionProvider?: boolean | TypeDefinitionOptions
		| TypeDefinitionRegistrationOptions;

	/**
	 * The server provides goto implementation support.
	 *
	 * @since 3.6.0
	 */
	implementationProvider?: boolean | ImplementationOptions
		| ImplementationRegistrationOptions;

	/**
	 * The server provides find references support.
	 */
	referencesProvider?: boolean | ReferenceOptions;

	/**
	 * The server provides document highlight support.
	 */
	documentHighlightProvider?: boolean | DocumentHighlightOptions;

	/**
	 * The server provides document symbol support.
	 */
	documentSymbolProvider?: boolean | DocumentSymbolOptions;

	/**
	 * The server provides code actions. The `CodeActionOptions` return type is
	 * only valid if the client signals code action literal support via the
	 * property `textDocument.codeAction.codeActionLiteralSupport`.
	 */
	codeActionProvider?: boolean | CodeActionOptions;

	/**
	 * The server provides code lens.
	 */
	codeLensProvider?: CodeLensOptions;

	/**
	 * The server provides document link support.
	 */
	documentLinkProvider?: DocumentLinkOptions;

	/**
	 * The server provides color provider support.
	 *
	 * @since 3.6.0
	 */
	colorProvider?: boolean | DocumentColorOptions
		| DocumentColorRegistrationOptions;

	/**
	 * The server provides document formatting.
	 */
	documentFormattingProvider?: boolean | DocumentFormattingOptions;

	/**
	 * The server provides document range formatting.
	 */
	documentRangeFormattingProvider?: boolean | DocumentRangeFormattingOptions;

	/**
	 * The server provides document formatting on typing.
	 */
	documentOnTypeFormattingProvider?: DocumentOnTypeFormattingOptions;

	/**
	 * The server provides rename support. RenameOptions may only be
	 * specified if the client states that it supports
	 * `prepareSupport` in its initial `initialize` request.
	 */
	renameProvider?: boolean | RenameOptions;

	/**
	 * The server provides folding provider support.
	 *
	 * @since 3.10.0
	 */
	foldingRangeProvider?: boolean | FoldingRangeOptions
		| FoldingRangeRegistrationOptions;

	/**
	 * The server provides execute command support.
	 */
	executeCommandProvider?: ExecuteCommandOptions;

	/**
	 * The server provides selection range support.
	 *
	 * @since 3.15.0
	 */
	selectionRangeProvider?: boolean | SelectionRangeOptions
		| SelectionRangeRegistrationOptions;

	/**
	 * The server provides linked editing range support.
	 *
	 * @since 3.16.0
	 */
	linkedEditingRangeProvider?: boolean | LinkedEditingRangeOptions
		| LinkedEditingRangeRegistrationOptions;

	/**
	 * The server provides call hierarchy support.
	 *
	 * @since 3.16.0
	 */
	callHierarchyProvider?: boolean | CallHierarchyOptions
		| CallHierarchyRegistrationOptions;

	/**
	 * The server provides semantic tokens support.
	 *
	 * @since 3.16.0
	 */
	semanticTokensProvider?: SemanticTokensOptions
		| SemanticTokensRegistrationOptions;

	/**
	 * Whether server provides moniker support.
	 *
	 * @since 3.16.0
	 */
	monikerProvider?: boolean | MonikerOptions | MonikerRegistrationOptions;

	/**
	 * The server provides type hierarchy support.
	 *
	 * @since 3.17.0
	 */
	typeHierarchyProvider?: boolean | TypeHierarchyOptions
		 | TypeHierarchyRegistrationOptions;

	/**
	 * The server provides inline values.
	 *
	 * @since 3.17.0
	 */
	inlineValueProvider?: boolean | InlineValueOptions
		 | InlineValueRegistrationOptions;

	/**
	 * The server provides inlay hints.
	 *
	 * @since 3.17.0
	 */
	inlayHintProvider?: boolean | InlayHintOptions
		 | InlayHintRegistrationOptions;

	/**
	 * The server has support for pull model diagnostics.
	 *
	 * @since 3.17.0
	 */
	diagnosticProvider?: DiagnosticOptions | DiagnosticRegistrationOptions;

	/**
	 * The server provides workspace symbol support.
	 */
	workspaceSymbolProvider?: boolean | WorkspaceSymbolOptions;

	/**
	 * The server provides inline completions.
	 *
	 * @since 3.18.0
	 */
	inlineCompletionProvider?: boolean | InlineCompletionOptions;

	/**
	 * Text document specific server capabilities.
	 *
	 * @since 3.18.0
	 */
	textDocument?: {
		/**
		 * Capabilities specific to the diagnostic pull model.
		 *
		 * @since 3.18.0
		 */
		diagnostic?: {
			/**
			 * Whether the server supports `MarkupContent` in diagnostic messages.
			 *
			 * @since 3.18.0
			 * @proposed
			 */
			markupMessageSupport?: boolean;
		};
	};

	/**
	 * Workspace specific server capabilities
	 */
	workspace?: {
		/**
		 * The server supports workspace folder.
		 *
		 * @since 3.6.0
		 */
		workspaceFolders?: WorkspaceFoldersServerCapabilities;

		/**
		 * The server is interested in file notifications/requests.
		 *
		 * @since 3.16.0
		 */
		fileOperations?: {
			/**
			 * The server is interested in receiving didCreateFiles
			 * notifications.
			 */
			didCreate?: FileOperationRegistrationOptions;

			/**
			 * The server is interested in receiving willCreateFiles requests.
			 */
			willCreate?: FileOperationRegistrationOptions;

			/**
			 * The server is interested in receiving didRenameFiles
			 * notifications.
			 */
			didRename?: FileOperationRegistrationOptions;

			/**
			 * The server is interested in receiving willRenameFiles requests.
			 */
			willRename?: FileOperationRegistrationOptions;

			/**
			 * The server is interested in receiving didDeleteFiles file
			 * notifications.
			 */
			didDelete?: FileOperationRegistrationOptions;

			/**
			 * The server is interested in receiving willDeleteFiles file
			 * requests.
			 */
			willDelete?: FileOperationRegistrationOptions;
		};
	};

	/**
	 * Experimental server capabilities.
	 */
	experimental?: LSPAny;
}


/* source file: "messages/3.18/initialized.md" */

interface InitializedParams {
}


/* source file: "messages/3.18/registerCapability.md" */

/**
 * General parameters to register for a capability.
 */
export interface Registration {
	/**
	 * The id used to register the request. The id can be used to deregister
	 * the request again.
	 */
	id: string;

	/**
	 * The method / capability to register for.
	 */
	method: string;

	/**
	 * Options necessary for the registration.
	 */
	registerOptions?: LSPAny;
}

export interface RegistrationParams {
	registrations: Registration[];
}


/**
 * Static registration options to be returned in the initialize request.
 */
export interface StaticRegistrationOptions {
	/**
	 * The id used to register the request. The id can be used to deregister
	 * the request again. See also Registration#id.
	 */
	id?: string;
}

/**
 * General text document registration options.
 */
export interface TextDocumentRegistrationOptions {
	/**
	 * A document selector to identify the scope of the registration. If set to
	 * null, the document selector provided on the client side will be used.
	 */
	documentSelector: DocumentSelector | null;
}


/* source file: "messages/3.18/unregisterCapability.md" */

/**
 * General parameters to unregister a capability.
 */
export interface Unregistration {
	/**
	 * The id used to unregister the request or notification. Usually an id
	 * provided during the register request.
	 */
	id: string;

	/**
	 * The method / capability to unregister for.
	 */
	method: string;
}

export interface UnregistrationParams {
	// This should correctly be named `unregistrations`. However, changing this
	// is a breaking change and needs to wait until we deliver a 4.x version
	// of the specification.
	unregisterations: Unregistration[];
}



/* source file: "messages/3.18/setTrace.md" */

interface SetTraceParams {
	/**
	 * The new value that should be assigned to the trace setting.
	 */
	value: TraceValue;
}


/* source file: "messages/3.18/logTrace.md" */

interface LogTraceParams {
	/**
	 * The message to be logged.
	 */
	message: string;
	/**
	 * Additional information that can be computed if the `trace` configuration
	 * is set to `'verbose'`.
	 */
	verbose?: string;
}


/* source file: "messages/3.18/shutdown.md" */


/* source file: "messages/3.18/exit.md" */

/**
 * Defines how the host (editor) should sync document changes to the language
 * server.
 */
export namespace TextDocumentSyncKind {
	/**
	 * Documents should not be synced at all.
	 */
	export const None = 0;

	/**
	 * Documents are synced by always sending the full content
	 * of the document.
	 */
	export const Full = 1;

	/**
	 * Documents are synced by sending the full content on open.
	 * After that only incremental updates to the document are
	 * sent.
	 */
	export const Incremental = 2;
}

export type TextDocumentSyncKind = 0 | 1 | 2;

export interface TextDocumentSyncOptions {
	/**
	 * Open and close notifications are sent to the server. If omitted open
	 * close notifications should not be sent.
	 */
	openClose?: boolean;

	/**
	 * Change notifications are sent to the server. See
	 * TextDocumentSyncKind.None, TextDocumentSyncKind.Full and
	 * TextDocumentSyncKind.Incremental. If omitted it defaults to
	 * TextDocumentSyncKind.None.
	 */
	change?: TextDocumentSyncKind;
}


/* source file: "textDocument/didOpen.md" */

interface DidOpenTextDocumentParams {
	/**
	 * The document that was opened.
	 */
	textDocument: TextDocumentItem;
}


/* source file: "textDocument/didChange.md" */

/**
 * Describe options to be used when registering for text document change events.
 */
export interface TextDocumentChangeRegistrationOptions
	extends TextDocumentRegistrationOptions {
	/**
	 * How documents are synced to the server. See TextDocumentSyncKind.Full
	 * and TextDocumentSyncKind.Incremental.
	 */
	syncKind: TextDocumentSyncKind;
}

interface DidChangeTextDocumentParams {
	/**
	 * The document that did change. The version number points
	 * to the version after all provided content changes have
	 * been applied.
	 */
	textDocument: VersionedTextDocumentIdentifier;

	/**
	 * The actual content changes. The content changes describe single state
	 * changes to the document. So if there are two content changes c1 (at
	 * array index 0) and c2 (at array index 1) for a document in state S then
	 * c1 moves the document from S to S' and c2 from S' to S''. So c1 is
	 * computed on the state S and c2 is computed on the state S'.
	 *
	 * To mirror the content of a document using change events use the following
	 * approach:
	 * - start with the same initial content
	 * - apply the 'textDocument/didChange' notifications in the order you
	 *   receive them.
	 * - apply the `TextDocumentContentChangeEvent`s in a single notification
	 *   in the order you receive them.
	 */
	contentChanges: TextDocumentContentChangeEvent[];
}

/**
 * An event describing a change to a text document. If only a text is provided
 * it is considered to be the full content of the document.
 */
export type TextDocumentContentChangeEvent = {
	/**
	 * The range of the document that changed.
	 */
	range: Range;

	/**
	 * The optional length of the range that got replaced.
	 *
	 * @deprecated use range instead.
	 */
	rangeLength?: uinteger;

	/**
	 * The new text for the provided range.
	 */
	text: string;
} | {
	/**
	 * The new text of the whole document.
	 */
	text: string;
};


/* source file: "textDocument/willSave.md" */

/**
 * The parameters send in a will save text document notification.
 */
export interface WillSaveTextDocumentParams {
	/**
	 * The document that will be saved.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The 'TextDocumentSaveReason'.
	 */
	reason: TextDocumentSaveReason;
}

/**
 * Represents reasons why a text document is saved.
 */
export namespace TextDocumentSaveReason {

	/**
	 * Manually triggered, e.g. by the user pressing save, by starting
	 * debugging, or by an API call.
	 */
	export const Manual = 1;

	/**
	 * Automatic after a delay.
	 */
	export const AfterDelay = 2;

	/**
	 * When the editor lost focus.
	 */
	export const FocusOut = 3;
}

export type TextDocumentSaveReason = 1 | 2 | 3;


/* source file: "textDocument/willSaveWaitUntil.md" */


/* source file: "textDocument/didSave.md" */

export interface SaveOptions {
	/**
	 * The client is supposed to include the content on save.
	 */
	includeText?: boolean;
}

export interface TextDocumentSaveRegistrationOptions
	extends TextDocumentRegistrationOptions {
	/**
	 * The client is supposed to include the content on save.
	 */
	includeText?: boolean;
}

interface DidSaveTextDocumentParams {
	/**
	 * The document that was saved.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * Optional the content when saved. Depends on the includeText value
	 * when the save notification was requested.
	 */
	text?: string;
}


/* source file: "textDocument/didClose.md" */

interface DidCloseTextDocumentParams {
	/**
	 * The document that was closed.
	 */
	textDocument: TextDocumentIdentifier;
}


/* source file: "textDocument/didRename.md" */

export interface TextDocumentSyncClientCapabilities {
	/**
	 * Whether text document synchronization supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports sending will save notifications.
	 */
	willSave?: boolean;

	/**
	 * The client supports sending a will save request and
	 * waits for a response providing text edits which will
	 * be applied to the document before it is saved.
	 */
	willSaveWaitUntil?: boolean;

	/**
	 * The client supports did save notifications.
	 */
	didSave?: boolean;
}

export interface TextDocumentSyncOptions {
	/**
	 * Open and close notifications are sent to the server. If omitted open
	 * close notification should not be sent.
	 */
	openClose?: boolean;
	/**
	 * Change notifications are sent to the server. See
	 * TextDocumentSyncKind.None, TextDocumentSyncKind.Full and
	 * TextDocumentSyncKind.Incremental. If omitted it defaults to
	 * TextDocumentSyncKind.None.
	 */
	change?: TextDocumentSyncKind;
	/**
	 * If present will save notifications are sent to the server. If omitted
	 * the notification should not be sent.
	 */
	willSave?: boolean;
	/**
	 * If present will save wait until requests are sent to the server. If
	 * omitted the request should not be sent.
	 */
	willSaveWaitUntil?: boolean;
	/**
	 * If present save notifications are sent to the server. If omitted the
	 * notification should not be sent.
	 */
	save?: boolean | SaveOptions;
}


/* source file: "notebookDocument/notebook.md" */

/**
 * A notebook document.
 *
 * @since 3.17.0
 */
export interface NotebookDocument {

	/**
	 * The notebook document's URI.
	 */
	uri: URI;

	/**
	 * The type of the notebook.
	 */
	notebookType: string;

	/**
	 * The version number of this document (it will increase after each
	 * change, including undo/redo).
	 */
	version: integer;

	/**
	 * Additional metadata stored with the notebook
	 * document.
	 */
	metadata?: LSPObject;

	/**
	 * The cells of a notebook.
	 */
	cells: NotebookCell[];
}

/**
 * A notebook cell.
 *
 * A cell's document URI must be unique across ALL notebook
 * cells and can therefore be used to uniquely identify a
 * notebook cell or the cell's text document.
 *
 * @since 3.17.0
 */
export interface NotebookCell {

	/**
	 * The cell's kind.
	 */
	kind: NotebookCellKind;

	/**
	 * The URI of the cell's text document
	 * content.
	 */
	document: DocumentUri;

	/**
	 * Additional metadata stored with the cell.
	 */
	metadata?: LSPObject;

	/**
	 * Additional execution summary information
	 * if supported by the client.
	 */
	executionSummary?: ExecutionSummary;
}

/**
 * A notebook cell kind.
 *
 * @since 3.17.0
 */
export namespace NotebookCellKind {

	/**
	 * A markup-cell is a formatted source that is used for display.
	 */
	export const Markup: 1 = 1;

	/**
	 * A code-cell is source code.
	 */
	export const Code: 2 = 2;
}

export interface ExecutionSummary {
	/**
	 * A strictly monotonically increasing value
	 * indicating the execution order of a cell
	 * inside a notebook.
	 */
	executionOrder: uinteger;

	/**
	 * Whether the execution was successful or
	 * not if known by the client.
	 */
	success?: boolean;
}

/**
 * A notebook cell text document filter denotes a cell text
 * document by different properties.
 *
 * @since 3.17.0
 */
export interface NotebookCellTextDocumentFilter {
	/**
	 * A filter that matches against the notebook
	 * containing the notebook cell. If a string
	 * value is provided, it matches against the
	 * notebook type. '*' matches every notebook.
	 */
	notebook: string | NotebookDocumentFilter;

	/**
	 * A language ID like `python`.
	 *
	 * Will be matched against the language ID of the
	 * notebook cell document. '*' matches every language.
	 */
	language?: string;
}

/**
 * A notebook document filter denotes a notebook document by
 * different properties.
 *
 * @since 3.17.0
 */
export type NotebookDocumentFilter = {
	/**
	 * The type of the enclosing notebook.
	 */
	notebookType: string;

	/**
	 * A Uri scheme, like `file` or `untitled`.
    */
	scheme?: string;

	/**
	 * A glob pattern.
	 */
	pattern?: GlobPattern;
} | {
	/**
	 * The type of the enclosing notebook.
	 */
	notebookType?: string;

	/**
	 * A Uri scheme, like `file` or `untitled`.
	 */
	scheme: string;

	/**
	 * A glob pattern.
	 */
	pattern?: GlobPattern;
} | {
	/**
	 * The type of the enclosing notebook.
	 */
	notebookType?: string;

	/**
	 * A Uri scheme, like `file` or `untitled`.
	 */
	scheme?: string;

	/**
	 * A glob pattern.
	 */
	pattern: GlobPattern;
};





/**
 * Notebook specific client capabilities.
 *
 * @since 3.17.0
 */
export interface NotebookDocumentSyncClientCapabilities {

	/**
	 * Whether implementation supports dynamic registration. If this is
	 * set to `true`, the client supports the new
	 * `(NotebookDocumentSyncRegistrationOptions & NotebookDocumentSyncOptions)`
	 * return value for the corresponding server capability as well.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports sending execution summary data per cell.
	 */
	executionSummarySupport?: boolean;
}

/**
 * Options specific to a notebook plus its cells
 * to be synced to the server.
 *
 * If a selector provides a notebook document
 * filter but no cell selector, all cells of a
 * matching notebook document will be synced.
 *
 * If a selector provides no notebook document
 * filter but only a cell selector, all notebook
 * documents that contain at least one matching
 * cell will be synced.
 *
 * @since 3.17.0
 */
export interface NotebookDocumentSyncOptions {
	/**
	 * The notebooks to be synced
	 */
	notebookSelector: ({
		/**
		 * The notebook to be synced. If a string
		 * value is provided, it matches against the
		 * notebook type. '*' matches every notebook.
		 */
		notebook: string | NotebookDocumentFilter;

		/**
		 * The cells of the matching notebook to be synced.
		 */
		cells?: { language: string }[];
	} | {
		/**
		 * The notebook to be synced. If a string
		 * value is provided, it matches against the
		 * notebook type. '*' matches every notebook.
		 */
		notebook?: string | NotebookDocumentFilter;

		/**
		 * The cells of the matching notebook to be synced.
		 */
		cells: { language: string }[];
	})[];

	/**
	 * Whether save notifications should be forwarded to
	 * the server. Will only be honored if mode === `notebook`.
	 */
	save?: boolean;
}

/**
 * Registration options specific to a notebook.
 *
 * @since 3.17.0
 */
export interface NotebookDocumentSyncRegistrationOptions extends
	NotebookDocumentSyncOptions, StaticRegistrationOptions {
}

/**
 * The params sent in an open notebook document notification.
 *
 * @since 3.17.0
 */
export interface DidOpenNotebookDocumentParams {

	/**
	 * The notebook document that got opened.
	 */
	notebookDocument: NotebookDocument;

	/**
	 * The text documents that represent the content
	 * of a notebook cell.
	 */
	cellTextDocuments: TextDocumentItem[];
}

/**
 * The params sent in a change notebook document notification.
 *
 * @since 3.17.0
 */
export interface DidChangeNotebookDocumentParams {

	/**
	 * The notebook document that did change. The version number points
	 * to the version after all provided changes have been applied.
	 */
	notebookDocument: VersionedNotebookDocumentIdentifier;

	/**
	 * The actual changes to the notebook document.
	 *
	 * The change describes a single state change to the notebook document,
	 * so it moves a notebook document, its cells and its cell text document
	 * contents from state S to S'.
	 *
	 * To mirror the content of a notebook using change events use the
	 * following approach:
	 * - start with the same initial content
	 * - apply the 'notebookDocument/didChange' notifications in the order
	 *   you receive them.
	 */
	change: NotebookDocumentChangeEvent;
}

/**
 * A versioned notebook document identifier.
 *
 * @since 3.17.0
 */
export interface VersionedNotebookDocumentIdentifier {

	/**
	 * The version number of this notebook document.
	 */
	version: integer;

	/**
	 * The notebook document's URI.
	 */
	uri: URI;
}

/**
 * A change event for a notebook document.
 *
 * @since 3.17.0
 */
export interface NotebookDocumentChangeEvent {
	/**
	 * The changed meta data if any.
	 */
	metadata?: LSPObject;

	/**
	 * Changes to cells.
	 */
	cells?: {
		/**
		 * Changes to the cell structure to add or
		 * remove cells.
		 */
		structure?: {
			/**
			 * The change to the cell array.
			 */
			array: NotebookCellArrayChange;

			/**
			 * Additional opened cell text documents.
			 */
			didOpen?: TextDocumentItem[];

			/**
			 * Additional closed cell text documents.
			 */
			didClose?: TextDocumentIdentifier[];
		};

		/**
		 * Changes to notebook cells properties like its
		 * kind, execution summary or metadata.
		 */
		data?: NotebookCell[];

		/**
		 * Changes to the text content of notebook cells.
		 */
		textContent?: {
			document: VersionedTextDocumentIdentifier;
			changes: TextDocumentContentChangeEvent[];
		}[];
	};
}

/**
 * A change describing how to move a `NotebookCell`
 * array from state S to S'.
 *
 * @since 3.17.0
 */
export interface NotebookCellArrayChange {
	/**
	 * The start offset of the cell that changed.
	 */
	start: uinteger;

	/**
	 * The number of deleted cells.
	 */
	deleteCount: uinteger;

	/**
	 * The new cells, if any.
	 */
	cells?: NotebookCell[];
}

/**
 * The params sent in a save notebook document notification.
 *
 * @since 3.17.0
 */
export interface DidSaveNotebookDocumentParams {
	/**
	 * The notebook document that got saved.
	 */
	notebookDocument: NotebookDocumentIdentifier;
}

/**
 * The params sent in a close notebook document notification.
 *
 * @since 3.17.0
 */
export interface DidCloseNotebookDocumentParams {

	/**
	 * The notebook document that got closed.
	 */
	notebookDocument: NotebookDocumentIdentifier;

	/**
	 * The text documents that represent the content
	 * of a notebook cell that got closed.
	 */
	cellTextDocuments: TextDocumentIdentifier[];
}

/**
 * A literal to identify a notebook document in the client.
 *
 * @since 3.17.0
 */
export interface NotebookDocumentIdentifier {
	/**
	 * The notebook document's URI.
	 */
	uri: URI;
}


/* source file: "language/declaration.md" */

export interface DeclarationClientCapabilities {
	/**
	 * Whether declaration supports dynamic registration. If this is set to
	 * `true`, the client supports the new `DeclarationRegistrationOptions`
	 * return value for the corresponding server capability as well.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports additional metadata in the form of declaration links.
	 */
	linkSupport?: boolean;
}

export interface DeclarationOptions extends WorkDoneProgressOptions {
}

export interface DeclarationRegistrationOptions extends DeclarationOptions,
	TextDocumentRegistrationOptions, StaticRegistrationOptions {
}

export interface DeclarationParams extends TextDocumentPositionParams,
	WorkDoneProgressParams, PartialResultParams {
}


/* source file: "language/definition.md" */

export interface DefinitionClientCapabilities {
	/**
	 * Whether definition supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports additional metadata in the form of definition links.
	 *
	 * @since 3.14.0
	 */
	linkSupport?: boolean;
}

export interface DefinitionOptions extends WorkDoneProgressOptions {
}

export interface DefinitionRegistrationOptions extends
	TextDocumentRegistrationOptions, DefinitionOptions {
}

export interface DefinitionParams extends TextDocumentPositionParams,
	WorkDoneProgressParams, PartialResultParams {
}


/* source file: "language/typeDefinition.md" */

export interface TypeDefinitionClientCapabilities {
	/**
	 * Whether implementation supports dynamic registration. If this is set to
	 * `true`, the client supports the new `TypeDefinitionRegistrationOptions`
	 * return value for the corresponding server capability as well.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports additional metadata in the form of definition links.
	 *
	 * @since 3.14.0
	 */
	linkSupport?: boolean;
}

export interface TypeDefinitionOptions extends WorkDoneProgressOptions {
}

export interface TypeDefinitionRegistrationOptions extends
	TextDocumentRegistrationOptions, TypeDefinitionOptions,
	StaticRegistrationOptions {
}

export interface TypeDefinitionParams extends TextDocumentPositionParams,
	WorkDoneProgressParams, PartialResultParams {
}


/* source file: "language/implementation.md" */

export interface ImplementationClientCapabilities {
	/**
	 * Whether the implementation supports dynamic registration. If this is set to
	 * `true`, the client supports the new `ImplementationRegistrationOptions`
	 * return value for the corresponding server capability as well.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports additional metadata in the form of definition links.
	 *
	 * @since 3.14.0
	 */
	linkSupport?: boolean;
}

export interface ImplementationOptions extends WorkDoneProgressOptions {
}

export interface ImplementationRegistrationOptions extends
	TextDocumentRegistrationOptions, ImplementationOptions,
	StaticRegistrationOptions {
}

export interface ImplementationParams extends TextDocumentPositionParams,
	WorkDoneProgressParams, PartialResultParams {
}


/* source file: "language/references.md" */

export interface ReferenceClientCapabilities {
	/**
	 * Whether references supports dynamic registration.
	 */
	dynamicRegistration?: boolean;
}

export interface ReferenceOptions extends WorkDoneProgressOptions {
}

export interface ReferenceRegistrationOptions extends
	TextDocumentRegistrationOptions, ReferenceOptions {
}

export interface ReferenceParams extends TextDocumentPositionParams,
	WorkDoneProgressParams, PartialResultParams {
	context: ReferenceContext;
}

export interface ReferenceContext {
	/**
	 * Include the declaration of the current symbol.
	 */
	includeDeclaration: boolean;
}


/* source file: "language/callHierarchy.md" */

interface CallHierarchyClientCapabilities {
	/**
	 * Whether implementation supports dynamic registration. If this is set to
	 * `true` the client supports the new `(TextDocumentRegistrationOptions &
	 * StaticRegistrationOptions)` return value for the corresponding server
	 * capability as well.
	 */
	dynamicRegistration?: boolean;
}

export interface CallHierarchyOptions extends WorkDoneProgressOptions {
}

export interface CallHierarchyRegistrationOptions extends
	TextDocumentRegistrationOptions, CallHierarchyOptions,
	StaticRegistrationOptions {
}

export interface CallHierarchyPrepareParams extends TextDocumentPositionParams,
	WorkDoneProgressParams {
}

export interface CallHierarchyItem {
	/**
	 * The name of this item.
	 */
	name: string;

	/**
	 * The kind of this item.
	 */
	kind: SymbolKind;

	/**
	 * Tags for this item.
	 */
	tags?: SymbolTag[];

	/**
	 * More detail for this item, e.g. the signature of a function.
	 */
	detail?: string;

	/**
	 * The resource identifier of this item.
	 */
	uri: DocumentUri;

	/**
	 * The range enclosing this symbol not including leading/trailing whitespace
	 * but everything else, e.g. comments and code.
	 */
	range: Range;

	/**
	 * The range that should be selected and revealed when this symbol is being
	 * picked, e.g. the name of a function. Must be contained by the
	 * [`range`](#CallHierarchyItem.range).
	 */
	selectionRange: Range;

	/**
	 * A data entry field that is preserved between a call hierarchy prepare and
	 * incoming calls or outgoing calls requests.
	 */
	data?: LSPAny;
}

export interface CallHierarchyIncomingCallsParams extends
	WorkDoneProgressParams, PartialResultParams {
	item: CallHierarchyItem;
}

export interface CallHierarchyIncomingCall {

	/**
	 * The item that makes the call.
	 */
	from: CallHierarchyItem;

	/**
	 * The ranges at which the calls appear. This is relative to the caller
	 * denoted by [`this.from`](#CallHierarchyIncomingCall.from).
	 */
	fromRanges: Range[];
}

export interface CallHierarchyOutgoingCallsParams extends
	WorkDoneProgressParams, PartialResultParams {
	item: CallHierarchyItem;
}

export interface CallHierarchyOutgoingCall {

	/**
	 * The item that is called.
	 */
	to: CallHierarchyItem;

	/**
	 * The range at which this item is called. This is the range relative to
	 * the caller, e.g., the item passed to `callHierarchy/outgoingCalls` request.
	 */
	fromRanges: Range[];
}


/* source file: "language/typeHierarchy.md" */

type TypeHierarchyClientCapabilities = {
	/**
	 * Whether implementation supports dynamic registration. If this is set to
	 * `true` the client supports the new `(TextDocumentRegistrationOptions &
	 * StaticRegistrationOptions)` return value for the corresponding server
	 * capability as well.
	 */
	dynamicRegistration?: boolean;
};

export interface TypeHierarchyOptions extends WorkDoneProgressOptions {
}

export interface TypeHierarchyRegistrationOptions extends
	TextDocumentRegistrationOptions, TypeHierarchyOptions,
	StaticRegistrationOptions {
}

export interface TypeHierarchyPrepareParams extends TextDocumentPositionParams,
	WorkDoneProgressParams {
}

export interface TypeHierarchyItem {
	/**
	 * The name of this item.
	 */
	name: string;

	/**
	 * The kind of this item.
	 */
	kind: SymbolKind;

	/**
	 * Tags for this item.
	 */
	tags?: SymbolTag[];

	/**
	 * More detail for this item, e.g. the signature of a function.
	 */
	detail?: string;

	/**
	 * The resource identifier of this item.
	 */
	uri: DocumentUri;

	/**
	 * The range enclosing this symbol not including leading/trailing whitespace
	 * but everything else, e.g. comments and code.
	 */
	range: Range;

	/**
	 * The range that should be selected and revealed when this symbol is being
	 * picked, e.g. the name of a function. Must be contained by the
	 * [`range`](#TypeHierarchyItem.range).
	 */
	selectionRange: Range;

	/**
	 * A data entry field that is preserved between a type hierarchy prepare and
	 * supertypes or subtypes requests. It could also be used to identify the
	 * type hierarchy in the server, helping improve the performance on
	 * resolving supertypes and subtypes.
	 */
	data?: LSPAny;
}

export interface TypeHierarchySupertypesParams extends
	WorkDoneProgressParams, PartialResultParams {
	item: TypeHierarchyItem;
}

export interface TypeHierarchySubtypesParams extends
	WorkDoneProgressParams, PartialResultParams {
	item: TypeHierarchyItem;
}


/* source file: "language/documentHighlight.md" */

export interface DocumentHighlightClientCapabilities {
	/**
	 * Whether document highlight supports dynamic registration.
	 */
	dynamicRegistration?: boolean;
}

export interface DocumentHighlightOptions extends WorkDoneProgressOptions {
}

export interface DocumentHighlightRegistrationOptions extends
	TextDocumentRegistrationOptions, DocumentHighlightOptions {
}

export interface DocumentHighlightParams extends TextDocumentPositionParams,
	WorkDoneProgressParams, PartialResultParams {
}

/**
 * A document highlight is a range inside a text document which deserves
 * special attention. Usually a document highlight is visualized by changing
 * the background color of its range.
 *
 */
export interface DocumentHighlight {
	/**
	 * The range this highlight applies to.
	 */
	range: Range;

	/**
	 * The highlight kind, default is DocumentHighlightKind.Text.
	 */
	kind?: DocumentHighlightKind;
}

/**
 * A document highlight kind.
 */
export namespace DocumentHighlightKind {
	/**
	 * A textual occurrence.
	 */
	export const Text = 1;

	/**
	 * Read-access of a symbol, like reading a variable.
	 */
	export const Read = 2;

	/**
	 * Write-access of a symbol, like writing to a variable.
	 */
	export const Write = 3;
}

export type DocumentHighlightKind = 1 | 2 | 3;


/* source file: "language/documentLink.md" */

export interface DocumentLinkClientCapabilities {
	/**
	 * Whether document link supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Whether the client supports the `tooltip` property on `DocumentLink`.
	 *
	 * @since 3.15.0
	 */
	tooltipSupport?: boolean;
}

export interface DocumentLinkOptions extends WorkDoneProgressOptions {
	/**
	 * Document links have a resolve provider as well.
	 */
	resolveProvider?: boolean;
}

export interface DocumentLinkRegistrationOptions extends
	TextDocumentRegistrationOptions, DocumentLinkOptions {
}

interface DocumentLinkParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The document to provide document links for.
	 */
	textDocument: TextDocumentIdentifier;
}

/**
 * A document link is a range in a text document that links to an internal or
 * external resource, like another text document or a web site.
 */
interface DocumentLink {
	/**
	 * The range this link applies to.
	 */
	range: Range;

	/**
	 * The URI this link points to. If missing, a resolve request is sent later.
	 */
	target?: URI;

	/**
	 * The tooltip text when you hover over this link.
	 *
	 * If a tooltip is provided, it will be displayed in a string that includes
	 * instructions on how to trigger the link, such as `{0} (ctrl + click)`.
	 * The specific instructions vary depending on OS, user settings, and
	 * localization.
	 *
	 * @since 3.15.0
	 */
	tooltip?: string;

	/**
	 * A data entry field that is preserved on a document link between a
	 * DocumentLinkRequest and a DocumentLinkResolveRequest.
	 */
	data?: LSPAny;
}


/* source file: "language/hover.md" */

export interface HoverClientCapabilities {
	/**
	 * Whether hover supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Client supports the following content formats if the content
	 * property refers to a `literal of type MarkupContent`.
	 * The order describes the preferred format of the client.
	 */
	contentFormat?: MarkupKind[];
}

export interface HoverOptions extends WorkDoneProgressOptions {
}

export interface HoverRegistrationOptions
	extends TextDocumentRegistrationOptions, HoverOptions {
}

export interface HoverParams extends TextDocumentPositionParams,
	WorkDoneProgressParams {
}

/**
 * The result of a hover request.
 */
export interface Hover {
	/**
	 * The hover's content.
	 */
	contents: MarkedString | MarkedString[] | MarkupContent;

	/**
	 * An optional range is a range inside a text document
	 * that is used to visualize a hover, e.g. by changing the background color.
	 */
	range?: Range;
}

/**
 * MarkedString can be used to render human readable text. It is either a
 * markdown string or a code-block that provides a language and a code snippet.
 * The language identifier is semantically equal to the optional language
 * identifier in fenced code blocks in GitHub issues.
 *
 * The pair of a language and a value is an equivalent to markdown:
 * ```${language}
 * ${value}
 * ```
 *
 * Note that markdown strings will be sanitized - that means html will be
 * escaped.
 *
 * @deprecated use MarkupContent instead.
 */
type MarkedString = string | { language: string; value: string };


/* source file: "language/codeLens.md" */

export interface CodeLensClientCapabilities {
	/**
	 * Whether code lens supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Whether the client supports resolving additional code lens
	 * properties via a separate `codeLens/resolve` request.
	 *
	 * @since 3.18.0
	 */
	resolveSupport?: ClientCodeLensResolveOptions;
}

/**
 * @since 3.18.0
 */
export type ClientCodeLensResolveOptions = {
	/**
	 * The properties that a client can resolve lazily.
	 */
	properties: string[];
};

export interface CodeLensOptions extends WorkDoneProgressOptions {
	/**
	 * Code lens has a resolve provider as well.
	 */
	resolveProvider?: boolean;
}

export interface CodeLensRegistrationOptions extends
	TextDocumentRegistrationOptions, CodeLensOptions {
}

interface CodeLensParams extends WorkDoneProgressParams, PartialResultParams {
	/**
	 * The document to request code lens for.
	 */
	textDocument: TextDocumentIdentifier;
}

/**
 * A code lens represents a command that should be shown along with
 * source text, like the number of references, a way to run tests, etc.
 *
 * A code lens is _unresolved_ when no command is associated to it. For
 * performance reasons the creation of a code lens and resolving should be done
 * in two stages.
 */
interface CodeLens {
	/**
	 * The range in which this code lens is valid. Should only span a single
	 * line.
	 */
	range: Range;

	/**
	 * The command this code lens represents.
	 */
	command?: Command;

	/**
	 * A data entry field that is preserved on a code lens item between
	 * a code lens and a code lens resolve request.
	 */
	data?: LSPAny;
}

export interface CodeLensWorkspaceClientCapabilities {
	/**
	 * Whether the client implementation supports a refresh request sent from the
	 * server to the client.
	 *
	 * Note that this event is global and will force the client to refresh all
	 * code lenses currently shown. It should be used with absolute care and is
	 * useful for situation where a server, for example, detects a project wide
	 * change that requires such a calculation.
	 */
	refreshSupport?: boolean;
}


/* source file: "language/foldingRange.md" */

export interface FoldingRangeClientCapabilities {
	/**
	 * Whether implementation supports dynamic registration for folding range
	 * providers. If this is set to `true` the client supports the new
	 * `FoldingRangeRegistrationOptions` return value for the corresponding
	 * server capability as well.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The maximum number of folding ranges that the client prefers to receive
	 * per document. The value serves as a hint, servers are free to follow the
	 * limit.
	 */
	rangeLimit?: uinteger;

	/**
	 * If set, the client signals that it only supports folding complete lines.
	 * If set, client will ignore specified `startCharacter` and `endCharacter`
	 * properties in a FoldingRange.
	 */
	lineFoldingOnly?: boolean;

	/**
	 * Specific options for the folding range kind.
	 *
	 * @since 3.17.0
	 */
	foldingRangeKind? : {
		/**
		 * The folding range kind values the client supports. When this
		 * property exists the client also guarantees that it will
		 * handle values outside its set gracefully and falls back
		 * to a default value when unknown.
		 */
		valueSet?: FoldingRangeKind[];
	};

	/**
	 * Specific options for the folding range.
	 * @since 3.17.0
	 */
	foldingRange?: {
		/**
		* If set, the client signals that it supports setting collapsedText on
		* folding ranges to display custom labels instead of the default text.
		*
		* @since 3.17.0
		*/
		collapsedText?: boolean;
	};
}

export interface FoldingRangeOptions extends WorkDoneProgressOptions {
}

export interface FoldingRangeRegistrationOptions extends
	TextDocumentRegistrationOptions, FoldingRangeOptions,
	StaticRegistrationOptions {
}

export interface FoldingRangeParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;
}

/**
 * A set of predefined range kinds.
 */
export namespace FoldingRangeKind {
	/**
	 * Folding range for a comment
	 */
	export const Comment = 'comment';

	/**
	 * Folding range for imports or includes
	 */
	export const Imports = 'imports';

	/**
	 * Folding range for a region (e.g. `#region`)
	 */
	export const Region = 'region';
}

/**
 * The type is a string since the value set is extensible
 */
export type FoldingRangeKind = string;

/**
 * Represents a folding range. To be valid, start and end line must be bigger
 * than zero and smaller than the number of lines in the document. Clients
 * are free to ignore invalid ranges.
 */
export interface FoldingRange {

	/**
	 * The zero-based start line of the range to fold. The folded area starts
	 * after the line's last character. To be valid, the end must be zero or
	 * larger and smaller than the number of lines in the document.
	 */
	startLine: uinteger;

	/**
	 * The zero-based character offset from where the folded range starts. If
	 * not defined, defaults to the length of the start line.
	 */
	startCharacter?: uinteger;

	/**
	 * The zero-based end line of the range to fold. The folded area ends with
	 * the line's last character. To be valid, the end must be zero or larger
	 * and smaller than the number of lines in the document.
	 */
	endLine: uinteger;

	/**
	 * The zero-based character offset before the folded range ends. If not
	 * defined, defaults to the length of the end line.
	 */
	endCharacter?: uinteger;

	/**
	 * Describes the kind of the folding range such as `comment` or `region`.
	 * The kind is used to categorize folding ranges and used by commands like
	 * 'Fold all comments'. See [FoldingRangeKind](#FoldingRangeKind) for an
	 * enumeration of standardized kinds.
	 */
	kind?: FoldingRangeKind;

	/**
	 * The text that the client should show when the specified range is
	 * collapsed. If not defined or not supported by the client, a default
	 * will be chosen by the client.
	 *
	 * @since 3.17.0 - proposed
	 */
	collapsedText?: string;
}

export interface FoldingRangeWorkspaceClientCapabilities {
	/**
	 * Whether the client implementation supports a refresh request sent from the
	 * server to the client.
	 *
	 * Note that this event is global and will force the client to refresh all
	 * folding ranges currently shown. It should be used with absolute care and is
	 * useful for situation where a server, for example, detects a project wide
	 * change that requires such a calculation.
	 * 
	 * @since 3.18.0
	 * @proposed
	 */
	refreshSupport?: boolean;
}


/* source file: "language/selectionRange.md" */

export interface SelectionRangeClientCapabilities {
	/**
	 * Whether the implementation supports dynamic registration for selection range
	 * providers. If this is set to `true`, the client supports the new
	 * `SelectionRangeRegistrationOptions` return value for the corresponding
	 * server capability as well.
	 */
	dynamicRegistration?: boolean;
}

export interface SelectionRangeOptions extends WorkDoneProgressOptions {
}

export interface SelectionRangeRegistrationOptions extends
	SelectionRangeOptions, TextDocumentRegistrationOptions,
	StaticRegistrationOptions {
}

export interface SelectionRangeParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The positions inside the text document.
	 */
	positions: Position[];
}

export interface SelectionRange {
	/**
	 * The [range](#Range) of this selection range.
	 */
	range: Range;
	/**
	 * The parent selection range containing this range.
	 * Therefore, `parent.range` must contain `this.range`.
	 */
	parent?: SelectionRange;
}


/* source file: "language/documentSymbol.md" */

export interface DocumentSymbolClientCapabilities {
	/**
	 * Whether document symbol supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Specific capabilities for the `SymbolKind` in the
	 * `textDocument/documentSymbol` request.
	 */
	symbolKind?: {
		/**
		 * The symbol kind values the client supports. When this
		 * property exists the client also guarantees that it will
		 * handle values outside its set gracefully and falls back
		 * to a default value when unknown.
		 *
		 * If this property is not present the client only supports
		 * the symbol kinds from `File` to `Array` as defined in
		 * the initial version of the protocol.
		 */
		valueSet?: SymbolKind[];
	};

	/**
	 * The client supports hierarchical document symbols.
	 */
	hierarchicalDocumentSymbolSupport?: boolean;

	/**
	 * The client supports tags on `SymbolInformation`. Tags are supported on
	 * `DocumentSymbol` if `hierarchicalDocumentSymbolSupport` is set to true.
	 * Clients supporting tags have to handle unknown tags gracefully.
	 *
	 * @since 3.16.0
	 */
	tagSupport?: {
		/**
		 * The tags supported by the client.
		 */
		valueSet: SymbolTag[];
	};

	/**
	 * The client supports an additional label presented in the UI when
	 * registering a document symbol provider.
	 *
	 * @since 3.16.0
	 */
	labelSupport?: boolean;
}

export interface DocumentSymbolOptions extends WorkDoneProgressOptions {
	/**
	 * A human-readable string that is shown when multiple outlines trees
	 * are shown for the same document.
	 *
	 * @since 3.16.0
	 */
	label?: string;
}

export interface DocumentSymbolRegistrationOptions extends
	TextDocumentRegistrationOptions, DocumentSymbolOptions {
}

export interface DocumentSymbolParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;
}

/**
 * A symbol kind.
 */
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

export type SymbolKind = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
	14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26;

/**
 * Symbol tags are extra annotations that tweak the rendering of a symbol.
 *
 * @since 3.16
 */
export namespace SymbolTag {

	/**
	 * Render a symbol as obsolete, usually using a strike-out.
	 */
	export const Deprecated: 1 = 1;
}

export type SymbolTag = 1;

/**
 * Represents programming constructs like variables, classes, interfaces etc.
 * that appear in a document. Document symbols can be hierarchical and they
 * have two ranges: one that encloses their definition and one that points to
 * their most interesting range, e.g. the range of an identifier.
 */
export interface DocumentSymbol {

	/**
	 * The name of this symbol. Will be displayed in the user interface and
	 * therefore must not be an empty string or a string only consisting of
	 * white spaces.
	 */
	name: string;

	/**
	 * More detail for this symbol, e.g. the signature of a function.
	 */
	detail?: string;

	/**
	 * The kind of this symbol.
	 */
	kind: SymbolKind;

	/**
	 * Tags for this document symbol.
	 *
	 * @since 3.16.0
	 */
	tags?: SymbolTag[];

	/**
	 * Indicates if this symbol is deprecated.
	 *
	 * @deprecated Use tags instead
	 */
	deprecated?: boolean;

	/**
	 * The range enclosing this symbol not including leading/trailing whitespace
	 * but everything else, like comments. This information is typically used to
	 * determine if the client's cursor is inside the symbol to reveal the
	 * symbol in the UI.
	 */
	range: Range;

	/**
	 * The range that should be selected and revealed when this symbol is being
	 * picked, e.g. the name of a function. Must be contained by the `range`.
	 */
	selectionRange: Range;

	/**
	 * Children of this symbol, e.g. properties of a class.
	 */
	children?: DocumentSymbol[];
}

/**
 * Represents information about programming constructs like variables, classes,
 * interfaces etc.
 *
 * @deprecated use DocumentSymbol or WorkspaceSymbol instead.
 */
export interface SymbolInformation {
	/**
	 * The name of this symbol.
	 */
	name: string;

	/**
	 * The kind of this symbol.
	 */
	kind: SymbolKind;

	/**
	 * Tags for this symbol.
	 *
	 * @since 3.16.0
	 */
	tags?: SymbolTag[];

	/**
	 * Indicates if this symbol is deprecated.
	 *
	 * @deprecated Use tags instead
	 */
	deprecated?: boolean;

	/**
	 * The location of this symbol. The location's range is used by a tool
	 * to reveal the location in the editor. If the symbol is selected in the
	 * tool the range's start information is used to position the cursor. So
	 * the range usually spans more then the actual symbol's name and does
	 * normally include things like visibility modifiers.
	 *
	 * The range doesn't have to denote a node range in the sense of an abstract
	 * syntax tree. It can therefore not be used to re-construct a hierarchy of
	 * the symbols.
	 */
	location: Location;

	/**
	 * The name of the symbol containing this symbol. This information is for
	 * user interface purposes (e.g. to render a qualifier in the user interface
	 * if necessary). It can't be used to re-infer a hierarchy for the document
	 * symbols.
	 */
	containerName?: string;
}


/* source file: "language/semanticTokens.md" */

export enum SemanticTokenTypes {
	namespace = 'namespace',
	/**
	 * Represents a generic type. Acts as a fallback for types which
	 * can't be mapped to a specific type like class or enum.
	 */
	type = 'type',
	class = 'class',
	enum = 'enum',
	interface = 'interface',
	struct = 'struct',
	typeParameter = 'typeParameter',
	parameter = 'parameter',
	variable = 'variable',
	property = 'property',
	enumMember = 'enumMember',
	event = 'event',
	function = 'function',
	method = 'method',
	macro = 'macro',
	keyword = 'keyword',
	modifier = 'modifier',
	comment = 'comment',
	string = 'string',
	number = 'number',
	regexp = 'regexp',
	operator = 'operator',
	/**
	 * @since 3.17.0
	 */
	decorator = 'decorator',
	/**
	 * @since 3.18.0
	 */
	label = 'label'
}

export enum SemanticTokenModifiers {
	declaration = 'declaration',
	definition = 'definition',
	readonly = 'readonly',
	static = 'static',
	deprecated = 'deprecated',
	abstract = 'abstract',
	async = 'async',
	modification = 'modification',
	documentation = 'documentation',
	defaultLibrary = 'defaultLibrary'
}

export namespace TokenFormat {
	export const Relative: 'relative' = 'relative';
}

export type TokenFormat = 'relative';

export interface SemanticTokensLegend {
	/**
	 * The token types a server uses.
	 */
	tokenTypes: string[];

	/**
	 * The token modifiers a server uses.
	 */
	tokenModifiers: string[];
}








interface SemanticTokensClientCapabilities {
	/**
	 * Whether the implementation supports dynamic registration. If this is set to
	 * `true`, the client supports the new `(TextDocumentRegistrationOptions &
	 * StaticRegistrationOptions)` return value for the corresponding server
	 * capability as well.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Which requests the client supports and might send to the server
	 * depending on the server's capability. Please note that clients might not
	 * show semantic tokens or degrade some of the user experience if a range
	 * or full request is advertised by the client but not provided by the
	 * server. If, for example, the client capability `requests.full` and
	 * `request.range` are both set to true but the server only provides a
	 * range provider, the client might not render a minimap correctly or might
	 * even decide to not show any semantic tokens at all.
	 */
	requests: {
		/**
		 * The client will send the `textDocument/semanticTokens/range` request
		 * if the server provides a corresponding handler.
		 */
		range?: boolean | {
		};

		/**
		 * The client will send the `textDocument/semanticTokens/full` request
		 * if the server provides a corresponding handler.
		 */
		full?: boolean | {
			/**
			 * The client will send the `textDocument/semanticTokens/full/delta`
			 * request if the server provides a corresponding handler.
			 */
			delta?: boolean;
		};
	};

	/**
	 * The token types that the client supports.
	 */
	tokenTypes: string[];

	/**
	 * The token modifiers that the client supports.
	 */
	tokenModifiers: string[];

	/**
	 * The formats the client supports.
	 */
	formats: TokenFormat[];

	/**
	 * Whether the client supports tokens that can overlap each other.
	 */
	overlappingTokenSupport?: boolean;

	/**
	 * Whether the client supports tokens that can span multiple lines.
	 */
	multilineTokenSupport?: boolean;

	/**
	 * Whether the client allows the server to actively cancel a
	 * semantic token request, e.g. supports returning
	 * ErrorCodes.ServerCancelled. If a server does so, the client
	 * needs to retrigger the request.
	 *
	 * @since 3.17.0
	 */
	serverCancelSupport?: boolean;

	/**
	 * Whether the client uses semantic tokens to augment existing
	 * syntax tokens. If set to `true`, client side created syntax
	 * tokens and semantic tokens are both used for colorization. If
	 * set to `false`, the client only uses the returned semantic tokens
	 * for colorization.
	 *
	 * If the value is `undefined` then the client behavior is not
	 * specified.
	 *
	 * @since 3.17.0
	 */
	augmentsSyntaxTokens?: boolean;
}

export interface SemanticTokensOptions extends WorkDoneProgressOptions {
	/**
	 * The legend used by the server.
	 */
	legend: SemanticTokensLegend;

	/**
	 * Server supports providing semantic tokens for a specific range
	 * of a document.
	 */
	range?: boolean | {
	};

	/**
	 * Server supports providing semantic tokens for a full document.
	 */
	full?: boolean | {
		/**
		 * The server supports deltas for full documents.
		 */
		delta?: boolean;
	};
}

export interface SemanticTokensRegistrationOptions extends
	TextDocumentRegistrationOptions, SemanticTokensOptions,
	StaticRegistrationOptions {
}

export interface SemanticTokensParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;
}

export interface SemanticTokens {
	/**
	 * An optional result ID. If provided and clients support delta updating,
	 * the client will include the result ID in the next semantic token request.
	 * A server can then, instead of computing all semantic tokens again, simply
	 * send a delta.
	 */
	resultId?: string;

	/**
	 * The actual tokens.
	 */
	data: uinteger[];
}

export interface SemanticTokensPartialResult {
	data: uinteger[];
}

export interface SemanticTokensDeltaParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The result ID of a previous response. The result ID can either point to
	 * a full response or a delta response, depending on what was received last.
	 */
	previousResultId: string;
}

export interface SemanticTokensDelta {
	readonly resultId?: string;
	/**
	 * The semantic token edits to transform a previous result into a new
	 * result.
	 */
	edits: SemanticTokensEdit[];
}

export interface SemanticTokensEdit {
	/**
	 * The start offset of the edit.
	 */
	start: uinteger;

	/**
	 * The count of elements to remove.
	 */
	deleteCount: uinteger;

	/**
	 * The elements to insert.
	 */
	data?: uinteger[];
}

export interface SemanticTokensDeltaPartialResult {
	edits: SemanticTokensEdit[];
}

export interface SemanticTokensRangeParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The range the semantic tokens are requested for.
	 */
	range: Range;
}

export interface SemanticTokensWorkspaceClientCapabilities {
	/**
	 * Whether the client implementation supports a refresh request sent from
	 * the server to the client.
	 *
	 * Note that this event is global and will force the client to refresh all
	 * semantic tokens currently shown. It should be used with absolute care
	 * and is useful for situation where a server, for example, detects a project
	 * wide change that requires such a calculation.
	 */
	refreshSupport?: boolean;
}


/* source file: "language/inlayHint.md" */

/**
 * Inlay hint client capabilities.
 *
 * @since 3.17.0
 */
export interface InlayHintClientCapabilities {

	/**
	 * Whether inlay hints support dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Indicates which properties a client can resolve lazily on an inlay
	 * hint.
	 */
	resolveSupport?: {

		/**
		 * The properties that a client can resolve lazily.
		 */
		properties: string[];
	};
}

/**
 * Inlay hint options used during static registration.
 *
 * @since 3.17.0
 */
export interface InlayHintOptions extends WorkDoneProgressOptions {
	/**
	 * The server provides support to resolve additional
	 * information for an inlay hint item.
	 */
	resolveProvider?: boolean;
}

/**
 * Inlay hint options used during static or dynamic registration.
 *
 * @since 3.17.0
 */
export interface InlayHintRegistrationOptions extends InlayHintOptions,
	TextDocumentRegistrationOptions, StaticRegistrationOptions {
}

/**
 * A parameter literal used in inlay hint requests.
 *
 * @since 3.17.0
 */
export interface InlayHintParams extends WorkDoneProgressParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The visible document range for which inlay hints should be computed.
	 */
	range: Range;
}

/**
 * Inlay hint information.
 *
 * @since 3.17.0
 */
export interface InlayHint {

	/**
	 * The position of this hint.
	 *
	 * If multiple hints have the same position, they will be shown in the order
	 * they appear in the response.
	 */
	position: Position;

	/**
	 * The label of this hint. A human readable string or an array of
	 * InlayHintLabelPart label parts.
	 *
	 * *Note* that neither the string nor the label part can be empty.
	 */
	label: string | InlayHintLabelPart[];

	/**
	 * The kind of this hint. Can be omitted in which case the client
	 * should fall back to a reasonable default.
	 */
	kind?: InlayHintKind;

	/**
	 * Optional text edits that are performed when accepting this inlay hint.
	 *
	 * *Note* that edits are expected to change the document so that the inlay
	 * hint (or its nearest variant) is now part of the document and the inlay
	 * hint itself is now obsolete.
	 *
	 * Depending on the client capability `inlayHint.resolveSupport`,
	 * clients might resolve this property late using the resolve request.
	 */
	textEdits?: TextEdit[];

	/**
	 * The tooltip text when you hover over this item.
	 *
	 * Depending on the client capability `inlayHint.resolveSupport` clients
	 * might resolve this property late using the resolve request.
	 */
	tooltip?: string | MarkupContent;

	/**
	 * Render padding before the hint.
	 *
	 * Note: Padding should use the editor's background color, not the
	 * background color of the hint itself. That means padding can be used
	 * to visually align/separate an inlay hint.
	 */
	paddingLeft?: boolean;

	/**
	 * Render padding after the hint.
	 *
	 * Note: Padding should use the editor's background color, not the
	 * background color of the hint itself. That means padding can be used
	 * to visually align/separate an inlay hint.
	 */
	paddingRight?: boolean;


	/**
	 * A data entry field that is preserved on an inlay hint between
	 * a `textDocument/inlayHint` and an `inlayHint/resolve` request.
	 */
	data?: LSPAny;
}

/**
 * An inlay hint label part allows for interactive and composite labels
 * of inlay hints.
 *
 * @since 3.17.0
 */
export interface InlayHintLabelPart {

	/**
	 * The value of this label part.
	 */
	value: string;

	/**
	 * The tooltip text when you hover over this label part. Depending on
	 * the client capability `inlayHint.resolveSupport`, clients might resolve
	 * this property late using the resolve request.
	 */
	tooltip?: string | MarkupContent;

	/**
	 * An optional source code location that represents this
	 * label part.
	 *
	 * The editor will use this location for the hover and for code navigation
	 * features: This part will become a clickable link that resolves to the
	 * definition of the symbol at the given location (not necessarily the
	 * location itself), it shows the hover that shows at the given location,
	 * and it shows a context menu with further code navigation commands.
	 *
	 * Depending on the client capability `inlayHint.resolveSupport` clients
	 * might resolve this property late using the resolve request.
	 */
	location?: Location;

	/**
	 * An optional command for this label part.
	 *
	 * Depending on the client capability `inlayHint.resolveSupport`, clients
	 * might resolve this property late using the resolve request.
	 */
	command?: Command;
}

/**
 * Inlay hint kinds.
 *
 * @since 3.17.0
 */
export namespace InlayHintKind {

	/**
	 * An inlay hint that is for a type annotation.
	 */
	export const Type = 1;

	/**
	 * An inlay hint that is for a parameter.
	 */
	export const Parameter = 2;
}

export type InlayHintKind = 1 | 2;

textDocument.inlayHint.resolveSupport = { properties: ['label.location'] };

/**
 * Client workspace capabilities specific to inlay hints.
 *
 * @since 3.17.0
 */
export interface InlayHintWorkspaceClientCapabilities {
	/**
	 * Whether the client implementation supports a refresh request sent from
	 * the server to the client.
	 *
	 * Note that this event is global and will force the client to refresh all
	 * inlay hints currently shown. It should be used with absolute care and
	 * is useful for situations where a server, for example, detects a project wide
	 * change that requires such a calculation.
	 */
	refreshSupport?: boolean;
}


/* source file: "language/inlineValue.md" */

/**
 * Client capabilities specific to inline values.
 *
 * @since 3.17.0
 */
export interface InlineValueClientCapabilities {
	/**
	 * Whether the implementation supports dynamic registration for inline
	 * value providers.
	 */
	dynamicRegistration?: boolean;
}

/**
 * Inline value options used during static registration.
 *
 * @since 3.17.0
 */
export interface InlineValueOptions extends WorkDoneProgressOptions {
}

/**
 * Inline value options used during static or dynamic registration.
 *
 * @since 3.17.0
 */
export interface InlineValueRegistrationOptions extends InlineValueOptions,
	TextDocumentRegistrationOptions, StaticRegistrationOptions {
}

/**
 * A parameter literal used in inline value requests.
 *
 * @since 3.17.0
 */
export interface InlineValueParams extends WorkDoneProgressParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The document range for which inline values should be computed.
	 */
	range: Range;

	/**
	 * Additional information about the context in which inline values were
	 * requested.
	 */
	context: InlineValueContext;
}

/**
 * @since 3.17.0
 */
export interface InlineValueContext {
	/**
	 * The stack frame (as a DAP ID) where the execution has stopped.
	 */
	frameId: integer;

	/**
	 * The document range where execution has stopped.
	 * Typically, the end position of the range denotes the line where the
	 * inline values are shown.
	 */
	stoppedLocation: Range;
}

/**
 * Provide inline value as text.
 *
 * @since 3.17.0
 */
export interface InlineValueText {
	/**
	 * The document range for which the inline value applies.
	 */
	range: Range;

	/**
	 * The text of the inline value.
	 */
	text: string;
}

/**
 * Provide inline value through a variable lookup.
 *
 * If only a range is specified, the variable name will be extracted from
 * the underlying document.
 *
 * An optional variable name can be used to override the extracted name.
 *
 * @since 3.17.0
 */
export interface InlineValueVariableLookup {
	/**
	 * The document range for which the inline value applies.
	 * The range is used to extract the variable name from the underlying
	 * document.
	 */
	range: Range;

	/**
	 * If specified, the name of the variable to look up.
	 */
	variableName?: string;

	/**
	 * How to perform the lookup.
	 */
	caseSensitiveLookup: boolean;
}

/**
 * Provide an inline value through an expression evaluation.
 *
 * If only a range is specified, the expression will be extracted from the
 * underlying document.
 *
 * An optional expression can be used to override the extracted expression.
 *
 * @since 3.17.0
 */
export interface InlineValueEvaluatableExpression {
	/**
	 * The document range for which the inline value applies.
	 * The range is used to extract the evaluatable expression from the
	 * underlying document.
	 */
	range: Range;

	/**
	 * If specified the expression overrides the extracted expression.
	 */
	expression?: string;
}

/**
 * Inline value information can be provided by different means:
 * - directly as a text value (class InlineValueText).
 * - as a name to use for a variable lookup (class InlineValueVariableLookup)
 * - as an evaluatable expression (class InlineValueEvaluatableExpression)
 * The InlineValue types combines all inline value types into one type.
 *
 * @since 3.17.0
 */
export type InlineValue = InlineValueText | InlineValueVariableLookup
	| InlineValueEvaluatableExpression;

/**
 * Client workspace capabilities specific to inline values.
 *
 * @since 3.17.0
 */
export interface InlineValueWorkspaceClientCapabilities {
	/**
	 * Whether the client implementation supports a refresh request sent from
	 * the server to the client.
	 *
	 * Note that this event is global and will force the client to refresh all
	 * inline values currently shown. It should be used with absolute care and
	 * is useful for situations where a server, for example, detects a project
	 * wide change that requires such a calculation.
	 */
	refreshSupport?: boolean;
}


/* source file: "language/moniker.md" */

interface MonikerClientCapabilities {
	/**
	 * Whether implementation supports dynamic registration. If this is set to
	 * `true`, the client supports the new `(TextDocumentRegistrationOptions &
	 * StaticRegistrationOptions)` return value for the corresponding server
	 * capability as well.
	 */
	dynamicRegistration?: boolean;
}

export interface MonikerOptions extends WorkDoneProgressOptions {
}

export interface MonikerRegistrationOptions extends
	TextDocumentRegistrationOptions, MonikerOptions {
}

export interface MonikerParams extends TextDocumentPositionParams,
	WorkDoneProgressParams, PartialResultParams {
}

/**
 * Moniker uniqueness level to define scope of the moniker.
 */
export enum UniquenessLevel {
	/**
	 * The moniker is only unique inside a document.
	 */
	document = 'document',

	/**
	 * The moniker is unique inside a project for which a dump got created.
	 */
	project = 'project',

	/**
	 * The moniker is unique inside the group to which a project belongs.
	 */
	group = 'group',

	/**
	 * The moniker is unique inside the moniker scheme.
	 */
	scheme = 'scheme',

	/**
	 * The moniker is globally unique.
	 */
	global = 'global'
}

/**
 * The moniker kind.
 */
export enum MonikerKind {
	/**
	 * The moniker represent a symbol that is imported into a project.
	 */
	import = 'import',

	/**
	 * The moniker represents a symbol that is exported from a project.
	 */
	export = 'export',

	/**
	 * The moniker represents a symbol that is local to a project (e.g. a local
	 * variable of a function, a class not visible outside the project, ...)
	 */
	local = 'local'
}

/**
 * Moniker definition to match LSIF 0.5 moniker definition.
 */
export interface Moniker {
	/**
	 * The scheme of the moniker. For example, `tsc` or `.NET`.
	 */
	scheme: string;

	/**
	 * The identifier of the moniker. The value is opaque in LSIF, however
	 * schema owners are allowed to define the structure if they want.
	 */
	identifier: string;

	/**
	 * The scope in which the moniker is unique.
	 */
	unique: UniquenessLevel;

	/**
	 * The moniker kind if known.
	 */
	kind?: MonikerKind;
}


/* source file: "language/completion.md" */

export interface CompletionClientCapabilities {
	/**
	 * Whether completion supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports the following `CompletionItem` specific
	 * capabilities.
	 */
	completionItem?: {
		/**
		 * Client supports snippets as insert text.
		 *
		 * A snippet can define tab stops and placeholders with `$1`, `$2`
		 * and `${3:foo}`. `$0` defines the final tab stop, it defaults to
		 * the end of the snippet. Placeholders with equal identifiers are
		 * linked, that is, typing in one will update others too.
		 */
		snippetSupport?: boolean;

		/**
		 * Client supports commit characters on a completion item.
		 */
		commitCharactersSupport?: boolean;

		/**
		 * Client supports these content formats for the documentation
		 * property. The order describes the preferred format of the client.
		 */
		documentationFormat?: MarkupKind[];

		/**
		 * Client supports the deprecated property on a completion item.
		 */
		deprecatedSupport?: boolean;

		/**
		 * Client supports the preselect property on a completion item.
		 */
		preselectSupport?: boolean;

		/**
		 * Client supports the tag property on a completion item. Clients
		 * supporting tags have to handle unknown tags gracefully. Clients
		 * especially need to preserve unknown tags when sending a completion
		 * item back to the server in a resolve call.
		 *
		 * @since 3.15.0
		 */
		tagSupport?: {
			/**
			 * The tags supported by the client.
			 */
			valueSet: CompletionItemTag[];
		};

		/**
		 * Client supports insert replace edit to control different behavior if
		 * a completion item is inserted in the text or should replace text.
		 *
		 * @since 3.16.0
		 */
		insertReplaceSupport?: boolean;

		/**
		 * Indicates which properties a client can resolve lazily on a
		 * completion item. Before version 3.16.0, only the predefined properties
		 * `documentation` and `detail` could be resolved lazily.
		 *
		 * @since 3.16.0
		 */
		resolveSupport?: {
			/**
			 * The properties that a client can resolve lazily.
			 */
			properties: string[];
		};

		/**
		 * The client supports the `insertTextMode` property on
		 * a completion item to override the whitespace handling mode
		 * as defined by the client (see `insertTextMode`).
		 *
		 * @since 3.16.0
		 */
		insertTextModeSupport?: {
			valueSet: InsertTextMode[];
		};

		/**
		 * The client has support for completion item label
		 * details (see also `CompletionItemLabelDetails`).
		 *
		 * @since 3.17.0
		 */
		labelDetailsSupport?: boolean;
	};

	completionItemKind?: {
		/**
		 * The completion item kind values the client supports. When this
		 * property exists, the client also guarantees that it will
		 * handle values outside its set gracefully and falls back
		 * to a default value when unknown.
		 *
		 * If this property is not present, the client only supports
		 * the completion item kinds from `Text` to `Reference` as defined in
		 * the initial version of the protocol.
		 */
		valueSet?: CompletionItemKind[];
	};

	/**
	 * The client supports sending additional context information for a
	 * `textDocument/completion` request.
	 */
	contextSupport?: boolean;

	/**
	 * The client's default when the completion item doesn't provide an
	 * `insertTextMode` property.
	 *
	 * @since 3.17.0
	 */
	insertTextMode?: InsertTextMode;

	/**
	 * The client supports the following `CompletionList` specific
	 * capabilities.
	 *
	 * @since 3.17.0
	 */
	completionList?: {
		/**
		 * The client supports the following itemDefaults on
		 * a completion list.
		 *
		 * The value lists the supported property names of the
		 * `CompletionList.itemDefaults` object. If omitted,
		 * no properties are supported.
		 *
		 * @since 3.17.0
		 */
		itemDefaults?: string[];

		/**
		 * Specifies whether the client supports `CompletionList.applyKind` to
		 * indicate how supported values from `completionList.itemDefaults`
		 * and `completion` will be combined.
		 *
		 * If a client supports `applyKind` it must support it for all fields
		 * that it supports that are listed in `CompletionList.applyKind`. This
		 * means when clients add support for new/future fields in completion
		 * items the MUST also support merge for them if those fields are
		 * defined in `CompletionList.applyKind`.
		 *
		 * @since 3.18.0
		 */
		applyKindSupport?: boolean;
	}
}

/**
 * Completion options.
 */
export interface CompletionOptions extends WorkDoneProgressOptions {
	/**
	 * Most tools trigger completion request automatically without explicitly
	 * requesting it using a keyboard shortcut (e.g., Ctrl+Space). Typically they
	 * do so when the user starts to type an identifier. For example, if the user
	 * types `c` in a JavaScript file, code complete will automatically pop up and
	 * present `console` besides others as a completion item. Characters that
	 * make up identifiers don't need to be listed here.
	 *
	 * If code complete should automatically be triggered on characters not being
	 * valid inside an identifier (for example, `.` in JavaScript), list them in
	 * `triggerCharacters`.
	 */
	triggerCharacters?: string[];

	/**
	 * The list of all possible characters that commit a completion. This field
	 * can be used if clients don't support individual commit characters per
	 * completion item. See client capability
	 * `completion.completionItem.commitCharactersSupport`.
	 *
	 * If a server provides both `allCommitCharacters` and commit characters on
	 * an individual completion item, the ones on the completion item win.
	 *
	 * @since 3.2.0
	 */
	allCommitCharacters?: string[];

	/**
	 * The server provides support to resolve additional
	 * information for a completion item.
	 */
	resolveProvider?: boolean;

	/**
	 * The server supports the following `CompletionItem` specific
	 * capabilities.
	 *
	 * @since 3.17.0
	 */
	completionItem?: {
		/**
		 * The server has support for completion item label
		 * details (see also `CompletionItemLabelDetails`) when receiving
		 * a completion item in a resolve call.
		 *
		 * @since 3.17.0
		 */
		labelDetailsSupport?: boolean;
	}
}

export interface CompletionRegistrationOptions
	extends TextDocumentRegistrationOptions, CompletionOptions {
}

export interface CompletionParams extends TextDocumentPositionParams,
	WorkDoneProgressParams, PartialResultParams {
	/**
	 * The completion context. This is only available if the client specifies
	 * to send this using the client capability
	 * `completion.contextSupport === true`
	 */
	context?: CompletionContext;
}

/**
 * How a completion was triggered.
 */
export namespace CompletionTriggerKind {
	/**
	 * Completion was triggered by typing an identifier (automatic code
	 * complete), manual invocation (e.g. Ctrl+Space) or via API.
	 */
	export const Invoked: 1 = 1;

	/**
	 * Completion was triggered by a trigger character specified by
	 * the `triggerCharacters` properties of the
	 * `CompletionRegistrationOptions`.
	 */
	export const TriggerCharacter: 2 = 2;

	/**
	 * Completion was re-triggered as the current completion list is incomplete.
	 */
	export const TriggerForIncompleteCompletions: 3 = 3;
}
export type CompletionTriggerKind = 1 | 2 | 3;

/**
 * Contains additional information about the context in which a completion
 * request is triggered.
 */
export interface CompletionContext {
	/**
	 * How the completion was triggered.
	 */
	triggerKind: CompletionTriggerKind;

	/**
	 * The trigger character (a single character) that
	 * has triggered code complete. Is undefined if
	 * `triggerKind !== CompletionTriggerKind.TriggerCharacter`
	 */
	triggerCharacter?: string;
}

/**
 * Represents a collection of [completion items](#CompletionItem) to be
 * presented in the editor.
 */
export interface CompletionList {
	/**
	 * This list is not complete. Further typing should result in recomputing
	 * this list.
	 *
	 * Recomputed lists have all their items replaced (not appended) in the
	 * incomplete completion sessions.
	 */
	isIncomplete: boolean;

	/**
	 * In many cases, the items of an actual completion result share the same
	 * value for properties like `commitCharacters` or the range of a text
	 * edit. A completion list can therefore define item defaults which will
	 * be used if a completion item itself doesn't specify the value.
	 *
	 * If a completion list specifies a default value and a completion item
	 * also specifies a corresponding value, the rules for combining these are
	 * defined by `applyKinds` (if the client supports it), defaulting to
	 * ApplyKind.Replace.
	 *
	 * Servers are only allowed to return default values if the client
	 * signals support for this via the `completionList.itemDefaults`
	 * capability.
	 *
	 * @since 3.17.0
	 */
	itemDefaults?: {
		/**
		 * A default commit character set.
		 *
		 * @since 3.17.0
		 */
		commitCharacters?: string[];

		/**
		 * A default edit range.
		 *
		 * @since 3.17.0
		 */
		editRange?: Range | {
			insert: Range;
			replace: Range;
		};

		/**
		 * A default insert text format.
		 *
		 * @since 3.17.0
		 */
		insertTextFormat?: InsertTextFormat;

		/**
		 * A default insert text mode.
		 *
		 * @since 3.17.0
		 */
		insertTextMode?: InsertTextMode;

		/**
		 * A default data value.
		 *
		 * @since 3.17.0
		 */
		data?: LSPAny;
	}

	/**
	 * Specifies how fields from a completion item should be combined with those
	 * from `completionList.itemDefaults`.
	 *
	 * If unspecified, all fields will be treated as ApplyKind.Replace.
	 *
	 * If a field's value is ApplyKind.Replace, the value from a completion item
	 * (if provided and not `null`) will always be used instead of the value
	 * from `completionItem.itemDefaults`.
	 *
	 * If a field's value is ApplyKind.Merge, the values will be merged using
	 * the rules defined against each field below.
	 *
	 * Servers are only allowed to return `applyKind` if the client
	 * signals support for this via the `completionList.applyKindSupport`
	 * capability.
	 *
	 * @since 3.18.0
	 */
	applyKind?: {
		/**
		 * Specifies whether commitCharacters on a completion will replace or be
		 * merged with those in `completionList.itemDefaults.commitCharacters`.
		 *
		 * If ApplyKind.Replace, the commit characters from the completion item
		 * will always be used unless not provided, in which case those from
		 * `completionList.itemDefaults.commitCharacters` will be used. An
		 * empty list can be used if a completion item does not have any commit
		 * characters and also should not use those from
		 * `completionList.itemDefaults.commitCharacters`.
		 *
		 * If ApplyKind.Merge the commitCharacters for the completion will be
		 * the union of all values in both
		 * `completionList.itemDefaults.commitCharacters` and the completion's
		 * own `commitCharacters`.
		 *
		 * @since 3.18.0
		 */
		commitCharacters?: ApplyKind;

		/**
		 * Specifies whether the `data` field on a completion will replace or
		 * be merged with data from `completionList.itemDefaults.data`.
		 *
		 * If ApplyKind.Replace, the data from the completion item will be used
		 * if provided (and not `null`), otherwise
		 * `completionList.itemDefaults.data` will be used. An empty object can
		 * be used if a completion item does not have any data but also should
		 * not use the value from `completionList.itemDefaults.data`.
		 *
		 * If ApplyKind.Merge, a shallow merge will be performed between
		 * `completionList.itemDefaults.data` and the completion's own data
		 * using the following rules:
		 *
		 * - If a completion's `data` field is not provided (or `null`), the
		 *   entire `data` field from `completionList.itemDefaults.data` will be
		 *   used as-is.
		 * - If a completion's `data` field is provided, each field will
		 *   overwrite the field of the same name in
		 *   `completionList.itemDefaults.data` but no merging of nested fields
		 *   within that value will occur.
		 *
		 * @since 3.18.0
		 */
		data?: ApplyKind;
	}

	/**
	 * The completion items.
	 */
	items: CompletionItem[];
}

/**
 * Defines whether the insert text in a completion item should be interpreted as
 * plain text or a snippet.
 */
export namespace InsertTextFormat {
	/**
	 * The primary text to be inserted is treated as a plain string.
	 */
	export const PlainText = 1;

	/**
	 * The primary text to be inserted is treated as a snippet.
	 *
	 * A snippet can define tab stops and placeholders with `$1`, `$2`
	 * and `${3:foo}`. `$0` defines the final tab stop, it defaults to
	 * the end of the snippet. Placeholders with equal identifiers are linked,
	 * that is, typing in one will update others too.
	 */
	export const Snippet = 2;
}

export type InsertTextFormat = 1 | 2;

/**
 * Completion item tags are extra annotations that tweak the rendering of a
 * completion item.
 *
 * @since 3.15.0
 */
export namespace CompletionItemTag {
	/**
	 * Render a completion as obsolete, usually using a strike-out.
	 */
	export const Deprecated = 1;
}

export type CompletionItemTag = 1;

/**
 * A special text edit to provide an insert and a replace operation.
 *
 * @since 3.16.0
 */
export interface InsertReplaceEdit {
	/**
	 * The string to be inserted.
	 */
	newText: string;

	/**
	 * The range if the insert is requested.
	 */
	insert: Range;

	/**
	 * The range if the replace is requested.
	 */
	replace: Range;
}

/**
 * How whitespace and indentation is handled during completion
 * item insertion.
 *
 * @since 3.16.0
 */
export namespace InsertTextMode {
	/**
	 * The insertion or replace strings are taken as-is. If the
	 * value is multiline, the lines below the cursor will be
	 * inserted using the indentation defined in the string value.
	 * The client will not apply any kind of adjustments to the
	 * string.
	 */
	export const asIs: 1 = 1;

	/**
	 * The editor adjusts leading whitespace of new lines so that
	 * they match the indentation up to the cursor of the line for
	 * which the item is accepted.
	 *
	 * Consider a line like this: <2tabs><cursor><3tabs>foo. Accepting a
	 * multi line completion item is indented using 2 tabs and all
	 * following lines inserted will be indented using 2 tabs as well.
	 */
	export const adjustIndentation: 2 = 2;
}

export type InsertTextMode = 1 | 2;

/**
 * Additional details for a completion item label.
 *
 * @since 3.17.0
 */
export interface CompletionItemLabelDetails {

	/**
	 * An optional string which is rendered less prominently directly after
	 * {@link CompletionItem.label label}, without any spacing. Should be
	 * used for function signatures or type annotations.
	 */
	detail?: string;

	/**
	 * An optional string which is rendered less prominently after
	 * {@link CompletionItemLabelDetails.detail}. Should be used for fully qualified
	 * names or file paths.
	 */
	description?: string;
}

/**
 * Defines how values from a set of defaults and an individual item will be
 * merged.
 *
 * @since 3.18.0
 */
export namespace ApplyKind {
	/**
	 * The value from the individual item (if provided and not `null`) will be
	 * used instead of the default.
	 */
	export const Replace: 1 = 1;

	/**
	 * The value from the item will be merged with the default.
	 *
	 * The specific rules for mergeing values are defined against each field
	 * that supports merging.
	 */
	export const Merge: 2 = 2;
}

/**
 * Defines how values from a set of defaults and an individual item will be
 * merged.
 *
 * @since 3.18.0
 */
export type ApplyKind = 1 | 2;

export interface CompletionItem {

	/**
	 * The label of this completion item.
	 *
	 * The label property is also by default the text that
	 * is inserted when selecting this completion.
	 *
	 * If label details are provided, the label itself should
	 * be an unqualified name of the completion item.
	 */
	label: string;

	/**
	 * Additional details for the label.
	 *
	 * @since 3.17.0
	 */
	labelDetails?: CompletionItemLabelDetails;

	/**
	 * The kind of this completion item. Based on the kind,
	 * an icon is chosen by the editor. The standardized set
	 * of available values is defined in `CompletionItemKind`.
	 */
	kind?: CompletionItemKind;

	/**
	 * Tags for this completion item.
	 *
	 * @since 3.15.0
	 */
	tags?: CompletionItemTag[];

	/**
	 * A human-readable string with additional information
	 * about this item, like type or symbol information.
	 */
	detail?: string;

	/**
	 * A human-readable string that represents a doc-comment.
	 */
	documentation?: string | MarkupContent;

	/**
	 * Indicates if this item is deprecated.
	 *
	 * @deprecated Use `tags` instead if supported.
	 */
	deprecated?: boolean;

	/**
	 * Select this item when showing.
	 *
	 * *Note* that only one completion item can be selected and that the
	 * tool / client decides which item that is. The rule is that the *first*
	 * item of those that match best is selected.
	 */
	preselect?: boolean;

	/**
	 * A string that should be used when comparing this item
	 * with other items. When omitted, the label is used
	 * as the sort text for this item.
	 */
	sortText?: string;

	/**
	 * A string that should be used when filtering a set of
	 * completion items. When omitted, the label is used as the
	 * filter text for this item.
	 */
	filterText?: string;

	/**
	 * A string that should be inserted into a document when selecting
	 * this completion. When omitted, the label is used as the insert text
	 * for this item.
	 *
	 * The `insertText` is subject to interpretation by the client side.
	 * Some tools might not take the string literally. For example,
	 * when code complete is requested for `con<cursor position>`
	 * and a completion item with an `insertText` of `console` is provided,
	 * VSCode will only insert `sole`. Therefore, it is
	 * recommended to use `textEdit` instead since it avoids additional client
	 * side interpretation.
	 */
	insertText?: string;

	/**
	 * The format of the insert text. The format applies to both the
	 * `insertText` property and the `newText` property of a provided
	 * `textEdit`. If omitted, defaults to `InsertTextFormat.PlainText`.
	 *
	 * Please note that the insertTextFormat doesn't apply to
	 * `additionalTextEdits`.
	 */
	insertTextFormat?: InsertTextFormat;

	/**
	 * How whitespace and indentation is handled during completion
	 * item insertion. If not provided, the client's default value depends on
	 * the `textDocument.completion.insertTextMode` client capability.
	 *
	 * @since 3.16.0
	 * @since 3.17.0 - support for `textDocument.completion.insertTextMode`
	 */
	insertTextMode?: InsertTextMode;

	/**
	 * An edit which is applied to a document when selecting this completion.
	 * When an edit is provided, the value of `insertText` is ignored.
	 *
	 * *Note:* The range of the edit must be a single line range and it must
	 * contain the position at which completion has been requested. Despite this
	 * limitation, your edit can write multiple lines.
	 *
	 * Most editors support two different operations when accepting a completion
	 * item. One is to insert a completion text and the other is to replace an
	 * existing text with a completion text. Since this can usually not be
	 * predetermined by a server it can report both ranges. Clients need to
	 * signal support for `InsertReplaceEdit`s via the
	 * `textDocument.completion.completionItem.insertReplaceSupport` client
	 * capability property.
	 *
	 * *Note 1:* The text edit's range as well as both ranges from an insert
	 * replace edit must be a single line and they must contain the position
	 * at which completion has been requested. In both cases, the new text can
	 * consist of multiple lines.
	 * *Note 2:* If an `InsertReplaceEdit` is returned, the edit's insert range
	 * must be a prefix of the edit's replace range, meaning it must be
	 * contained in and starting at the same position.
	 *
	 * @since 3.16.0 additional type `InsertReplaceEdit`
	 */
	textEdit?: TextEdit | InsertReplaceEdit;

	/**
	 * The edit text used if the completion item is part of a CompletionList and
	 * CompletionList defines an item default for the text edit range.
	 *
	 * Clients will only honor this property if they opt into completion list
	 * item defaults using the capability `completionList.itemDefaults`.
	 *
	 * If not provided and a list's default range is provided, the label
	 * property is used as a text.
	 *
	 * @since 3.17.0
	 */
	textEditText?: string;

	/**
	 * An optional array of additional text edits that are applied when
	 * selecting this completion. Edits must not overlap (including the same
	 * insert position) with the main edit nor with themselves.
	 *
	 * Additional text edits should be used to change text unrelated to the
	 * current cursor position (for example adding an import statement at the
	 * top of the file if the completion item will insert an unqualified type).
	 */
	additionalTextEdits?: TextEdit[];

	/**
	 * An optional set of characters that, when pressed while this completion is
	 * active, will accept it first and then type that character. *Note* that all
	 * commit characters should have `length=1` and that superfluous characters
	 * will be ignored.
	 */
	commitCharacters?: string[];

	/**
	 * An optional command that is executed *after* inserting this completion.
	 * *Note* that additional modifications to the current document should be
	 * described with the additionalTextEdits-property.
	 */
	command?: Command;

	/**
	 * A data entry field that is preserved on a completion item between
	 * a completion and a completion resolve request.
	 */
	data?: LSPAny;
}

/**
 * The kind of a completion entry.
 */
export namespace CompletionItemKind {
	export const Text = 1;
	export const Method = 2;
	export const Function = 3;
	export const Constructor = 4;
	export const Field = 5;
	export const Variable = 6;
	export const Class = 7;
	export const Interface = 8;
	export const Module = 9;
	export const Property = 10;
	export const Unit = 11;
	export const Value = 12;
	export const Enum = 13;
	export const Keyword = 14;
	export const Snippet = 15;
	export const Color = 16;
	export const File = 17;
	export const Reference = 18;
	export const Folder = 19;
	export const EnumMember = 20;
	export const Constant = 21;
	export const Struct = 22;
	export const Event = 23;
	export const Operator = 24;
	export const TypeParameter = 25;
}

export type CompletionItemKind = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25;






/* source file: "language/publishDiagnostics.md" */

export interface PublishDiagnosticsClientCapabilities {
	/**
	 * Whether the clients accepts diagnostics with related information.
	 */
	relatedInformation?: boolean;

	/**
	 * Client supports the tag property to provide meta data about a diagnostic.
	 * Clients supporting tags have to handle unknown tags gracefully.
	 *
	 * @since 3.15.0
	 */
	tagSupport?: {
		/**
		 * The tags supported by the client.
		 */
		valueSet: DiagnosticTag[];
	};

	/**
	 * Whether the client interprets the version property of the
	 * `textDocument/publishDiagnostics` notification's parameter.
	 *
	 * @since 3.15.0
	 */
	versionSupport?: boolean;

	/**
	 * Client supports a codeDescription property.
	 *
	 * @since 3.16.0
	 */
	codeDescriptionSupport?: boolean;

	/**
	 * Whether code action supports the `data` property which is
	 * preserved between a `textDocument/publishDiagnostics` and
	 * `textDocument/codeAction` request.
	 *
	 * @since 3.16.0
	 */
	dataSupport?: boolean;
}

interface PublishDiagnosticsParams {
	/**
	 * The URI for which diagnostic information is reported.
	 */
	uri: DocumentUri;

	/**
	 * Optionally, the version number of the document the diagnostics are
	 * published for.
	 *
	 * @since 3.15.0
	 */
	version?: integer;

	/**
	 * An array of diagnostic information items.
	 */
	diagnostics: Diagnostic[];
}


/* source file: "language/pullDiagnostics.md" */

/**
 * Client capabilities specific to diagnostic pull requests.
 *
 * @since 3.17.0
 */
export interface DiagnosticClientCapabilities {
	/**
	 * Whether implementation supports dynamic registration. If this is set to
	 * `true`, the client supports the new
	 * `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
	 * return value for the corresponding server capability as well.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Whether the clients supports related documents for document diagnostic
	 * pulls.
	 */
	relatedDocumentSupport?: boolean;

	/**
	 * Whether the client supports `MarkupContent` in diagnostic messages.
	 * 
	 * @since 3.18.0
	 * @proposed
	 */
	markupMessageSupport?: boolean;
}

/**
 * Diagnostic options.
 *
 * @since 3.17.0
 */
export interface DiagnosticOptions extends WorkDoneProgressOptions {
	/**
	 * An optional identifier under which the diagnostics are
	 * managed by the client.
	 */
	identifier?: string;

	/**
	 * Whether the language has inter file dependencies, meaning that
	 * editing code in one file can result in a different diagnostic
	 * set in another file. Inter file dependencies are common for
	 * most programming languages and typically uncommon for linters.
	 */
	interFileDependencies: boolean;

	/**
	 * The server provides support for workspace diagnostics as well.
	 */
	workspaceDiagnostics: boolean;
}

/**
 * Diagnostic registration options.
 *
 * @since 3.17.0
 */
export interface DiagnosticRegistrationOptions extends
	TextDocumentRegistrationOptions, DiagnosticOptions,
	StaticRegistrationOptions {
}

/**
 * Parameters of the document diagnostic request.
 *
 * @since 3.17.0
 */
export interface DocumentDiagnosticParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The additional identifier  provided during registration.
	 */
	identifier?: string;

	/**
	 * The result ID of a previous response, if provided.
	 */
	previousResultId?: string;
}

/**
 * The result of a document diagnostic pull request. A report can
 * either be a full report, containing all diagnostics for the
 * requested document, or an unchanged report, indicating that nothing
 * has changed in terms of diagnostics in comparison to the last
 * pull request.
 *
 * @since 3.17.0
 */
export type DocumentDiagnosticReport = RelatedFullDocumentDiagnosticReport
	| RelatedUnchangedDocumentDiagnosticReport;

/**
 * The document diagnostic report kinds.
 *
 * @since 3.17.0
 */
export namespace DocumentDiagnosticReportKind {
	/**
	 * A diagnostic report with a full
	 * set of problems.
	 */
	export const Full = 'full';

	/**
	 * A report indicating that the last
	 * returned report is still accurate.
	 */
	export const Unchanged = 'unchanged';
}

export type DocumentDiagnosticReportKind = 'full' | 'unchanged';

/**
 * A diagnostic report with a full set of problems.
 *
 * @since 3.17.0
 */
export interface FullDocumentDiagnosticReport {
	/**
	 * A full document diagnostic report.
	 */
	kind: DocumentDiagnosticReportKind.Full;

	/**
	 * An optional result ID. If provided, it will
	 * be sent on the next diagnostic request for the
	 * same document.
	 */
	resultId?: string;

	/**
	 * The actual items.
	 */
	items: Diagnostic[];
}

/**
 * A diagnostic report indicating that the last returned
 * report is still accurate.
 *
 * @since 3.17.0
 */
export interface UnchangedDocumentDiagnosticReport {
	/**
	 * A document diagnostic report indicating
	 * no changes to the last result. A server can
	 * only return `unchanged` if result IDs are
	 * provided.
	 */
	kind: DocumentDiagnosticReportKind.Unchanged;

	/**
	 * A result ID which will be sent on the next
	 * diagnostic request for the same document.
	 */
	resultId: string;
}

/**
 * A full diagnostic report with a set of related documents.
 *
 * @since 3.17.0
 */
export interface RelatedFullDocumentDiagnosticReport extends
	FullDocumentDiagnosticReport {
	/**
	 * Diagnostics of related documents. This information is useful
	 * in programming languages where code in a file A can generate
	 * diagnostics in a file B which A depends on. An example of
	 * such a language is C/C++, where macro definitions in a file
	 * a.cpp can result in errors in a header file b.hpp.
	 *
	 * @since 3.17.0
	 */
	relatedDocuments?: {
		[uri: string /** DocumentUri */]:
			FullDocumentDiagnosticReport | UnchangedDocumentDiagnosticReport;
	};
}

/**
 * An unchanged diagnostic report with a set of related documents.
 *
 * @since 3.17.0
 */
export interface RelatedUnchangedDocumentDiagnosticReport extends
	UnchangedDocumentDiagnosticReport {
	/**
	 * Diagnostics of related documents. This information is useful
	 * in programming languages where code in a file A can generate
	 * diagnostics in a file B which A depends on. An example of
	 * such a language is C/C++, where macro definitions in a file
	 * a.cpp can result in errors in a header file b.hpp.
	 *
	 * @since 3.17.0
	 */
	relatedDocuments?: {
		[uri: string /** DocumentUri */]:
			FullDocumentDiagnosticReport | UnchangedDocumentDiagnosticReport;
	};
}

/**
 * A partial result for a document diagnostic report.
 *
 * @since 3.17.0
 */
export interface DocumentDiagnosticReportPartialResult {
	relatedDocuments: {
		[uri: string /** DocumentUri */]:
			FullDocumentDiagnosticReport | UnchangedDocumentDiagnosticReport;
	};
}

/**
 * Cancellation data returned from a diagnostic request.
 *
 * @since 3.17.0
 */
export interface DiagnosticServerCancellationData {
	retriggerRequest: boolean;
}

/**
 * Parameters of the workspace diagnostic request.
 *
 * @since 3.17.0
 */
export interface WorkspaceDiagnosticParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The additional identifier provided during registration.
	 */
	identifier?: string;

	/**
	 * The currently known diagnostic reports with their
	 * previous result IDs.
	 */
	previousResultIds: PreviousResultId[];
}

/**
 * A previous result ID in a workspace pull request.
 *
 * @since 3.17.0
 */
export interface PreviousResultId {
	/**
	 * The URI for which the client knows a
	 * result ID.
	 */
	uri: DocumentUri;

	/**
	 * The value of the previous result ID.
	 */
	value: string;
}

/**
 * A workspace diagnostic report.
 *
 * @since 3.17.0
 */
export interface WorkspaceDiagnosticReport {
	items: WorkspaceDocumentDiagnosticReport[];
}

/**
 * A full document diagnostic report for a workspace diagnostic result.
 *
 * @since 3.17.0
 */
export interface WorkspaceFullDocumentDiagnosticReport extends
	FullDocumentDiagnosticReport {

	/**
	 * The URI for which diagnostic information is reported.
	 */
	uri: DocumentUri;

	/**
	 * The version number for which the diagnostics are reported.
	 * If the document is not marked as open, `null` can be provided.
	 */
	version: integer | null;
}

/**
 * An unchanged document diagnostic report for a workspace diagnostic result.
 *
 * @since 3.17.0
 */
export interface WorkspaceUnchangedDocumentDiagnosticReport extends
	UnchangedDocumentDiagnosticReport {

	/**
	 * The URI for which diagnostic information is reported.
	 */
	uri: DocumentUri;

	/**
	 * The version number for which the diagnostics are reported.
	 * If the document is not marked as open, `null` can be provided.
	 */
	version: integer | null;
};

/**
 * A workspace diagnostic document report.
 *
 * @since 3.17.0
 */
export type WorkspaceDocumentDiagnosticReport =
	WorkspaceFullDocumentDiagnosticReport
	| WorkspaceUnchangedDocumentDiagnosticReport;

/**
 * A partial result for a workspace diagnostic report.
 *
 * @since 3.17.0
 */
export interface WorkspaceDiagnosticReportPartialResult {
	items: WorkspaceDocumentDiagnosticReport[];
}

/**
 * Workspace client capabilities specific to diagnostic pull requests.
 *
 * @since 3.17.0
 */
export interface DiagnosticWorkspaceClientCapabilities {
	/**
	 * Whether the client implementation supports a refresh request sent from
	 * the server to the client.
	 *
	 * Note that this event is global and will force the client to refresh all
	 * pulled diagnostics currently shown. It should be used with absolute care
	 * and is useful for situation where a server, for example, detects a project
	 * wide change that requires such a calculation.
	 */
	refreshSupport?: boolean;
}


/* source file: "language/signatureHelp.md" */

export interface SignatureHelpClientCapabilities {
	/**
	 * Whether signature help supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports the following `SignatureInformation`
	 * specific properties.
	 */
	signatureInformation?: {
		/**
		 * Client supports the following content formats for the documentation
		 * property. The order describes the preferred format of the client.
		 */
		documentationFormat?: MarkupKind[];

		/**
		 * Client capabilities specific to parameter information.
		 */
		parameterInformation?: {
			/**
			 * The client supports processing label offsets instead of a
			 * simple label string.
			 *
			 * @since 3.14.0
			 */
			labelOffsetSupport?: boolean;
		};

		/**
		 * The client supports the `activeParameter` property on
		 * `SignatureInformation` literal.
		 *
		 * @since 3.16.0
		 */
		activeParameterSupport?: boolean;

		/**
		 * The client supports the `activeParameter` property on
		 * `SignatureHelp`/`SignatureInformation` being set to `null` to
		 * indicate that no parameter should be active.
		 *
		 * @since 3.18.0
		 */
		noActiveParameterSupport?: boolean;

	};

	/**
	 * The client supports sending additional context information for a
	 * `textDocument/signatureHelp` request. A client that opts into
	 * contextSupport will also support the `retriggerCharacters` on
	 * `SignatureHelpOptions`.
	 *
	 * @since 3.15.0
	 */
	contextSupport?: boolean;
}

export interface SignatureHelpOptions extends WorkDoneProgressOptions {
	/**
	 * The characters that trigger signature help
	 * automatically.
	 */
	triggerCharacters?: string[];

	/**
	 * List of characters that re-trigger signature help.
	 *
	 * These trigger characters are only active when signature help is already
	 * showing. All trigger characters are also counted as re-trigger
	 * characters.
	 *
	 * @since 3.15.0
	 */
	retriggerCharacters?: string[];
}

export interface SignatureHelpRegistrationOptions
	extends TextDocumentRegistrationOptions, SignatureHelpOptions {
}

export interface SignatureHelpParams extends TextDocumentPositionParams,
	WorkDoneProgressParams {
	/**
	 * The signature help context. This is only available if the client
	 * specifies to send this using the client capability
	 * `textDocument.signatureHelp.contextSupport === true`
	 *
	 * @since 3.15.0
	 */
	context?: SignatureHelpContext;
}

/**
 * How a signature help was triggered.
 *
 * @since 3.15.0
 */
export namespace SignatureHelpTriggerKind {
	/**
	 * Signature help was invoked manually by the user or by a command.
	 */
	export const Invoked: 1 = 1;
	/**
	 * Signature help was triggered by a trigger character.
	 */
	export const TriggerCharacter: 2 = 2;
	/**
	 * Signature help was triggered by the cursor moving or by the document
	 * content changing.
	 */
	export const ContentChange: 3 = 3;
}
export type SignatureHelpTriggerKind = 1 | 2 | 3;

/**
 * Additional information about the context in which a signature help request
 * was triggered.
 *
 * @since 3.15.0
 */
export interface SignatureHelpContext {
	/**
	 * Action that caused signature help to be triggered.
	 */
	triggerKind: SignatureHelpTriggerKind;

	/**
	 * Character that caused signature help to be triggered.
	 *
	 * This is undefined when triggerKind !==
	 * SignatureHelpTriggerKind.TriggerCharacter
	 */
	triggerCharacter?: string;

	/**
	 * `true` if signature help was already showing when it was triggered.
	 *
	 * Retriggers occur when the signature help is already active and can be
	 * caused by actions such as typing a trigger character, a cursor move, or
	 * document content changes.
	 */
	isRetrigger: boolean;

	/**
	 * The currently active `SignatureHelp`.
	 *
	 * The `activeSignatureHelp` has its `SignatureHelp.activeSignature` field
	 * updated based on the user navigating through available signatures.
	 */
	activeSignatureHelp?: SignatureHelp;
}

/**
 * Signature help represents the signature of something
 * callable. There can be multiple signatures,
 * but only one active one and only one active parameter.
 */
export interface SignatureHelp {
	/**
	 * One or more signatures. If no signatures are available,
	 * the signature help request should return `null`.
	 */
	signatures: SignatureInformation[];

	/**
	 * The active signature. If omitted or the value lies outside the
	 * range of `signatures`, the value defaults to zero or is ignored if
	 * the `SignatureHelp` has no signatures.
	 *
	 * Whenever possible, implementers should make an active decision about
	 * the active signature and shouldn't rely on a default value.
	 *
	 * In future versions of the protocol, this property might become
	 * mandatory to better express this.
	 */
	activeSignature?: uinteger;

	/**
	 * The active parameter of the active signature.
	 *
	 * If `null`, no parameter of the signature is active (for example, a named
	 * argument that does not match any declared parameters). This is only valid
	 * since 3.18.0 and if the client specifies the client capability
	 * `textDocument.signatureHelp.noActiveParameterSupport === true`.
	 *
	 * If omitted or the value lies outside the range of
	 * `signatures[activeSignature].parameters`, it defaults to 0 if the active
	 * signature has parameters.
	 *
	 * If the active signature has no parameters, it is ignored.
	 *
	 * In future versions of the protocol this property might become
	 * mandatory (but still nullable) to better express the active parameter if
	 * the active signature does have any.
	 */
	activeParameter?: uinteger | null;
}

/**
 * Represents the signature of something callable. A signature
 * can have a label, like a function-name, a doc-comment, and
 * a set of parameters.
 */
export interface SignatureInformation {
	/**
	 * The label of this signature. Will be shown in the UI.
	 */
	label: string;

	/**
	 * The human-readable doc-comment of this signature.
     * Will be shown in the UI but can be omitted.
	 */
	documentation?: string | MarkupContent;

	/**
	 * The parameters of this signature.
	 */
	parameters?: ParameterInformation[];

	/**
	 * The index of the active parameter.
	 *
	 * If `null`, no parameter of the signature is active (for example, a named
	 * argument that does not match any declared parameters). This is only valid
	 * since 3.18.0 and if the client specifies the client capability
	 * `textDocument.signatureHelp.noActiveParameterSupport === true`.
	 *
	 * If provided (or `null`), this is used in place of
	 * `SignatureHelp.activeParameter`.
	 *
	 * @since 3.16.0
	 */
	activeParameter?: uinteger | null;
}

/**
 * Represents a parameter of a callable-signature. A parameter can
 * have a label and a doc-comment.
 */
export interface ParameterInformation {

	/**
	 * The label of this parameter information.
	 *
	 * Either a string or an inclusive start and exclusive end offset within
	 * its containing signature label (see SignatureInformation.label). The
	 * offsets are based on a UTF-16 string representation, as `Position` and
	 * `Range` do.
	 *
	 * To avoid ambiguities, a server should use the [start, end] offset value
	 * instead of using a substring. Whether a client support this is
	 * controlled via `labelOffsetSupport` client capability.
	 *
	 * *Note*: a label of type string should be a substring of its containing
	 * signature label. Its intended use case is to highlight the parameter
	 * label part in the `SignatureInformation.label`.
	 */
	label: string | [uinteger, uinteger];

	/**
	 * The human-readable doc-comment of this parameter. Will be shown
	 * in the UI but can be omitted.
	 */
	documentation?: string | MarkupContent;
}


/* source file: "language/codeAction.md" */

export interface CodeActionClientCapabilities {
	/**
	 * Whether code action supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * The client supports code action literals as a valid
	 * response of the `textDocument/codeAction` request.
	 *
	 * @since 3.8.0
	 */
	codeActionLiteralSupport?: {
		/**
		 * The code action kind is supported with the following value
		 * set.
		 */
		codeActionKind: {

			/**
			 * The code action kind values that the client supports. When this
			 * property exists, the client also guarantees that it will
			 * handle values outside its set gracefully and falls back
			 * to a default value when unknown.
			 */
			valueSet: CodeActionKind[];
		};
	};

	/**
	 * Whether code action supports the `isPreferred` property.
	 *
	 * @since 3.15.0
	 */
	isPreferredSupport?: boolean;

	/**
	 * Whether code action supports the `disabled` property.
	 *
	 * @since 3.16.0
	 */
	disabledSupport?: boolean;

	/**
	 * Whether code action supports the `data` property which is
	 * preserved between a `textDocument/codeAction` and a
	 * `codeAction/resolve` request.
	 *
	 * @since 3.16.0
	 */
	dataSupport?: boolean;

	/**
	 * Whether the client supports resolving additional code action
	 * properties via a separate `codeAction/resolve` request.
	 *
	 * @since 3.16.0
	 */
	resolveSupport?: {
		/**
		 * The properties that a client can resolve lazily.
		 */
		properties: string[];
	};

	/**
	 * Whether the client honors the change annotations in
	 * text edits and resource operations returned via the
	 * `CodeAction#edit` property by, for example, presenting
	 * the workspace edit in the user interface and asking
	 * for confirmation.
	 *
	 * @since 3.16.0
	 */
	honorsChangeAnnotations?: boolean;

	/**
	 * Whether the client supports documentation for a class of code actions.
	 *
	 * @since 3.18.0
	 * @proposed
	 */
	 documentationSupport?: boolean;

	/**
	 * Client supports the tag property on a code action. Clients
	 * supporting tags have to handle unknown tags gracefully.
	 *
	 * @since 3.18.0 - proposed
	 */
	tagSupport?: {
		/**
		 * The tags supported by the client.
		 */
		valueSet: CodeActionTag[];
	}; 
}

/**
 * Documentation for a class of code actions.
 *
 * @since 3.18.0
 * @proposed
 */
export interface CodeActionKindDocumentation {
	/**
	 * The kind of the code action being documented.
	 *
	 * If the kind is generic, such as `CodeActionKind.Refactor`, the
	 * documentation will be shown whenever any refactorings are returned. If
	 * the kind is more specific, such as `CodeActionKind.RefactorExtract`, the
	 * documentation will only be shown when extract refactoring code actions
	 * are returned.
	 */
	kind: CodeActionKind;

	/**
	 * Command that is used to display the documentation to the user.
	 *
	 * The title of this documentation code action is taken
	 * from {@linkcode Command.title}
	 */
	command: Command;
}

export interface CodeActionOptions extends WorkDoneProgressOptions {
	/**
	 * CodeActionKinds that this server may return.
	 *
	 * The list of kinds may be generic, such as `CodeActionKind.Refactor`,
	 * or the server may list out every specific kind they provide.
	 */
	codeActionKinds?: CodeActionKind[];

	/**
	 * Static documentation for a class of code actions.
	 *
	 * Documentation from the provider should be shown in the code actions
	 * menu if either:
	 *
	 * - Code actions of `kind` are requested by the editor. In this case,
	 *   the editor will show the documentation that most closely matches the
	 *   requested code action kind. For example, if a provider has
	 *   documentation for both `Refactor` and `RefactorExtract`, when the
	 *   user requests code actions for `RefactorExtract`, the editor will use
	 *   the documentation for `RefactorExtract` instead of the documentation
	 *   for `Refactor`.
	 *
	 * - Any code actions of `kind` are returned by the provider.
	 *
	 * At most one documentation entry should be shown per provider.
	 *
	 * @since 3.18.0
	 * @proposed
	 */
	documentation?: CodeActionKindDocumentation[];

	/**
	 * The server provides support to resolve additional
	 * information for a code action.
	 *
	 * @since 3.16.0
	 */
	resolveProvider?: boolean;
}

export interface CodeActionRegistrationOptions extends
	TextDocumentRegistrationOptions, CodeActionOptions {
}

/**
 * Params for the CodeActionRequest.
 */
export interface CodeActionParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The document in which the command was invoked.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The range for which the command was invoked.
	 */
	range: Range;

	/**
	 * Context carrying additional information.
	 */
	context: CodeActionContext;
}

/**
 * The kind of a code action.
 *
 * Kinds are a hierarchical list of identifiers separated by `.`,
 * e.g. `"refactor.extract.function"`.
 *
 * The set of kinds is open and the client needs to announce
 * the kinds it supports to the server during initialization.
 */
export type CodeActionKind = string;

/**
 * A set of predefined code action kinds.
 */
export namespace CodeActionKind {

	/**
	 * Empty kind.
	 */
	export const Empty: CodeActionKind = '';

	/**
	 * Base kind for quickfix actions: 'quickfix'.
	 */
	export const QuickFix: CodeActionKind = 'quickfix';

	/**
	 * Base kind for refactoring actions: 'refactor'.
	 */
	export const Refactor: CodeActionKind = 'refactor';

	/**
	 * Base kind for refactoring extraction actions: 'refactor.extract'.
	 *
	 * Example extract actions:
	 *
	 * - Extract method
	 * - Extract function
	 * - Extract variable
	 * - Extract interface from class
	 * - ...
	 */
	export const RefactorExtract: CodeActionKind = 'refactor.extract';

	/**
	 * Base kind for refactoring inline actions: 'refactor.inline'.
	 *
	 * Example inline actions:
	 *
	 * - Inline function
	 * - Inline variable
	 * - Inline constant
	 * - ...
	 */
	export const RefactorInline: CodeActionKind = 'refactor.inline';

	/**
	 * Base kind for refactoring move actions: 'refactor.move'
	 *
	 * Example move actions:
	 *
	 * - Move a function to a new file
	 * - Move a property between classes
	 * - Move method to base class
	 * - ...
	 *
	 * @since 3.18.0 - proposed
	 */
	export const RefactorMove: CodeActionKind = 'refactor.move';

	/**
	 * Base kind for refactoring rewrite actions: 'refactor.rewrite'.
	 *
	 * Example rewrite actions:
	 *
	 * - Convert JavaScript function to class
	 * - Add or remove parameter
	 * - Encapsulate field
	 * - Make method static
	 * - ...
	 */
	export const RefactorRewrite: CodeActionKind = 'refactor.rewrite';

	/**
	 * Base kind for source actions: `source`.
	 *
	 * Source code actions apply to the entire file.
	 */
	export const Source: CodeActionKind = 'source';

	/**
	 * Base kind for an organize imports source action:
	 * `source.organizeImports`.
	 */
	export const SourceOrganizeImports: CodeActionKind =
		'source.organizeImports';

	/**
	 * Base kind for a 'fix all' source action: `source.fixAll`.
	 *
	 * 'Fix all' actions automatically fix errors that have a clear fix that
	 * do not require user input. They should not suppress errors or perform
	 * unsafe fixes such as generating new types or classes.
	 *
	 * @since 3.17.0
	 */
	export const SourceFixAll: CodeActionKind = 'source.fixAll';

	/**
	 * Base kind for all code actions applying to the entire notebook's scope. CodeActionKinds using
	 * this should always begin with `notebook.`
	 *
	 * @since 3.18.0
	 */
	export const Notebook: CodeActionKind = 'notebook';
}

/**
 * Contains additional diagnostic information about the context in which
 * a code action is run.
 */
export interface CodeActionContext {
	/**
	 * An array of diagnostics known on the client side overlapping the range
	 * provided to the `textDocument/codeAction` request. They are provided so
	 * that the server knows which errors are currently presented to the user
	 * for the given range. There is no guarantee that these accurately reflect
	 * the error state of the resource. The primary parameter
	 * to compute code actions is the provided range.
	 * 
	 * Note that the client should check the `textDocument.diagnostic.markupMessageSupport`
	 * server capability before sending diagnostics with markup messages to a server.
	 * Diagnostics with markup messages should be excluded for servers that don't support
	 * them.
	 */
	diagnostics: Diagnostic[];

	/**
	 * Requested kind of actions to return.
	 *
	 * Actions not of this kind are filtered out by the client before being
	 * shown, so servers can omit computing them.
	 */
	only?: CodeActionKind[];

	/**
	 * The reason why code actions were requested.
	 *
	 * @since 3.17.0
	 */
	triggerKind?: CodeActionTriggerKind;
}

/**
 * The reason why code actions were requested.
 *
 * @since 3.17.0
 */
export namespace CodeActionTriggerKind {
	/**
	 * Code actions were explicitly requested by the user or by an extension.
	 */
	export const Invoked: 1 = 1;

	/**
	 * Code actions were requested automatically.
	 *
	 * This typically happens when the current selection in a file changes,
	 * but can also be triggered when file content changes.
	 */
	export const Automatic: 2 = 2;
}

export type CodeActionTriggerKind = 1 | 2;

/**
 * Code action tags are extra annotations that tweak the behavior of a code action.
 *
 * @since 3.18.0 - proposed
 */
export namespace CodeActionTag {
	/**
	 * Marks the code action as LLM-generated.
	 */
	export const LLMGenerated = 1;
}
export type CodeActionTag = 1;

/**
 * A code action represents a change that can be performed in code, e.g. to fix
 * a problem or to refactor code.
 *
 * A CodeAction must set either `edit` and/or a `command`. If both are supplied,
 * the `edit` is applied first, then the `command` is executed.
 */
export interface CodeAction {

	/**
	 * A short, human-readable title for this code action.
	 */
	title: string;

	/**
	 * The kind of the code action.
	 *
	 * Used to filter code actions.
	 */
	kind?: CodeActionKind;

	/**
	 * The diagnostics that this code action resolves.
	 */
	diagnostics?: Diagnostic[];

	/**
	 * Marks this as a preferred action. Preferred actions are used by the
	 * `auto fix` command and can be targeted by keybindings.
	 *
	 * A quick fix should be marked preferred if it properly addresses the
	 * underlying error. A refactoring should be marked preferred if it is the
	 * most reasonable choice of actions to take.
	 *
	 * @since 3.15.0
	 */
	isPreferred?: boolean;

	/**
	 * Marks that the code action cannot currently be applied.
	 *
	 * Clients should follow the following guidelines regarding disabled code
	 * actions:
	 *
	 * - Disabled code actions are not shown in automatic lightbulbs code
	 *   action menus.
	 *
	 * - Disabled actions are shown as faded out in the code action menu when
	 *   the user request a more specific type of code action, such as
	 *   refactorings.
	 *
	 * - If the user has a keybinding that auto applies a code action and only
	 *   a disabled code actions are returned, the client should show the user
	 *   an error message with `reason` in the editor.
	 *
	 * @since 3.16.0
	 */
	disabled?: {

		/**
		 * Human readable description of why the code action is currently
		 * disabled.
		 *
		 * This is displayed in the code actions UI.
		 */
		reason: string;
	};

	/**
	 * The workspace edit this code action performs.
	 */
	edit?: WorkspaceEdit;

	/**
	 * A command this code action executes. If a code action
	 * provides an edit and a command, first the edit is
	 * executed and then the command.
	 */
	command?: Command;

	/**
	 * A data entry field that is preserved on a code action between
	 * a `textDocument/codeAction` and a `codeAction/resolve` request.
	 *
	 * @since 3.16.0
	 */
	data?: LSPAny;

	/**
 	 * Tags for this code action.
	 *
	 * @since 3.18.0 - proposed
	 */
	tags?: CodeActionTag[];
}

textDocument.codeAction.resolveSupport = { properties: ['edit'] };



/* source file: "language/documentColor.md" */

export interface DocumentColorClientCapabilities {
	/**
	 * Whether document color supports dynamic registration.
	 */
	dynamicRegistration?: boolean;
}

export interface DocumentColorOptions extends WorkDoneProgressOptions {
}

export interface DocumentColorRegistrationOptions extends
	TextDocumentRegistrationOptions, StaticRegistrationOptions,
	DocumentColorOptions {
}

interface DocumentColorParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;
}

interface ColorInformation {
	/**
	 * The range in the document where this color appears.
	 */
	range: Range;

	/**
	 * The actual color value for this color range.
	 */
	color: Color;
}

/**
 * Represents a color in RGBA space.
 */
interface Color {

	/**
	 * The red component of this color in the range [0-1].
	 */
	readonly red: decimal;

	/**
	 * The green component of this color in the range [0-1].
	 */
	readonly green: decimal;

	/**
	 * The blue component of this color in the range [0-1].
	 */
	readonly blue: decimal;

	/**
	 * The alpha component of this color in the range [0-1].
	 */
	readonly alpha: decimal;
}


/* source file: "language/colorPresentation.md" */

interface ColorPresentationParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * The text document.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The color information to request presentations for.
	 */
	color: Color;

	/**
	 * The range where the color would be inserted. Serves as a context.
	 */
	range: Range;
}

interface ColorPresentation {
	/**
	 * The label of this color presentation. It will be shown on the color
	 * picker header. By default, this is also the text that is inserted when
	 * selecting this color presentation.
	 */
	label: string;
	/**
	 * An [edit](#TextEdit) which is applied to a document when selecting
	 * this presentation for the color. When omitted, the
	 * [label](#ColorPresentation.label) is used.
	 */
	textEdit?: TextEdit;
	/**
	 * An optional array of additional [text edits](#TextEdit) that are applied
	 * when selecting this color presentation. Edits must not overlap with the
	 * main [edit](#ColorPresentation.textEdit) nor with themselves.
	 */
	additionalTextEdits?: TextEdit[];
}


/* source file: "language/formatting.md" */

export interface DocumentFormattingClientCapabilities {
	/**
	 * Whether formatting supports dynamic registration.
	 */
	dynamicRegistration?: boolean;
}

export interface DocumentFormattingOptions extends WorkDoneProgressOptions {
}

export interface DocumentFormattingRegistrationOptions extends
	TextDocumentRegistrationOptions, DocumentFormattingOptions {
}

interface DocumentFormattingParams extends WorkDoneProgressParams {
	/**
	 * The document to format.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The formatting options.
	 */
	options: FormattingOptions;
}

/**
 * Value-object describing what options formatting should use.
 */
interface FormattingOptions {
	/**
	 * Size of a tab in spaces.
	 */
	tabSize: uinteger;

	/**
	 * Prefer spaces over tabs.
	 */
	insertSpaces: boolean;

	/**
	 * Trim trailing whitespace on a line.
	 *
	 * @since 3.15.0
	 */
	trimTrailingWhitespace?: boolean;

	/**
	 * Insert a newline character at the end of the file if one does not exist.
	 *
	 * @since 3.15.0
	 */
	insertFinalNewline?: boolean;

	/**
	 * Trim all newlines after the final newline at the end of the file.
	 *
	 * @since 3.15.0
	 */
	trimFinalNewlines?: boolean;

	/**
	 * Signature for further properties.
	 */
	[key: string]: boolean | integer | string;
}


/* source file: "language/rangeFormatting.md" */

export interface DocumentRangeFormattingClientCapabilities {
	/**
	 * Whether formatting supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Whether the client supports formatting multiple ranges at once.
	 *
	 * @since 3.18.0
 	 * @proposed
	 */
	rangesSupport?: boolean;
}

export interface DocumentRangeFormattingOptions extends
	WorkDoneProgressOptions {
	/**
	 * Whether the server supports formatting multiple ranges at once.
	 *
	 * @since 3.18.0
	 * @proposed
	 */
	rangesSupport?: boolean;
}

export interface DocumentRangeFormattingRegistrationOptions extends
	TextDocumentRegistrationOptions, DocumentRangeFormattingOptions {
}

interface DocumentRangeFormattingParams extends WorkDoneProgressParams {
	/**
	 * The document to format.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The range to format.
	 */
	range: Range;

	/**
	 * The formatting options.
	 */
	options: FormattingOptions;
}

interface DocumentRangesFormattingParams extends WorkDoneProgressParams {
	/**
	 * The document to format.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The ranges to format.
	 */
	ranges: Range[];

	/**
	 * The format options.
	 */
	options: FormattingOptions;
}


/* source file: "language/onTypeFormatting.md" */

export interface DocumentOnTypeFormattingClientCapabilities {
	/**
	 * Whether on type formatting supports dynamic registration.
	 */
	dynamicRegistration?: boolean;
}

export interface DocumentOnTypeFormattingOptions {
	/**
	 * A character on which formatting should be triggered, like `{`.
	 */
	firstTriggerCharacter: string;

	/**
	 * More trigger characters.
	 */
	moreTriggerCharacter?: string[];
}

export interface DocumentOnTypeFormattingRegistrationOptions extends
	TextDocumentRegistrationOptions, DocumentOnTypeFormattingOptions {
}

interface DocumentOnTypeFormattingParams {

	/**
	 * The document to format.
	 */
	textDocument: TextDocumentIdentifier;

	/**
	 * The position around which the on type formatting should happen.
	 * This is not necessarily the exact position where the character denoted
	 * by the property `ch` got typed.
	 */
	position: Position;

	/**
	 * The character that has been typed that triggered the formatting
	 * on type request. That is not necessarily the last character that
	 * got inserted into the document since the client could auto insert
	 * characters as well (e.g. automatic brace completion).
	 */
	ch: string;

	/**
	 * The formatting options.
	 */
	options: FormattingOptions;
}


/* source file: "language/rename.md" */

export namespace PrepareSupportDefaultBehavior {
	/**
	 * The client's default behavior is to select the identifier
	 * according to the language's syntax rule.
	 */
	 export const Identifier: 1 = 1;
}

export type PrepareSupportDefaultBehavior = 1;

export interface RenameClientCapabilities {
	/**
	 * Whether rename supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Client supports testing for validity of rename operations
	 * before execution.
	 *
	 * @since version 3.12.0
	 */
	prepareSupport?: boolean;

	/**
	 * Client supports the default behavior result
	 * (`{ defaultBehavior: boolean }`).
	 *
	 * The value indicates the default behavior used by the
	 * client.
	 *
	 * @since version 3.16.0
	 */
	prepareSupportDefaultBehavior?: PrepareSupportDefaultBehavior;

	/**
	 * Whether the client honors the change annotations in
	 * text edits and resource operations returned via the
	 * rename request's workspace edit by, for example, presenting
	 * the workspace edit in the user interface and asking
	 * for confirmation.
	 *
	 * @since 3.16.0
	 */
	honorsChangeAnnotations?: boolean;
}

export interface RenameOptions extends WorkDoneProgressOptions {
	/**
	 * Renames should be checked and tested before being executed.
	 */
	prepareProvider?: boolean;
}

export interface RenameRegistrationOptions extends
	TextDocumentRegistrationOptions, RenameOptions {
}

interface RenameParams extends TextDocumentPositionParams,
	WorkDoneProgressParams {
	/**
	 * The new name of the symbol. If the given name is not valid, the
	 * request must return a [ResponseError](#ResponseError) with an
	 * appropriate message set.
	 */
	newName: string;
}

export interface PrepareRenameParams extends TextDocumentPositionParams, WorkDoneProgressParams {
}


/* source file: "language/linkedEditingRange.md" */

export interface LinkedEditingRangeClientCapabilities {
	/**
	 * Whether the implementation supports dynamic registration.
	 * If this is set to `true` the client supports the new
	 * `(TextDocumentRegistrationOptions & StaticRegistrationOptions)`
	 * return value for the corresponding server capability as well.
	 */
	dynamicRegistration?: boolean;
}

export interface LinkedEditingRangeOptions extends WorkDoneProgressOptions {
}

export interface LinkedEditingRangeRegistrationOptions extends
	TextDocumentRegistrationOptions, LinkedEditingRangeOptions,
	StaticRegistrationOptions {
}

export interface LinkedEditingRangeParams extends TextDocumentPositionParams,
	WorkDoneProgressParams {
}

export interface LinkedEditingRanges {
	/**
	 * A list of ranges that can be renamed together. The ranges must have
	 * identical length and contain identical text content. The ranges cannot
	 * overlap.
	 */
	ranges: Range[];

	/**
	 * An optional word pattern (regular expression) that describes valid
	 * contents for the given ranges. If no pattern is provided, the client
	 * configuration's word pattern will be used.
	 */
	wordPattern?: string;
}


/* source file: "language/inlineCompletion.md" */

/**
 * Client capabilities specific to inline completions.
 *
 * @since 3.18.0
 */
export interface InlineCompletionClientCapabilities {
	/**
	 * Whether implementation supports dynamic registration for inline
	 * completion providers.
	 */
	dynamicRegistration?: boolean;
}

/**
 * Inline completion options used during static registration.
 *
 * @since 3.18.0
 */
export interface InlineCompletionOptions extends WorkDoneProgressOptions {
}

/**
 * Inline completion options used during static or dynamic registration.
 *
 * @since 3.18.0
 */
export interface InlineCompletionRegistrationOptions extends
	InlineCompletionOptions, TextDocumentRegistrationOptions,
	StaticRegistrationOptions {
}

/**
 * A parameter literal used in inline completion requests.
 *
 * @since 3.18.0
 */
export interface InlineCompletionParams extends TextDocumentPositionParams,
	WorkDoneProgressParams {
	/**
	 * Additional information about the context in which inline completions
	 * were requested.
	 */
	context: InlineCompletionContext;
}

/**
 * Provides information about the context in which an inline completion was
 * requested.
 *
 * @since 3.18.0
 */
export interface InlineCompletionContext {
	/**
	 * Describes how the inline completion was triggered.
	 */
	triggerKind: InlineCompletionTriggerKind;

	/**
	 * Provides information about the currently selected item in the
	 * autocomplete widget if it is visible.
	 *
	 * If set, provided inline completions must extend the text of the
	 * selected item and use the same range, otherwise they are not shown as
	 * preview.
	 * As an example, if the document text is `console.` and the selected item
	 * is `.log` replacing the `.` in the document, the inline completion must
	 * also replace `.` and start with `.log`, for example `.log()`.
	 *
	 * Inline completion providers are requested again whenever the selected
	 * item changes.
	 */
	selectedCompletionInfo?: SelectedCompletionInfo;
}

/**
 * Describes how an {@link InlineCompletionItemProvider inline completion
 * provider} was triggered.
 *
 * @since 3.18.0
 */
export namespace InlineCompletionTriggerKind {
	/**
	 * Completion was triggered explicitly by a user gesture.
	 * Return multiple completion items to enable cycling through them.
	 */
	export const Invoked: 1 = 1;

	/**
	 * Completion was triggered automatically while editing.
	 * It is sufficient to return a single completion item in this case.
	 */
	export const Automatic: 2 = 2;
}

export type InlineCompletionTriggerKind = 1 | 2;

/**
 * Describes the currently selected completion item.
 *
 * @since 3.18.0
 */
export interface SelectedCompletionInfo {
	/**
	 * The range that will be replaced if this completion item is accepted.
	 */
	range: Range;

	/**
	 * The text the range will be replaced with if this completion is
	 * accepted.
	 */
	text: string;
}

/**
 * Represents a collection of {@link InlineCompletionItem inline completion
 * items} to be presented in the editor.
 *
 * @since 3.18.0
 */
export interface InlineCompletionList {
	/**
	 * The inline completion items.
	 */
	items: InlineCompletionItem[];
}

/**
 * An inline completion item represents a text snippet that is proposed inline
 * to complete text that is being typed.
 *
 * @since 3.18.0
 */
export interface InlineCompletionItem {
	/**
	 * The text to replace the range with. Must be set.
	 * Is used both for the preview and the accept operation.
	 */
	insertText: string | StringValue;

	/**
	 * A text that is used to decide if this inline completion should be
	 * shown. When `falsy`, the {@link InlineCompletionItem.insertText} is
	 * used.
	 *
	 * An inline completion is shown if the text to replace is a prefix of the
	 * filter text.
	 */
	filterText?: string;

	/**
	 * The range to replace.
	 * Must begin and end on the same line.
	 *
	 * Prefer replacements over insertions to provide a better experience when
	 * the user deletes typed text.
	 */
	range?: Range;

	/**
	 * An optional {@link Command} that is executed *after* inserting this
	 * completion.
	 */
	command?: Command;
}


/* source file: "workspace/symbol.md" */

interface WorkspaceSymbolClientCapabilities {
	/**
	 * Symbol request supports dynamic registration.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Specific capabilities for the `SymbolKind` in the `workspace/symbol`
	 * request.
	 */
	symbolKind?: {
		/**
		 * The symbol kind values the client supports. When this
		 * property exists, the client also guarantees that it will
		 * handle values outside its set gracefully and falls back
		 * to a default value when unknown.
		 *
		 * If this property is not present, the client only supports
		 * the symbol kinds from `File` to `Array` as defined in
		 * the initial version of the protocol.
		 */
		valueSet?: SymbolKind[];
	};

	/**
	 * The client supports tags on `SymbolInformation` and `WorkspaceSymbol`.
	 * Clients supporting tags have to handle unknown tags gracefully.
	 *
	 * @since 3.16.0
	 */
	tagSupport?: {
		/**
		 * The tags supported by the client.
		 */
		valueSet: SymbolTag[];
	};

	/**
	 * The client supports partial workspace symbols. The client will send the
	 * request `workspaceSymbol/resolve` to the server to resolve additional
	 * properties.
	 *
	 * @since 3.17.0 - proposedState
	 */
	resolveSupport?: {
		/**
		 * The properties that a client can resolve lazily. Usually consists of
		 * `location.range`.
		 */
		properties: string[];
	};
}

export interface WorkspaceSymbolOptions extends WorkDoneProgressOptions {
	/**
	 * The server provides support to resolve additional
	 * information for a workspace symbol.
	 *
	 * @since 3.17.0
	 */
	resolveProvider?: boolean;
}

export interface WorkspaceSymbolRegistrationOptions
	extends WorkspaceSymbolOptions {
}

/**
 * The parameters of a Workspace Symbol Request.
 */
interface WorkspaceSymbolParams extends WorkDoneProgressParams,
	PartialResultParams {
	/**
	 * A query string to filter symbols by. Clients may send an empty
	 * string here to request all symbols.
	 *
	 * The `query`-parameter should be interpreted in a *relaxed way* as editors
	 * will apply their own highlighting and scoring on the results. A good rule
	 * of thumb is to match case-insensitive and to simply check that the
	 * characters of *query* appear in their order in a candidate symbol.
	 * Servers shouldn't use prefix, substring, or similar strict matching.
	 */
	query: string;
}

/**
 * A special workspace symbol that supports locations without a range.
 *
 * @since 3.17.0
 */
export interface WorkspaceSymbol {
	/**
	 * The name of this symbol.
	 */
	name: string;

	/**
	 * The kind of this symbol.
	 */
	kind: SymbolKind;

	/**
	 * Tags for this completion item.
	 */
	tags?: SymbolTag[];

	/**
	 * The name of the symbol containing this symbol. This information is for
	 * user interface purposes (e.g. to render a qualifier in the user interface
	 * if necessary). It can't be used to re-infer a hierarchy for the document
	 * symbols.
	 */
	containerName?: string;

	/**
	 * The location of this symbol. Whether a server is allowed to
	 * return a location without a range depends on the client
	 * capability `workspace.symbol.resolveSupport`.
	 *
	 * See also `SymbolInformation.location`.
	 */
	location: Location | { uri: DocumentUri };

	/**
	 * A data entry field that is preserved on a workspace symbol between a
	 * workspace symbol request and a workspace symbol resolve request.
	 */
	data?: LSPAny;
}


/* source file: "workspace/configuration.md" */


export interface ConfigurationParams {
	items: ConfigurationItem[];
}

export interface ConfigurationItem {
	/**
	 * The scope to get the configuration section for.
	 */
	scopeUri?: URI;

	/**
	 * The configuration section asked for.
	 */
	section?: string;
}


/* source file: "workspace/didChangeConfiguration.md" */

export interface DidChangeConfigurationClientCapabilities {
	/**
	 * Did change configuration notification supports dynamic registration.
	 *
	 * @since 3.6.0 to support the new pull model.
	 */
	dynamicRegistration?: boolean;
}

interface DidChangeConfigurationParams {
	/**
	 * The actual changed settings.
	 */
	settings: LSPAny;
}


/* source file: "workspace/workspaceFolders.md" */

export interface WorkspaceFoldersServerCapabilities {
	/**
	 * The server has support for workspace folders.
	 */
	supported?: boolean;

	/**
	 * Whether the server wants to receive workspace folder
	 * change notifications.
	 *
	 * If a string is provided, the string is treated as an ID
	 * under which the notification is registered on the client
	 * side. The ID can be used to unregister for these events
	 * using the `client/unregisterCapability` request.
	 */
	changeNotifications?: string | boolean;
}

export interface WorkspaceFolder {
	/**
	 * The associated URI for this workspace folder.
	 */
	uri: URI;

	/**
	 * The name of the workspace folder. Used to refer to this
	 * workspace folder in the user interface.
	 */
	name: string;
}


/* source file: "workspace/didChangeWorkspaceFolders.md" */


export interface DidChangeWorkspaceFoldersParams {
	/**
	 * The actual workspace folder change event.
	 */
	event: WorkspaceFoldersChangeEvent;
}

/**
 * The workspace folder change event.
 */
export interface WorkspaceFoldersChangeEvent {
	/**
	 * The array of added workspace folders.
	 */
	added: WorkspaceFolder[];

	/**
	 * The array of removed workspace folders.
	 */
	removed: WorkspaceFolder[];
}


/* source file: "workspace/willCreateFiles.md" */

/**
 * The options to register for file operations.
 *
 * @since 3.16.0
 */
interface FileOperationRegistrationOptions {
	/**
	 * The actual filters.
	 */
	filters: FileOperationFilter[];
}

/**
 * A pattern kind describing if a glob pattern matches a file,
 * a folder, or both.
 *
 * @since 3.16.0
 */
export namespace FileOperationPatternKind {
	/**
	 * The pattern matches a file only.
	 */
	export const file: 'file' = 'file';

	/**
	 * The pattern matches a folder only.
	 */
	export const folder: 'folder' = 'folder';
}

export type FileOperationPatternKind = 'file' | 'folder';

/**
 * Matching options for the file operation pattern.
 *
 * @since 3.16.0
 */
export interface FileOperationPatternOptions {

	/**
	 * The pattern should be matched ignoring casing.
	 */
	ignoreCase?: boolean;
}

/**
 * A pattern to describe in which file operation requests or notifications
 * the server is interested in.
 *
 * @since 3.16.0
 */
interface FileOperationPattern {
	/**
	 * The glob pattern to match. Glob patterns can have the following syntax:
	 * - `*` to match zero or more characters in a path segment
	 * - `?` to match on one character in a path segment
	 * - `**` to match any number of path segments, including none
	 * - `{}` to group sub patterns into an OR expression. (e.g. `**​/*.{ts,js}`
	 *   matches all TypeScript and JavaScript files)
	 * - `[]` to declare a range of characters to match in a path segment
	 *   (e.g., `example.[0-9]` to match on `example.0`, `example.1`, …)
	 * - `[!...]` to negate a range of characters to match in a path segment
	 *   (e.g., `example.[!0-9]` to match on `example.a`, `example.b`, but
	 *   not `example.0`)
	 */
	glob: string;

	/**
	 * Whether to match files or folders with this pattern.
	 *
	 * Matches both if undefined.
	 */
	matches?: FileOperationPatternKind;

	/**
	 * Additional options used during matching.
	 */
	options?: FileOperationPatternOptions;
}

/**
 * A filter to describe in which file operation requests or notifications
 * the server is interested in.
 *
 * @since 3.16.0
 */
export interface FileOperationFilter {

	/**
	 * A URI scheme, like `file` or `untitled`.
	 */
	scheme?: string;

	/**
	 * The actual file operation pattern.
	 */
	pattern: FileOperationPattern;
}

/**
 * The parameters sent in notifications/requests for user-initiated creation
 * of files.
 *
 * @since 3.16.0
 */
export interface CreateFilesParams {

	/**
	 * An array of all files/folders created in this operation.
	 */
	files: FileCreate[];
}

/**
 * Represents information on a file/folder create.
 *
 * @since 3.16.0
 */
export interface FileCreate {

	/**
	 * A file:// URI for the location of the file/folder being created.
	 */
	uri: string;
}


/* source file: "workspace/didCreateFiles.md" */


/* source file: "workspace/willRenameFiles.md" */

/**
 * The parameters sent in notifications/requests for user-initiated renames
 * of files.
 *
 * @since 3.16.0
 */
export interface RenameFilesParams {

	/**
	 * An array of all files/folders renamed in this operation. When a folder
	 * is renamed, only the folder will be included, and not its children.
	 */
	files: FileRename[];
}

/**
 * Represents information on a file/folder rename.
 *
 * @since 3.16.0
 */
export interface FileRename {

	/**
	 * A file:// URI for the original location of the file/folder being renamed.
	 */
	oldUri: string;

	/**
	 * A file:// URI for the new location of the file/folder being renamed.
	 */
	newUri: string;
}


/* source file: "workspace/didRenameFiles.md" */


/* source file: "workspace/willDeleteFiles.md" */

/**
 * The parameters sent in notifications/requests for user-initiated deletes
 * of files.
 *
 * @since 3.16.0
 */
export interface DeleteFilesParams {

	/**
	 * An array of all files/folders deleted in this operation.
	 */
	files: FileDelete[];
}

/**
 * Represents information on a file/folder delete.
 *
 * @since 3.16.0
 */
export interface FileDelete {

	/**
	 * A file:// URI for the location of the file/folder being deleted.
	 */
	uri: string;
}


/* source file: "workspace/didDeleteFiles.md" */


/* source file: "workspace/didChangeWatchedFiles.md" */

export interface DidChangeWatchedFilesClientCapabilities {
	/**
	 * Did change watched files notification supports dynamic registration.
	 * Please note that the current protocol doesn't support static
	 * configuration for file changes from the server side.
	 */
	dynamicRegistration?: boolean;

	/**
	 * Whether the client has support for relative patterns
	 * or not.
	 *
	 * @since 3.17.0
	 */
	relativePatternSupport?: boolean;
}

/**
 * Describe options to be used when registering for file system change events.
 */
export interface DidChangeWatchedFilesRegistrationOptions {
	/**
	 * The watchers to register.
	 */
	watchers: FileSystemWatcher[];
}

export interface FileSystemWatcher {
	/**
	 * The glob pattern to watch. See {@link GlobPattern glob pattern}
	 * for more detail.
	 *
 	 * @since 3.17.0 support for relative patterns.
	 */
	globPattern: GlobPattern;

	/**
	 * The kind of events of interest. If omitted, it defaults
	 * to WatchKind.Create | WatchKind.Change | WatchKind.Delete
	 * which is 7.
	 */
	kind?: WatchKind;
}

export namespace WatchKind {
	/**
	 * Interested in create events.
	 */
	export const Create = 1;

	/**
	 * Interested in change events.
	 */
	export const Change = 2;

	/**
	 * Interested in delete events.
	 */
	export const Delete = 4;
}
export type WatchKind = uinteger;

interface DidChangeWatchedFilesParams {
	/**
	 * The actual file events.
	 */
	changes: FileEvent[];
}

/**
 * An event describing a file change.
 */
interface FileEvent {
	/**
	 * The file's URI.
	 */
	uri: DocumentUri;
	/**
	 * The change type.
	 */
	type: FileChangeType;
}

/**
 * The file event type.
 */
export namespace FileChangeType {
	/**
	 * The file got created.
	 */
	export const Created = 1;
	/**
	 * The file got changed.
	 */
	export const Changed = 2;
	/**
	 * The file got deleted.
	 */
	export const Deleted = 3;
}

export type FileChangeType = 1 | 2 | 3;


/* source file: "workspace/executeCommand.md" */

export interface ExecuteCommandClientCapabilities {
	/**
	 * Execute command supports dynamic registration.
	 */
	dynamicRegistration?: boolean;
}

export interface ExecuteCommandOptions extends WorkDoneProgressOptions {
	/**
	 * The commands to be executed on the server.
	 */
	commands: string[];
}

/**
 * Execute command registration options.
 */
export interface ExecuteCommandRegistrationOptions
	extends ExecuteCommandOptions {
}

export interface ExecuteCommandParams extends WorkDoneProgressParams {

	/**
	 * The identifier of the actual command handler.
	 */
	command: string;
	/**
	 * Arguments that the command should be invoked with.
	 */
	arguments?: LSPAny[];
}


/* source file: "workspace/applyEdit.md" */

export interface ApplyWorkspaceEditParams {
	/**
	 * An optional label of the workspace edit. This label is
	 * presented in the user interface, for example, on an undo
	 * stack to undo the workspace edit.
	 */
	label?: string;

	/**
	 * The edits to apply.
	 */
	edit: WorkspaceEdit;

	/**
	 * Additional data about the edit.
	 *
	 * @since 3.18.0
	 * @proposed
	 */
	metadata?: WorkspaceEditMetadata;
}

/**
 * Additional data about a workspace edit.
 *
 * @since 3.18.0
 * @proposed
 */
export interface WorkspaceEditMetadata {
	/**
	 * Signal to the editor that this edit is a refactoring.
	 */
	isRefactoring?: boolean;
}

export interface ApplyWorkspaceEditResult {
	/**
	 * Indicates whether the edit was applied or not.
	 */
	applied: boolean;

	/**
	 * An optional textual description for why the edit was not applied.
	 * This may be used by the server for diagnostic logging or to provide
	 * a suitable error for a request that triggered the edit.
	 */
	failureReason?: string;

	/**
	 * Depending on the client's failure handling strategy, `failedChange`
	 * might contain the index of the change that failed. This property is
	 * only available if the client signals a `failureHandling` strategy
	 * in its client capabilities.
	 */
	failedChange?: uinteger;
}


/* source file: "workspace/textDocumentContent.md" */

/**
 * Client capabilities for a text document content provider.
 *
 * @since 3.18.0
 */
export type TextDocumentContentClientCapabilities = {
	/**
	 * Text document content provider supports dynamic registration.
	 */
	dynamicRegistration?: boolean;
};

/**
 * Text document content provider options.
 *
 * @since 3.18.0
 */
export type TextDocumentContentOptions = {
	/**
	 * The schemes for which the server provides content.
	 */
	schemes: string[];
};

/**
 * Text document content provider registration options.
 *
 * @since 3.18.0
 */
export type TextDocumentContentRegistrationOptions = TextDocumentContentOptions &
	StaticRegistrationOptions;

/**
 * Parameters for the `workspace/textDocumentContent` request.
 *
 * @since 3.18.0
 */
export interface TextDocumentContentParams {
	/**
	 * The uri of the text document.
	 */
	uri: DocumentUri;
}

/**
 * Result of the `workspace/textDocumentContent` request.
 *
 * @since 3.18.0
 * @proposed
 */
export interface TextDocumentContentResult {
	/**
	 * The text content of the text document. Please note, that the content of
	 * any subsequent open notifications for the text document might differ
	 * from the returned content due to whitespace and line ending
	 * normalizations done on the client
	 */
	text: string;
}

/**
 * Parameters for the `workspace/textDocumentContent/refresh` request.
 *
 * @since 3.18.0
 */
export interface TextDocumentContentRefreshParams {
	/**
	 * The uri of the text document to refresh.
	 */
	uri: DocumentUri;
}


/* source file: "messages/3.18/showMessage.md" */

interface ShowMessageParams {
	/**
	 * The message type. See {@link MessageType}.
	 */
	type: MessageType;

	/**
	 * The actual message.
	 */
	message: string;
}

export namespace MessageType {
	/**
	 * An error message.
	 */
	export const Error = 1;
	/**
	 * A warning message.
	 */
	export const Warning = 2;
	/**
	 * An information message.
	 */
	export const Info = 3;
	/**
	 * A log message.
	 */
	export const Log = 4;
	/**
	 * A debug message.
	 *
	 * @since 3.18.0
	 */
	export const Debug = 5;
}

export type MessageType = 1 | 2 | 3 | 4 | 5;


/* source file: "messages/3.18/showMessageRequest.md" */

/**
 * Show message request client capabilities
 */
export interface ShowMessageRequestClientCapabilities {
	/**
	 * Capabilities specific to the `MessageActionItem` type.
	 */
	messageActionItem?: {
		/**
		 * Whether the client supports additional attributes which
		 * are preserved and sent back to the server in the
		 * request's response.
		 */
		additionalPropertiesSupport?: boolean;
	};
}

interface ShowMessageRequestParams {
	/**
	 * The message type. See {@link MessageType}.
	 */
	type: MessageType;

	/**
	 * The actual message.
	 */
	message: string;

	/**
	 * The message action items to present.
	 */
	actions?: MessageActionItem[];
}

interface MessageActionItem {
	/**
	 * A short title like 'Retry', 'Open Log' etc.
	 */
	title: string;
}


/* source file: "window/showDocument.md" */

/**
 * Client capabilities for the show document request.
 *
 * @since 3.16.0
 */
export interface ShowDocumentClientCapabilities {
	/**
	 * The client has support for the show document
	 * request.
	 */
	support: boolean;
}

/**
 * Params to show a resource.
 *
 * @since 3.16.0
 */
export interface ShowDocumentParams {
	/**
	 * The URI to show.
	 */
	uri: URI;

	/**
	 * Indicates to show the resource in an external program.
	 * To show, for example, `https://code.visualstudio.com/`
	 * in the default web browser, set `external` to `true`.
	 */
	external?: boolean;

	/**
	 * An optional property to indicate whether the editor
	 * showing the document should take focus or not.
	 * Clients might ignore this property if an external
	 * program is started.
	 */
	takeFocus?: boolean;

	/**
	 * An optional selection range if the document is a text
	 * document. Clients might ignore this property if an
	 * external program is started or the file is not a text
	 * file.
	 */
	selection?: Range;
}

/**
 * The result of a show document request.
 *
 * @since 3.16.0
 */
export interface ShowDocumentResult {
	/**
	 * A boolean indicating if the show was successful.
	 */
	success: boolean;
}


/* source file: "messages/3.18/logMessage.md" */

interface LogMessageParams {
	/**
	 * The message type. See {@link MessageType}.
	 */
	type: MessageType;

	/**
	 * The actual message.
	 */
	message: string;
}


/* source file: "window/workDoneProgressCreate.md" */

export interface WorkDoneProgressCreateParams {
	/**
	 * The token to be used to report progress.
	 */
	token: ProgressToken;
}


/* source file: "window/workDoneProgressCancel.md" */

export interface WorkDoneProgressCancelParams {
	/**
	 * The token to be used to report progress.
	 */
	token: ProgressToken;
}


/* source file: "messages/3.18/telemetryEvent.md" */
