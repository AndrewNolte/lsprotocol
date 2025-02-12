# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import re
from contextlib import contextmanager
from pathlib import Path

import generator.model as model

PARTS_RE = re.compile(r"(([a-z0-9])([A-Z]))")


def get_parts(name: str) -> list[str]:
    name = name.replace("_", " ")
    return PARTS_RE.sub(r"\2 \3", name).split()


def to_pascal_case(name: str) -> str:
    return "".join([c.capitalize() for c in get_parts(name)])


def lsp_to_base_types(lsp_type: model.BaseType):
    match lsp_type.name:
        case "string" | "RegExp":
            return "std::string"
        case "DocumentUri" | "URI":
            return "std::string"
        case "decimal":
            return "float"
        case "integer":
            return "int"
        case "uinteger":
            return "uint"
        case "boolean":
            return "bool"
        case "null":
            return "std::monostate"

    raise ValueError(f"Unknown base type: {lsp_type.name}")


def write_docs(func):
    def wrapper(self, *args, **kwargs):
        if args[0].documentation is not None:
            self.block_comment(args[0].documentation)
        func(self, *args, **kwargs)

    return wrapper


def lsp_to_cpp_type(t: model.Type) -> str:
    if t is None:
        return "void"
    match type(t):
        case model.BaseType:
            return lsp_to_base_types(t)
        case model.ReferenceType:
            return t.name
        case model.ArrayType:
            return f"std::vector<{lsp_to_cpp_type(t.element)}>"
        case model.MapType:
            return f"flat_hash_map<std::string, {lsp_to_cpp_type(t.value)}>"
        case model.OrType:
            subtypes = [lsp_to_cpp_type(sub_t) for sub_t in t.items]
            if len(subtypes) == 2 and "std::monostate" in subtypes:
                subtypes.remove("std::monostate")
                return f"std::optional<{subtypes[0]}>"
            return f"std::variant<{', '.join(subtypes)}>"
        case model.TupleType:
            return f"std::tuple<{', '.join([lsp_to_cpp_type(sub_t) for sub_t in t.items])}>"
        case model.LiteralType:
            return "void"
        case model.StringLiteralType:
            return f"std::string /* = '{t.value}*/"
        case _:
            print(f"Unknown type: {t}")
            return t.name

    return "void"


