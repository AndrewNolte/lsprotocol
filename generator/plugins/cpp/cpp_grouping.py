from dataclasses import dataclass, field
from typing import Iterable, TypeAlias

import generator.model as model

BASE_TYPES = {
    "URI",
    "DocumentUri",
    "integer",
    "uinteger",
    "decimal",
    "RegExp",
    "string",
    "boolean",
    "null",
}


CYCLICAL_TYPES = {
    "LSPAny",
    "LSPObject",
    "LSPArray",
}


def get_deps(
    t: model.LSP_TYPE_SPEC
    | model.Structure
    | model.Request
    | model.Notification
    | None,
) -> set[str]:
    """
    Recurse through the given type to get direct dependencies
    """
    if t is None:
        return set()
    if hasattr(t, "deprecated") and t.deprecated:
        return set()
    match type(t):
        case model.BaseType:
            # return {t.name}
            return set()
        case model.ReferenceType:
            if t.name in CYCLICAL_TYPES:
                return set()
            return {t.name}
        case model.OrType:
            return set.union(*(get_deps(sub_t) for sub_t in t.items))
        case model.ArrayType:
            return get_deps(t.element)
        case model.MapType:
            return get_deps(t.value)
        case model.LiteralType:
            return set()
        case model.StringLiteralType:
            return set()
        case model.TupleType:
            return set.union(*(get_deps(sub_t) for sub_t in t.items))
        case model.Structure:
            s = set()
            if t.deprecated:
                return s
            for member in t.properties:
                if member.deprecated is not None:
                    continue
                s.update(get_deps(member.type))
            for parent in t.extends + t.mixins:
                s.add(parent.name)
            return s
        case model.Request:
            return set.union(
                *(get_deps(member) for member in [t.params, t.result, t.partialResult])
            )
        case model.Notification:
            return get_deps(t.params)
        case _:
            raise ValueError(f"Unknown type: {t}")


ModelSymbol: TypeAlias = (
    model.LSP_TYPE_SPEC
    | model.Structure
    | model.Request
    | model.Notification
    | model.Enum
    | model.TypeAlias
    | model.BaseType
)


def get_name(t: ModelSymbol) -> str:
    if isinstance(t, model.Request | model.Notification):
        return t.method
    elif isinstance(t, str):
        return t
    return t.name


class Symbol:
    """
    Represents symbols in lsp.json and their dep/ref relationships
    """

    underlying: (
        model.Structure
        | model.Enum
        | model.TypeAlias
        | model.Request
        | model.Notification
    )

    # Symbols that this symbol depends on
    deps: set["Symbol"] = field(default_factory=set)

    # Symbols that depend on this symbol
    refs: set["Symbol"] = field(default_factory=set)

    def __init__(self, underlying):
        self.underlying = underlying
        self.refs = set()
        self.deps = set()
        if isinstance(self.underlying, str):
            if self.underlying in BASE_TYPES:
                self.underlying = model.BaseType(kind="base", name=self.underlying)
            else:
                raise ValueError(f"Unknown symbol: {self.underlying}")
            # raise ValueError("Underlying symbol cannot be None")

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def name(self):
        if isinstance(self.underlying, model.Request | model.Notification):
            return self.underlying.method
        return self.underlying.name

    def __str__(self) -> str:
        return f"{self.name}: {type(self.underlying).__name__}"

    def __repr__(self) -> str:
        return str(self)

    def dump(self, depth: int = 5):
        printed = set()
        to_print = set([self])
        while to_print and depth > 0:
            n_set = set()
            for sym in to_print:
                print(sym)
                printed.add(sym)
                for ref in sym.refs | sym.deps:
                    if ref not in printed:
                        n_set.add(ref)
            depth -= 1
            to_print = n_set
            print()


