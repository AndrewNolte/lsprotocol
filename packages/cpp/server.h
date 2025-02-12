/// @generated via `python -m generator --plugin cpp`

#pragma once
#include <optional>
#include <variant>
#include <vector>

#include "json_types.h"
#include "lsptypes.h"

namespace lsp {

class Server {
    /** A request to provide inline values in a document. The request's
    parameter is of type {@link InlineValueParams}, the response is of type
    {@link InlineValue InlineValue[]} or a Thenable that resolves to such.

    @since 3.17.0 */
    std::optional<std::vector<InlineValue>> inlineValue(InlineValueParams);
    /** A request to provide selection ranges in a document. The request's
    parameter is of type {@link SelectionRangeParams}, the
    response is of type {@link SelectionRange SelectionRange[]} or a Thenable
    that resolves to such. */
    std::optional<std::vector<SelectionRange>> selectionRange(
            SelectionRangeParams);
    /** Request to request hover information at a given text document position.
    The request's parameter is of type {@link TextDocumentPosition} the response
    is of type {@link Hover} or a Thenable that resolves to such. */
    std::optional<Hover> hover(HoverParams);
    /** A request to provide inlay hints in a document. The request's parameter
    is of type {@link InlayHintsParams}, the response is of type
    {@link InlayHint InlayHint[]} or a Thenable that resolves to such.

    @since 3.17.0 */
    std::optional<std::vector<InlayHint>> inlayHint(InlayHintParams);
    /** The will delete files request is sent from the client to the server
    before files are actually deleted as long as the deletion is triggered from
    within the client.

    @since 3.16.0 */
    void didDeleteFiles(DeleteFilesParams);
    std::optional<SignatureHelp> signatureHelp(SignatureHelpParams);
    /** @since 3.16.0 */
    std::optional<SemanticTokens> semanticTokensrange(
            SemanticTokensRangeParams);
    /** A request to list project-wide symbols matching the query string given
    by the {@link WorkspaceSymbolParams}. The response is
    of type {@link SymbolInformation SymbolInformation[]} or a Thenable that
    resolves to such.

    @since 3.17.0 - support for WorkspaceSymbol in the returned data. Clients
     need to advertise support for WorkspaceSymbols via the client capability
     `workspace.symbol.resolveSupport`.
     */
    std::variant<std::vector<SymbolInformation>,
                 std::vector<WorkspaceSymbol>,
                 std::monostate>
            symbol(WorkspaceSymbolParams);
    /** A request to provide document links */
    std::optional<std::vector<DocumentLink>> documentLink(DocumentLinkParams);
    /** A request to result a `CallHierarchyItem` in a document at a given
    position. Can be used as an input to an incoming or outgoing call hierarchy.

    @since 3.16.0 */
    std::optional<std::vector<CallHierarchyItem>> prepareCallHierarchy(
            CallHierarchyPrepareParams);
    /** A request to resolve the implementation locations of a symbol at a given
    text document position. The request's parameter is of type {@link
    TextDocumentPositionParams} the response is of type {@link Definition} or a
    Thenable that resolves to such. */
    std::variant<Definition, std::vector<DefinitionLink>, std::monostate>
            implementation(ImplementationParams);
    void progress(ProgressParams);
    /** Request to resolve additional information for a given document link. The
    request's parameter is of type {@link DocumentLink} the response is of type
    {@link DocumentLink} or a Thenable that resolves to such. */
    DocumentLink resolve(DocumentLink);
    /** A request to resolve the range inside the workspace
    symbol's location.

    @since 3.17.0 */
    WorkspaceSymbol resolve(WorkspaceSymbol);
    /** A request to resolve the type definition locations of a symbol at a
    given text document position. The request's parameter is of type {@link
    TextDocumentPositionParams} the response is of type {@link Declaration} or a
    typed array of {@link DeclarationLink} or a Thenable that resolves to such.
  */
    std::variant<Declaration, std::vector<DeclarationLink>, std::monostate>
            declaration(DeclarationParams);
    void cancelRequest(CancelParams);
    /** The document diagnostic request definition.

    @since 3.17.0 */
    DocumentDiagnosticReport diagnostic(DocumentDiagnosticParams);
    void didChange(DidChangeNotebookDocumentParams);
    /** The document close notification is sent from the client to the server
    when the document got closed in the client. The document's truth now exists
    where the document's uri points to (e.g. if the document's uri is a file uri
    the truth now exists on disk). As with the open notification the close
    notification is about managing the document's content. Receiving a close
    notification doesn't mean that the document was open in an editor before. A
    close notification requires a previous open notification to be sent. */
    void didClose(DidCloseTextDocumentParams);
    /** A request to resolve the subtypes for a given `TypeHierarchyItem`.

    @since 3.17.0 */
    std::optional<std::vector<TypeHierarchyItem>> subtypes(
            TypeHierarchySubtypesParams);
    /** The document open notification is sent from the client to the server to
    signal newly opened text documents. The document's truth is now managed by
    the client and the server must not try to read the document's truth using
    the document's uri. Open in this sense means it is managed by the client. It
    doesn't necessarily mean that its content is presented in an editor. An open
    notification must not be sent more than once without a corresponding close
    notification send before. This means open and close notification must be
    balanced and the max open count is one. */
    void didOpen(DidOpenTextDocumentParams);
    /** A request to get the moniker of a symbol at a given text document
    position. The request parameter is of type {@link
    TextDocumentPositionParams}. The response is of type {@link Moniker
    Moniker[]} or `null`. */
    std::optional<std::vector<Moniker>> moniker(MonikerParams);
    /** A request to format a whole document. */
    std::optional<std::vector<TextEdit>> formatting(DocumentFormattingParams);
    /** A request to result a `TypeHierarchyItem` in a document at a given
    position. Can be used as an input to a subtypes or supertypes type
    hierarchy.

    @since 3.17.0 */
    std::optional<std::vector<TypeHierarchyItem>> prepareTypeHierarchy(
            TypeHierarchyPrepareParams);
    /** The did rename files notification is sent from the client to the server
    when files were renamed from within the client.

    @since 3.16.0 */
    void didRenameFiles(RenameFilesParams);
    /** The `workspace/textDocumentContent` request is sent from the client to
    the server to request the content of a text document.

    @since 3.18.0
    @proposed */
    TextDocumentContentResult textDocumentContent(TextDocumentContentParams);
    /** A notification sent when a notebook document is saved.

    @since 3.17.0 */
    void didSave(DidSaveNotebookDocumentParams);
    /** The will rename files request is sent from the client to the server
    before files are actually renamed as long as the rename is triggered from
    within the client.

    @since 3.16.0 */
    std::optional<WorkspaceEdit> willRenameFiles(RenameFilesParams);
    /** The watched files notification is sent from the client to the server
    when the client detects changes to file watched by the language client. */
    void didChangeWatchedFiles(DidChangeWatchedFilesParams);
    /** A request to format ranges in a document.

    @since 3.18.0
    @proposed */
    std::optional<std::vector<TextEdit>> rangesFormatting(
            DocumentRangesFormattingParams);
    /** The document change notification is sent from the client to the server
    to signal changes to a text document. */
    void didChange(DidChangeTextDocumentParams);
    /** The will create files request is sent from the client to the server
    before files are actually created as long as the creation is triggered from
    within the client.

    The request can return a `WorkspaceEdit` which will be applied to workspace
    before the files are created. Hence the `WorkspaceEdit` can not manipulate
    the content of the file to be created.

    @since 3.16.0 */
    std::optional<WorkspaceEdit> willCreateFiles(CreateFilesParams);
    /** The did create files notification is sent from the client to the server
    when files were created from within the client.

    @since 3.16.0 */
    void didCreateFiles(CreateFilesParams);
    /** A request to resolve the definition location of a symbol at a given text
    document position. The request's parameter is of type {@link
    TextDocumentPosition} the response is of either type {@link Definition} or a
    typed array of
    {@link DefinitionLink} or a Thenable that resolves to such. */
    std::variant<Definition, std::vector<DefinitionLink>, std::monostate>
            definition(DefinitionParams);
    /** The `window/workDoneProgress/cancel` notification is sent from  the
    client to the server to cancel a progress initiated on the server side. */
    void workDoneProgresscancel(WorkDoneProgressCancelParams);
    /** Request to resolve a {@link DocumentHighlight} for a given
    text document position. The request's parameter is of type {@link
    TextDocumentPosition} the request response is an array of type {@link
    DocumentHighlight} or a Thenable that resolves to such. */
    std::optional<std::vector<DocumentHighlight>> documentHighlight(
            DocumentHighlightParams);
    /** The exit event is sent from the client to the server to
    ask the server to exit its process. */
    void exit();
    /** A request send from the client to the server to execute a command. The
    request might return a workspace edit which the client will apply to the
    workspace. */
    std::optional<LSPAny> executeCommand(ExecuteCommandParams);
    /** The initialized notification is sent from the client to the
    server after the client is fully initialized and the server
    is allowed to send requests from the server to the client. */
    void initialized(InitializedParams);
    /** The document save notification is sent from the client to the server
    when the document got saved in the client. */
    void didSave(DidSaveTextDocumentParams);
    /** A request to resolve project-wide references for the symbol denoted
    by the given text document position. The request's parameter is of
    type {@link ReferenceParams} the response is of type
    {@link Location Location[]} or a Thenable that resolves to such. */
    std::optional<std::vector<Location>> references(ReferenceParams);
    /** The `workspace/didChangeWorkspaceFolders` notification is sent from the
    client to the server when the workspace folder configuration changes. */
    void didChangeWorkspaceFolders(DidChangeWorkspaceFoldersParams);
    /** The initialize request is sent from the client to the server.
    It is sent once as the request after starting up the server.
    The requests parameter is of type {@link InitializeParams}
    the response if of type {@link InitializeResult} of a Thenable that
    resolves to such. */
    InitializeResult initialize(InitializeParams);
    /** A request to resolve additional properties for an inlay hint.
    The request's parameter is of type {@link InlayHint}, the response is
    of type {@link InlayHint} or a Thenable that resolves to such.

    @since 3.17.0 */
    InlayHint resolve(InlayHint);
    /** A notification sent when a notebook opens.

    @since 3.17.0 */
    void didOpen(DidOpenNotebookDocumentParams);
    /** A shutdown request is sent from the client to the server.
    It is sent once when the client decides to shutdown the
    server. The only notification that is sent after a shutdown request
    is the exit event. */
    std::monostate shutdown();
    /** A request to list all symbols found in a given text document. The
    request's parameter is of type {@link TextDocumentIdentifier} the response
    is of type {@link SymbolInformation SymbolInformation[]} or a Thenable that
    resolves to such. */
    std::variant<std::vector<SymbolInformation>,
                 std::vector<DocumentSymbol>,
                 std::monostate>
            documentSymbol(DocumentSymbolParams);
    /** @since 3.16.0 */
    std::optional<SemanticTokens> semanticTokensfull(SemanticTokensParams);
    /** A request to rename a symbol. */
    std::optional<WorkspaceEdit> rename(RenameParams);
    /** A request to provide code lens for the given text document. */
    std::optional<std::vector<CodeLens>> codeLens(CodeLensParams);
    /** A request to format a document on type. */
    std::optional<std::vector<TextEdit>> onTypeFormatting(
            DocumentOnTypeFormattingParams);
    /** Request to request completion at a given text document position. The
    request's parameter is of type {@link TextDocumentPosition} the response is
    of type {@link CompletionItem CompletionItem[]} or {@link CompletionList} or
    a Thenable that resolves to such.

    The request can delay the computation of the {@link CompletionItem.detail
    `detail`} and {@link CompletionItem.documentation `documentation`}
    properties to the `completionItem/resolve` request. However, properties that
    are needed for the initial sorting and filtering, like `sortText`,
    `filterText`, `insertText`, and `textEdit`, must not be changed during
    resolve. */
    std::variant<std::vector<CompletionItem>, CompletionList, std::monostate>
            completion(CompletionParams);
    /** A request to resolve the type definition locations of a symbol at a
    given text document position. The request's parameter is of type {@link
    TextDocumentPositionParams} the response is of type {@link Definition} or a
    Thenable that resolves to such. */
    std::variant<Definition, std::vector<DefinitionLink>, std::monostate>
            typeDefinition(TypeDefinitionParams);
    /** A request to list all color symbols found in a given text document. The
    request's parameter is of type {@link DocumentColorParams} the response is
    of type {@link ColorInformation ColorInformation[]} or a Thenable that
    resolves to such. */
    std::vector<ColorInformation> documentColor(DocumentColorParams);
    /** A request to resolve the outgoing calls for a given `CallHierarchyItem`.

    @since 3.16.0 */
    std::optional<std::vector<CallHierarchyOutgoingCall>> outgoingCalls(
            CallHierarchyOutgoingCallsParams);
    /** A request to test and perform the setup necessary for a rename.

    @since 3.16 - support for default behavior */
    std::optional<PrepareRenameResult> prepareRename(PrepareRenameParams);
    /** A request to provide folding ranges in a document. The request's
    parameter is of type {@link FoldingRangeParams}, the
    response is of type {@link FoldingRangeList} or a Thenable
    that resolves to such. */
    std::optional<std::vector<FoldingRange>> foldingRange(FoldingRangeParams);
    /** A request to resolve the supertypes for a given `TypeHierarchyItem`.

    @since 3.17.0 */
    std::optional<std::vector<TypeHierarchyItem>> supertypes(
            TypeHierarchySupertypesParams);
    /** A request to resolve a command for a given code lens. */
    CodeLens resolve(CodeLens);
    /** A request to provide inline completions in a document. The request's
    parameter is of type {@link InlineCompletionParams}, the response is of type
    {@link InlineCompletion InlineCompletion[]} or a Thenable that resolves to
    such.

    @since 3.18.0
    @proposed */
    std::variant<InlineCompletionList,
                 std::vector<InlineCompletionItem>,
                 std::monostate>
            inlineCompletion(InlineCompletionParams);
    /** The did delete files notification is sent from the client to the server
    when files were deleted from within the client.

    @since 3.16.0 */
    std::optional<WorkspaceEdit> willDeleteFiles(DeleteFilesParams);
    /** The configuration change notification is sent from the client to the
    server when the client's configuration has changed. The notification
    contains the changed configuration as defined by the language client. */
    void didChangeConfiguration(DidChangeConfigurationParams);
    /** Request to resolve additional information for a given completion
    item.The request's parameter is of type {@link CompletionItem} the response
    is of type {@link CompletionItem} or a Thenable that resolves to such. */
    CompletionItem resolve(CompletionItem);
    void setTrace(SetTraceParams);
    /** A request to provide commands for the given text document and range. */
    std::optional<std::vector<std::variant<Command, CodeAction>>> codeAction(
            CodeActionParams);
    /** A request to list all presentation for a color. The request's
    parameter is of type {@link ColorPresentationParams} the
    response is of type {@link ColorInformation ColorInformation[]} or a
    Thenable that resolves to such. */
    std::vector<ColorPresentation> colorPresentation(ColorPresentationParams);
    /** A notification sent when a notebook closes.

    @since 3.17.0 */
    void didClose(DidCloseNotebookDocumentParams);
    /** A document will save notification is sent from the client to the server
    before the document is actually saved. */
    void willSave(WillSaveTextDocumentParams);
    /** The workspace diagnostic request definition.

    @since 3.17.0 */
    WorkspaceDiagnosticReport diagnostic(WorkspaceDiagnosticParams);
    /** A request to provide ranges that can be edited together.

    @since 3.16.0 */
    std::optional<LinkedEditingRanges> linkedEditingRange(
            LinkedEditingRangeParams);
    /** @since 3.16.0 */
    std::variant<SemanticTokens, SemanticTokensDelta, std::monostate>
            semanticTokensfulldelta(SemanticTokensDeltaParams);
    /** A request to format a range in a document. */
    std::optional<std::vector<TextEdit>> rangeFormatting(
            DocumentRangeFormattingParams);
    /** Request to resolve additional information for a given code action.The
    request's parameter is of type {@link CodeAction} the response is of type
    {@link CodeAction} or a Thenable that resolves to such. */
    CodeAction resolve(CodeAction);
    /** A request to resolve the incoming calls for a given `CallHierarchyItem`.

    @since 3.16.0 */
    std::optional<std::vector<CallHierarchyIncomingCall>> incomingCalls(
            CallHierarchyIncomingCallsParams);
    /** A document will save request is sent from the client to the server
    before the document is actually saved. The request can return an array of
    TextEdits which will be applied to the text document before it is saved.
    Please note that clients might drop results if computing the text edits took
    too long or if a server constantly fails on this request. This is done to
    keep the save fast and reliable. */
    std::optional<std::vector<TextEdit>> willSaveWaitUntil(
            WillSaveTextDocumentParams);
};
} // namespace lsp
