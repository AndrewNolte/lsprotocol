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


NULL_VALUE = "std::monostate"


def lsp_to_base_types(lsp_type: model.BaseType):
    match lsp_type.name:
        case "string" | "RegExp":
            return "std::string"
        case "DocumentUri" | "URI":
            return "URI"
        case "decimal":
            return "float"
        case "integer":
            return "int"
        case "uinteger":
            return "uint"
        case "boolean":
            return "bool"
        case "null":
            return NULL_VALUE

    raise ValueError(f"Unknown base type: {lsp_type.name}")


def write_docs(func):
    def wrapper(self, *args, **kwargs):
        if args[0].documentation is not None:
            self.block_comment(args[0].documentation)
        func(self, *args, **kwargs)
        self.writeln()

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
            return f"std::unordered_map<std::string, {lsp_to_cpp_type(t.value)}>"
        case model.OrType:
            subtypes = [lsp_to_cpp_type(sub_t) for sub_t in t.items]
            if len(subtypes) == 2 and NULL_VALUE in subtypes:
                subtypes.remove(NULL_VALUE)
                return f"std::optional<{subtypes[0]}>"
            return f"rfl::Variant<{', '.join(subtypes)}>"
        case model.TupleType:
            return f"rfl::Tuple<{', '.join([lsp_to_cpp_type(sub_t) for sub_t in t.items])}>"
        case model.LiteralType:
            return "void"
        case model.StringLiteralType:
            # return f"std::string /* = '{t.value}*/"
            return f'rfl::Literal<"{t.value}">'
        case _:
            print(f"Unknown type: {t}")
            return t.name

    return "void"


def get_route_return(req: model.Request | model.Notification) -> str:
    if isinstance(req, model.Request):
        cpp_type = lsp_to_cpp_type(req.result)
        if cpp_type == NULL_VALUE:
            return "std::monostate"
        return cpp_type
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
        self.syms: dict[str, model.Structure] = dict()

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
        # self.write("/** " + comment + " */" + "\n")
        for line in comment.split("\n"):
            self.write("/// " + line + "\n")

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
        enum_type = enum.type.name
        if enum_type == "string":  # type: ignore
            # and any(not m.value.isalnum() for m in enum.values)
            # short circuit to literal if we have a potentially bad enum name
            # TODO: maybe make a custom rfl parser instead for these?
            vlist = ", ".join(f'"{m.value}"' for m in enum.values if not m.proposed)
            self.writeln(f"using {enum.name} = rfl::Literal<{vlist}>;")

            return
        header = f"enum class {enum.name}"
        match enum_type:
            case "string":
                pass
            case "uinteger":
                # All unisgned enums are small atm
                header += " : uint8_t"
            case "integer":
                header += " : int32_t"
            case _:
                raise ValueError(f"Unknown enum type: {enum.type}")

        # Write body
        with self.curly(header):
            if enum_type == "string":
                # check for types that can't be used in enum names
                for member in enum.values:
                    self.writeln(f"{member.value},")
            else:
                for member in enum.values:
                    self.writeln(f"{member.name} = {member.value},")
            # Enums almost always go server -> client, so we don't need to make parsers
        self.writeln("")

    @write_docs
    def write_property(self, member: model.Property, parent: model.Structure) -> None:
        if member.optional:
            # SelectionRange should be the only one that does this
            wrapper_type = (
                "rfl::Box"
                if isinstance(member.type, model.ReferenceType)
                and member.type.name == parent.name
                else "std::optional"
            )
            subtype = lsp_to_cpp_type(member.type)
            if not subtype.startswith("std::optional"):
                self.writeln(f"{wrapper_type}<{subtype}> {member.name};")
                return
        self.writeln(f"{lsp_to_cpp_type(member.type)} {member.name};")

    # Used internall by write_struct
    def _write_extends(
        self, parent: model.ReferenceType, tag: str, members: set[str]
    ) -> None:
        p_symbol = self.syms[parent.name]
        for member in p_symbol.properties:
            if member.name in members:
                self.writeln(f"/// skipping {member.name} @{tag} from {parent.name}")
                continue
            self.writeln(f"/// @{tag} from {parent.name}")
            self.write_property(member, parent=parent)
            members.add(member.name)
        for gparent in p_symbol.extends:
            self._write_extends(gparent, "inherited", members)
        for gparent in p_symbol.mixins:
            self._write_extends(gparent, "mixin", members)

    @write_docs
    def write_struct(self, struct: model.Structure) -> None:
        self.syms[struct.name] = struct
        header = f"struct {struct.name}"

        with self.curly(header):
            members = set()
            for member in struct.properties:
                self.write_property(member, parent=struct)
                members.add(member.name)
            for parent in struct.extends:
                self._write_extends(parent, "inherited", members)
            for parent in struct.mixins:
                self._write_extends(parent, "mixin", members)

    @write_docs
    def write_type_alias(self, type_alias: model.TypeAlias) -> None:
        self.writeln(f"using {type_alias.name} = {lsp_to_cpp_type(type_alias.type)};")

    def get_method_signature(
        self, req: model.Request | model.Notification, name: str
    ) -> tuple[str, str]:
        # Write the method
        res_str = (
            lsp_to_cpp_type(req.result) if isinstance(req, model.Request) else "void"
        )

        params_str = lsp_to_cpp_type(req.params)

        if params_str == "void":
            params_str = "std::monostate"
        else:
            params_str = f"const {params_str}&"

        return res_str, params_str

    @write_docs
    def write_method_header(
        self, req: model.Request | model.Notification, name: str
    ) -> None:
        ret, params = self.get_method_signature(req, name)
        ret_val = "" if isinstance(req, model.Notification) else f"return {ret}{{}};"

        self.writeln(f"virtual {ret} {name}({params}) {{ {ret_val} }}")

    @write_docs
    def write_client_route(
        self, req: model.Request | model.Notification, name: str
    ) -> None:
        ret, params = self.get_method_signature(req, name)
        ret_val = "" if ret == "void" else f"return {ret}{{}};"
        if isinstance(req, model.Request):
            # TODO: Implement with async/await
            self.writeln(f" virtual {ret} {name}({params}) {{ {ret_val} }}")
        else:
            with self.curly(f"void {name}({params} params)"):
                self.writeln(
                    f'sendNotification("{req.method}", rfl::to_generic<rfl::UnderlyingEnums>(params));'
                )

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
                print(f"Unknown symbol type: {sym}, skipping writing")

        self.writeln()