class SymbolBasket:
    """
    Graph algorithms for the symbols
    """

    def __init__(self):
        self.syms: dict[str, Symbol] = dict()

    def add_symbol(self, sym: ModelSymbol):
        self.syms[get_name(sym)] = Symbol(sym)

    def add_all(self, spec: model.LSPModel) -> None:
        for t in BASE_TYPES:
            self.syms[t] = Symbol(model.BaseType(kind="base", name=t))
        for enum in spec.enumerations:
            self.syms[enum.name] = Symbol(enum)
        for type_alias in spec.typeAliases:
            if type_alias.name in CYCLICAL_TYPES:
                continue
            self.syms[type_alias.name] = Symbol(type_alias)
        for struct in spec.structures:
            self.syms[struct.name] = Symbol(struct)
        for req in spec.requests:
            self.syms[req.method] = Symbol(req)
        for notif in spec.notifications:
            self.syms[notif.method] = Symbol(notif)

    def connect(self) -> None:
        # Add deps
        for sym in self.syms.values():
            un = sym.underlying
            match type(sym.underlying):
                case model.Structure:
                    self.syms[un.name].deps = {
                        self.syms[ref] for ref in get_deps(un)
                    } - {self.syms[un.name]}
                case model.TypeAlias:
                    self.syms[sym.name].deps = {
                        self.syms[ref] for ref in get_deps(un.type)
                    }
                case model.Request:
                    self.syms[un.method].deps = {self.syms[ref] for ref in get_deps(un)}
                case model.Notification:
                    self.syms[un.method].deps = {self.syms[ref] for ref in get_deps(un)}

        # Add Refs
        for sym in self.syms.values():
            for dep in sym.deps:
                dep.refs.add(sym)

    def get_strict_deps(
        self, syms: list[ModelSymbol], include_all=False
    ) -> list[Symbol]:
        """ "
        Get the set of symbols that are depended on by only the given set of symbols. Returns a list in topological order
        """
        strict_deps: set[Symbol] = set(self.syms[get_name(sym)] for sym in syms)

        if len(strict_deps) == 0 or include_all:
            # Add symbols with no references
            for sym in self.syms.values():
                if len(sym.refs) == 0:
                    strict_deps.add(sym)

        s_len = 0
        order_deps = sorted(list(strict_deps), key=lambda x: x.name)
        # Frontier expand deps
        while True:
            if len(strict_deps) == s_len:
                break
            s_len = len(strict_deps)
            # Add all symbols that have all their refs in this group already
            n_strict_deps = set()
            for s in strict_deps:
                for dep in s.deps:
                    if all(ref in strict_deps for ref in dep.refs):
                        n_strict_deps.add(dep)

            # set only impl-
            # strict_deps |= n_strict_deps
            for dep in sorted(n_strict_deps, key=lambda x: x.name):
                if dep not in strict_deps:
                    strict_deps.add(dep)
                    order_deps.append(dep)

        return order_deps[::-1]

    def get_syms(self) -> dict[str, ModelSymbol]:
        return {k: v.underlying for k, v in self.syms.items()}


@dataclass
class SymbolGroup:
    name: str
    tot_routes: int = 0
    routes: list[model.Request | model.Notification] = field(default_factory=list)
    children: dict[str, "SymbolGroup"] = field(default_factory=dict)

    def add_route(self, name: str, route: model.Request | model.Notification):
        self.tot_routes += 1
        if name == "":
            self.routes.append(route)
            return

        sp = name.split("/")
        bn = sp[0]

        if bn not in self.children:
            self.children[bn] = SymbolGroup(bn)
        self.children[bn].add_route("/".join(sp[1:]), route)

    def iter_routes(self) -> Iterable[model.Request | model.Notification]:
        for route in self.routes:
            yield route
        for child in self.children.values():
            yield from child.iter_routes()

    def print_tree(self, tabs: int = 0) -> None:
        print(" " * tabs + self.name + f" ({self.tot_routes})")
        for route in self.routes:
            print(" " * (tabs + 4) + route.method)
        for child in self.children.values():
            child.print_tree(tabs + 4)

    def iter_groups(
        self, max_count: int, path=""
    ) -> Iterable[tuple[str, "SymbolGroup"]]:
        """
        yield groups of routes that have less than max_count routes
        """
        if self.tot_routes < max_count:
            yield path, self
        else:
            for child in self.children.values():
                yield from child.iter_groups(max_count, path + "/" + child.name)


RESOLVE_MAP = {
    "completionItem": "textDocument",
    "workspaceSymbol": "workspace",
    "codeLens": "textDocument",
    "inlayHint": "textDocument",
    "documentLink": "textDocument",
    "codeAction": "textDocument",
}


class RootSymbolGroup(SymbolGroup):
    def add_route(self, name: str, route: model.Request | model.Notification):
        if name.endswith("/resolve"):
            bn = name.split("/")[0]
            folder = RESOLVE_MAP.get(bn, bn)
            super().add_route(f"{folder}/{name}", route)
            return
        return super().add_route(name, route)
