/// @generated via `python -m generator --plugin cpp`

#pragma once
#include <variant>

#include "json_types.h"
#include "lsptypes.h"

namespace lsp {

class Client {
    /** The show message notification is sent from a server to a client to ask
    the client to display a particular message in the user interface. */
    void showMessage(ShowMessageParams);
    void progress(ProgressParams);
    /** The telemetry event notification is sent from the server to the client
    to ask the client to log telemetry data. */
    void event(LSPAny);
    /** The `window/workDoneProgress/create` request is sent from the server to
    the client to initiate progress reporting from the server. */
    std::monostate workDoneProgresscreate(WorkDoneProgressCreateParams);
    /** The `workspace/workspaceFolders` is sent from the server to the client
     * to fetch the open workspace folders. */
    std::variant<std::vector<WorkspaceFolder>, std::monostate>
    workspaceFolders();
    /** @since 3.17.0 */
    std::monostate inlayHintrefresh();
    /** The show message request is sent from the server to the client to show a
    message and a set of options actions to the user. */
    std::variant<MessageActionItem, std::monostate> showMessageRequest(
            ShowMessageRequestParams);
    /** The `client/unregisterCapability` request is sent from the server to the
    client to unregister a previously registered capability handler on the
    client side. */
    std::monostate unregisterCapability(UnregistrationParams);
    /** @since 3.18.0
    @proposed */
    std::monostate foldingRangerefresh();
    /** A request sent from the server to the client to modified certain
     * resources. */
    ApplyWorkspaceEditResult applyEdit(ApplyWorkspaceEditParams);
    /** A request to show a document. This request might open an
    external program depending on the value of the URI to open.
    For example a request to open `https://code.visualstudio.com/`
    will very likely open the URI in a WEB browser.

    @since 3.16.0 */
    ShowDocumentResult showDocument(ShowDocumentParams);
    /** The 'workspace/configuration' request is sent from the server to the
    client to fetch a certain configuration setting.

    This pull model replaces the old push model were the client signaled
    configuration change via an event. If the server still needs to react to
    configuration changes (since the server caches the result of
    `workspace/configuration` requests) the server should register for an empty
    configuration change event and empty the cache if such an event is received.
  */
    std::vector<LSPAny> configuration(ConfigurationParams);
    void logTrace(LogTraceParams);
    /** A request to refresh all code actions

    @since 3.16.0 */
    std::monostate codeLensrefresh();
    /** The diagnostic refresh request definition.

    @since 3.17.0 */
    std::monostate diagnosticrefresh();
    /** The `workspace/textDocumentContent` request is sent from the server to
    the client to refresh the content of a specific text document.

    @since 3.18.0
    @proposed */
    std::monostate textDocumentContentrefresh(TextDocumentContentRefreshParams);
    /** The log message notification is sent from the server to the client to
    ask the client to log a particular message. */
    void logMessage(LogMessageParams);
    void cancelRequest(CancelParams);
    /** @since 3.16.0 */
    std::monostate semanticTokensrefresh();
    /** The `client/registerCapability` request is sent from the server to the
    client to register a new capability handler on the client side. */
    std::monostate registerCapability(RegistrationParams);
    /** @since 3.17.0 */
    std::monostate inlineValuerefresh();
    /** Diagnostics notification are sent from the server to the client to
    signal results of validation runs. */
    void publishDiagnostics(PublishDiagnosticsParams);
};
} // namespace lsp
