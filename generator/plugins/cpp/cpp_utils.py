# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import subprocess
from functools import cache
from pathlib import Path

import generator.model as model

from .cpp_grouping import ModelSymbol, RootSymbolGroup, SymbolBasket
from .cpp_writer import CppWriter, get_route_return, lsp_to_cpp_type

COMMON_INCLUDES = [
    "<variant>",
    "<optional>",
    "<vector>",
    "JsonTypes.h",
    "URI.h",
    "<rfl/json.hpp>",
]
LSP_TYPES = "LspTypes.h"

METHODMAP = {
    "textDocument": "Doc",
    "notebookDocument": "notebook",
}


def get_route_name(req: model.Request | model.Notification) -> str:
    method = req.method.split("/")
    # remap some long names
    method = [METHODMAP.get(part, part) for part in method]
    # convert first char of each to upper
    method = [part[0].upper() + part[1:] for part in method]

    method[0] = method[0].replace("$", "")

    # Client has a bunch of methods with no results, which imo should probably be notifications

    method_name = "".join(method)
    # if method_name == "getWorkspaceSemanticTokensRefresh":
    #     breakpoint()
    return method_name


def get_prefix(req: model.Request | model.Notification) -> str:
    prefix = "on" if (isinstance(req, model.Notification)) else "get"
    return prefix


def generate_from_spec(spec: model.LSPModel, output_dir: str, test_dir: str) -> None:
    # Visit all the types to figure out how to split them up by route

    # Build dependency graph
    basket = SymbolBasket()
    basket.add_all(spec)
    basket.connect()

    # Group routes by their path
    routes = list(spec.requests) + list(spec.notifications)
    root = RootSymbolGroup("root")
    for req in routes:
        root.add_route(req.method, req)

    remaining_syms: dict[str, ModelSymbol] = {
        v.name: v.underlying for v in basket.syms.values()
    }

    # Group symbols into chunks based on their path
    # Just group everything together for now. If needed can split up types

    server_writer = CppWriter(
        Path(output_dir) / "LspServer.h",
        includes=COMMON_INCLUDES + [LSP_TYPES] + ["JsonRpcServer.h"],
    )

    client_writer = CppWriter(
        Path(output_dir) / "LspClient.h",
        includes=COMMON_INCLUDES + [LSP_TYPES] + ["JsonRpc.h"],
    )

    groups = list(root.iter_groups(100))
    assert len(groups) == 1
    path, group = groups[0]

    # virtual lsp::InitializeResult initialize(const lsp::InitializeParams&);

    # Add routes to group basket
    out_path = Path(output_dir)
    rel_path = path[1:]
    if rel_path == "$":
        rel_path = "Tracing"
    if rel_path == "":
        rel_path = "LspTypes"

    print(out_path / Path(f"{rel_path}.h"))
    header_path = f"{rel_path}.h"

    lsp_types_writer = CppWriter(
        out_path / Path(header_path),
        includes=COMMON_INCLUDES,
    )
    # impl_writer = CppWriter(out_path / Path(f"{rel_path}.cpp"), is_impl=True)
    # Get their strict deps (depended on by only symbols in this group)
    # Write symbols in topological order
    server_syms = list[model.Request | model.Notification]()
    client_syms = list[model.Request | model.Notification]()

    for sym in basket.get_strict_deps(group.iter_routes(), include_all=True):
        print(f"  {sym}")
        un = sym.underlying
        if isinstance(un, model.Notification | model.Request):
            if un.messageDirection in ["clientToServer", "both"]:
                server_syms.append(un)
            if un.messageDirection in ["serverToClient", "both"]:
                client_syms.append(un)
        else:
            lsp_types_writer.write_symbol(un)

        # Remove from common
        del remaining_syms[sym.name]

    lsp_types_writer.close()

    with server_writer.curly(
        "template<typename Impl>\nclass LspServer: public JsonRpcServer<Impl>"
    ):
        server_writer.write("protected:")
        for sym in server_syms:
            prefix = get_prefix(sym)
            name = get_route_name(sym)
            implMethod = prefix + name
            server_writer.write_method_header(sym, implMethod)
            with server_writer.curly(f"void register{name}()"):
                params = sym.params.name if sym.params else "std::nullopt_t"
                if isinstance(sym, model.Request):
                    server_writer.writeln(
                        f'this->template registerMethod<{params}, {get_route_return(sym)}, &Impl::{implMethod}>("{sym.method}");'
                    )
                else:
                    server_writer.writeln(
                        f'this->template registerNotification<{params}, &Impl::{implMethod}>("{sym.method}");'
                    )

        # Binding code
        # server_writer.writeln("public:")

        # with server_writer.curly("void registerRpcMethods()"):
        #     #     if constexpr (HasImpl<MyServer, int, void, &MyServer::initialized>) {
        #     # std::cout << "MyServer implements initialized(int) -> void\n";
        #     for sym in server_syms:
        #         name = get_route_name(sym)
        #         return_type = get_route_return(sym)
        #         if isinstance(sym, model.Request):
        #             params = sym.params.name if sym.params else "void"
        #             server_writer.writeln(
        #                 f'this->template registerMethod<{params}, {return_type}, &Impl::{name}>("{sym.method}");'
        #             )
        #         else:
        #             params = sym.params.name if sym.params else "void"
        #             server_writer.writeln(
        #                 f'this->template registerNotification<{params}, &Impl::{name}>("{sym.method}");'
        #             )

    with client_writer.curly("class LspClient"):
        client_writer.writeln("public:")
        for sym in client_syms:
            client_writer.write_client_route(sym, get_prefix(sym) + get_route_name(sym))

    server_writer.close()
    client_writer.close()

    # Gather basket for common.h
    # common_basket = SymbolBasket()
    # for sym in remaining_syms.values():
    #     common_basket.add_symbol(sym)
    # common_basket.connect()

    # Write common symbols
    # common_writer = CppWriter(Path(output_dir) / "common.h")
    # common_writer.writeln()

    # Assert no remaining deps
    if len(remaining_syms) > 0:
        print("Remaining symbols:")
        for sym in remaining_syms:
            print(f"  {sym}")
        raise ValueError("Remaining symbols with cycles, add them to the special file")

    # Copy custom cpp
    subprocess.run(
        "cp generator/plugins/cpp/rfl/* packages/cpp/", shell=True, check=True
    )

    subprocess.run("clang-format packages/cpp/**.h -i", shell=True, check=True)