class CppWriter:
    """
    1 <-> 1 relationship with a cpp file that is written.
    It knows how to write symbols to cpp/h files.
    """

    def __init__(  # pylint: disable=dangerous-default-value
        self,
        file: Path | str,
        is_impl: bool = False,
        includes: list[str] = [],
    ) -> None:
        output_folder = Path(file).parent
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)

        # Config
        self.is_impl = is_impl
        self.namespace = "lsp"

        # State tracking
        self.indent_level = 0
        self.current_line = 0

        # Open the file for writing
        self.file = open(file, "w", encoding="utf-8")
        self.writeln(f"/// @gene{'rated'} via `python -m generator --plugin cpp`")
        self.writeln()
        if is_impl is False:
            self.writeln("#pragma once")

        for inc in includes:
            if inc.startswith("<"):
                self.writeln(f"#include {inc}")
            else:
                self.writeln(f'#include "{inc}"')

        self.writeln()

        if is_impl is False:
            self.writeln(f"namespace {self.namespace} {{")

        self.writeln()

    def write(self, s: str):
        self.file.write(s)
        self.current_line += s.count("\n")

    def writeln(self, s: str = ""):
        self.file.write("    " * self.indent_level + s + "\n")
        self.current_line += 1

    def get_current_line_number(self) -> int:
        return self.current_line

    def close(self):
        if self.is_impl is False:
            self.writeln("} // namespace lsp")
        self.file.close()

    @contextmanager
    def indent(self):
        """
        Indent the code block by one level for this context
        """
        self.indent_level += 1
        yield
        self.indent_level -= 1

    def block_comment(self, comment: str):
        """
        Write a comment line
        """
        self.write("/** " + comment + " */" + "\n")

    @contextmanager
    def curly(self, before: str):
        """
        Write a block of code surrounded by curly braces
        """
        self.write(before)
        self.writeln(" {")
        with self.indent():
            yield
        self.writeln("};")

    @write_docs
    def write_enum(self, enum: model.Enum):
        """
        Write an enum to the file
        """
        # Make header
        header = f"enum class {enum.name}"
        enum_type = enum.type.name
        match enum_type:
            case "string" | "uinteger":
                # All unisgned enums are small atm
                header += " : uint8_t"
            case "integer":
                header += " : int32_t"
            case _:
                raise ValueError(f"Unknown enum type: {enum.type}")

        # Write body
        with self.curly(header):
            if enum_type == "string":
                for member in enum.values:
                    member.name = to_pascal_case(member.name)
                    self.writeln(f"{member.name},")
            else:
                for member in enum.values:
                    self.writeln(f"{member.name} = {member.value},")

        # Write converters
        if enum_type == "string":
            with self.curly("std::string_view toString(" + enum.name + " value)"):
                # with self.curly("switch (value)"):
                self.writeln("switch (value) {")
                for member in enum.values:
                    self.writeln(
                        f'case {enum.name}::{member.name}: return "{member.value}";'
                    )
                self.writeln('default: return "";')

                self.writeln("}")

            # Enums almost always go server -> client, so we don't need to make parsers
        self.writeln("")

    @write_docs
    def write_property(self, member: model.Property) -> None:
        self.writeln(f"{lsp_to_cpp_type(member.type)} {member.name};")

    @write_docs
    def write_struct(self, struct: model.Structure) -> None:
        # Check for inheritance
        if struct.extends:
            base_classes = ", ".join(base.name for base in struct.extends)
            header = f"struct {struct.name} : {base_classes}"
        else:
            header = f"struct {struct.name}"

        with self.curly(header):
            for member in struct.properties:
                self.write_property(member)

    @write_docs
    def write_type_alias(self, type_alias: model.TypeAlias) -> None:
        self.writeln(f"using {type_alias.name} = {lsp_to_cpp_type(type_alias.type)};")

    def get_register_method(self, req: model.Request | model.Notification) -> str:
        res_str = (
            lsp_to_cpp_type(req.result) if isinstance(req, model.Request) else "void"
        )
        params_str = lsp_to_cpp_type(req.params)

        method_str = req.method
        if "/" in method_str:
            method_str = "".join(method_str.split("/")[1:])
        method_str = method_str[0].upper() + method_str[1:]
        return f"void register{method_str}Provider(std::function<{res_str}({params_str})> method)"

    def get_method(self, req: model.Request | model.Notification) -> str:
        res_str = (
            lsp_to_cpp_type(req.result) if isinstance(req, model.Request) else "void"
        )
        if res_str == "nullptr":
            res_str = "void"
        params_str = lsp_to_cpp_type(req.params)
        if params_str == "void":
            params_str = ""

        method_str = req.method
        if "/" in method_str:
            method_str = "".join(method_str.split("/")[1:])
        return f"{res_str} {method_str}({params_str})"

    @write_docs
    def write_register_header(self, req: model.Request | model.Notification) -> None:
        # Write the method

        # make void register<req.method>(c: void (*)(const req&)) -> <req.result>);

        self.writeln(self.get_register_method(req) + ";")

    def write_register_impl(self, req: model.Request | model.Notification) -> None:
        # Write the method
        with self.curly(self.get_register_method(req)):
            # Add capability to initialization struct
            self.writeln("// TODO: Implement me (serdes)")
            # Record method in incoming method map

    @write_docs
    def write_method_header(self, req: model.Request | model.Notification) -> None:
        # Write the method
        self.writeln(self.get_method(req) + ";")

    @write_docs
    def write_method_impl(self, req: model.Request | model.Notification) -> None:
        # Write the method
        with self.curly(self.get_method(req)):
            # Add capability to initialization struct
            self.writeln("// TODO: Implement me (business logic)")
            # Record method in incoming method map

    def write_symbol(self, sym: model.Structure | model.Enum | model.TypeAlias):
        match type(sym):
            case model.Structure:
                self.write_struct(sym)
            case model.Enum:
                self.write_enum(sym)
            case model.TypeAlias:
                self.write_type_alias(sym)
            case model.BaseType:
                # These are raw cpp types, no need to write
                pass
            case _:
                breakpoint()
                print(f"Unknown symbol type: {sym}, skipping writing")

        self.writeln()
