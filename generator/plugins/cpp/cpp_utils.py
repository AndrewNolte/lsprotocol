# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import subprocess
from pathlib import Path

import generator.model as model

from .cpp_grouping import ModelSymbol, RootSymbolGroup, SymbolBasket
from .cpp_writer import CppWriter

COMMON_INCLUDES = [
    "<variant>",
    "<optional>",
    "<vector>",
    "json_types.h",
]
LSP_TYPES = "lsptypes.h"


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
        Path(output_dir) / "server.h",
        includes=COMMON_INCLUDES + [LSP_TYPES],
    )

    client_writer = CppWriter(
        Path(output_dir) / "client.h",
        includes=COMMON_INCLUDES + [LSP_TYPES],
    )

    groups = list(root.iter_groups(100))
    assert len(groups) == 1
    path, group = groups[0]

    with server_writer.curly("class Server"), client_writer.curly("class Client"):
        # Add routes to group basket
        out_path = Path(output_dir)
        rel_path = path[1:]
        if rel_path == "$":
            rel_path = "tracing"
        if rel_path == "":
            rel_path = "lsptypes"

        print(out_path / Path(f"{rel_path}.h"))
        header_path = f"{rel_path}.h"

        lsp_types_writer = CppWriter(
            out_path / Path(header_path),
            includes=COMMON_INCLUDES,
        )
        # impl_writer = CppWriter(out_path / Path(f"{rel_path}.cpp"), is_impl=True)
        # Get their strict deps (depended on by only symbols in this group)
        # Write symbols in topological order

        for sym in basket.get_strict_deps(group.iter_routes(), include_all=True):
            print(f"  {sym}")
            un = sym.underlying
            if isinstance(un, model.Notification | model.Request):
                if un.messageDirection in ["clientToServer", "both"]:
                    server_writer.write_method_header(un)
                if un.messageDirection in ["serverToClient", "both"]:
                    client_writer.write_method_header(un)
            else:
                lsp_types_writer.write_symbol(un)

            # Remove from common
            del remaining_syms[sym.name]

        lsp_types_writer.close()

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
        "cp generator/plugins/cpp/rapidjson/* packages/cpp/", shell=True, check=True
    )

    subprocess.run("clang-format packages/cpp/**.h -i", shell=True, check=True)
