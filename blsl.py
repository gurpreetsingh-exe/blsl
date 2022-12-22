#!/usr/bin/python
import sys
from enum import Enum, auto
from typing import List, Dict


def usage(arg0: str):
    print(f'Usage: {arg0} [options] input')
    print("\nOptions:")
    print("  -h, --help        display help information")
    exit(1)


class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value


class TokenKind(Enum):
    Ident = auto()

    Int = auto()
    Void = auto()
    Vec4 = auto()

    Const = auto()
    In = auto()
    Out = auto()
    InOut = auto()

    LParen = auto()
    RParen = auto()
    LBrace = auto()
    RBrace = auto()
    Comma = auto()


keywords: Dict[str, TokenKind] = {
    'int': TokenKind.Int,
    'void': TokenKind.Void,
    'vec4': TokenKind.Vec4,
    'const': TokenKind.Const,
    'in': TokenKind.In,
    'out': TokenKind.Out,
    'inout': TokenKind.InOut,
}


class StorageQualifier(Enum):
    Const = auto()
    In = auto()
    Out = auto()
    InOut = auto()


storage_qualifiers: Dict[TokenKind, StorageQualifier] = {
    TokenKind.Const: StorageQualifier.Const,
    TokenKind.In: StorageQualifier.In,
    TokenKind.Out: StorageQualifier.Out,
    TokenKind.InOut: StorageQualifier.InOut,
}


class TypeKind(Enum):
    Int = auto()
    Void = auto()
    Vec4 = auto()


def get_ty(kind: TokenKind) -> TypeKind | None:
    match kind:
        case TokenKind.Int: return TypeKind.Int
        case TokenKind.Void: return TypeKind.Void
        case TokenKind.Vec4: return TypeKind.Vec4


punc: Dict[str, TokenKind] = {
    '(': TokenKind.LParen,
    ')': TokenKind.RParen,
    '{': TokenKind.LBrace,
    '}': TokenKind.RBrace,
    ',': TokenKind.Comma,
}


def tokenize(src: str) -> List[Token]:
    tokens: List[Token] = []

    def add_token(kind: TokenKind, begin: int, end: int):
        val: str = src[begin:end]
        if kind == TokenKind.Ident and val in keywords:
            kind = keywords[val]
        tokens.append(Token(kind, val))

    i = 0
    while i < len(src):
        c = src[i]
        if c.isspace():
            i += 1
        elif c.isalpha():
            begin = i
            while i < len(src) and src[i].isalnum():
                i += 1
            add_token(TokenKind.Ident, begin, i)
        elif c in punc:
            add_token(punc[c], i, i + 1)
            i += 1
        else:
            i += 1

    return tokens


class Def:
    def __init__(self, kind):
        self.kind = kind


class Ty:
    def __init__(self, kind: TypeKind):
        self.kind = kind


class Ident:
    def __init__(self, name: str):
        self.name = name


class TyQualifier:
    pass


class Storage(TyQualifier):
    def __init__(self, kind: StorageQualifier):
        self.kind = kind


class FnArg:
    def __init__(self, name: Ident, ty: Ty, ty_qualifier: TyQualifier):
        self.name = name
        self.ty = ty
        self.ty_qualifier = ty_qualifier


class Block:
    def __init__(self):
        pass


class Fn:
    def __init__(self, name: Ident, args: List[FnArg], ret_ty: Ty, body: Block):
        self.name = name
        self.args = args
        self.ret_ty = ret_ty
        self.body = body


class Module:
    def __init__(self, defs: List[Def]):
        self.defs = defs


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.tokens_len = len(self.tokens)
        self.t = self.tokens[self.i]

    def eat(self):
        if self.i < self.tokens_len - 1:
            self.i += 1
            self.t = self.tokens[self.i]
        else:
            self.t = None

    def expect(self, kind: TokenKind) -> Token:
        if self.t.kind == kind:
            t = self.t
            self.eat()
            return t
        else:
            assert False, f"expected `{kind}`, found `{self.t.kind}`"

    def parse_ty(self) -> Ty:
        match ty := get_ty(self.t.kind):
            case None:
                assert False, 'expected type'
            case _:
                self.eat()
                return Ty(ty)

    def parse_ident(self) -> Ident:
        return Ident(self.expect(TokenKind.Ident).value)

    def parse_storage_qualifier(self) -> Storage | None:
        kind = self.t.kind
        if kind in storage_qualifiers:
            self.eat()
            return Storage(storage_qualifiers[kind])

    def parse_ty_qualifier(self) -> List[TyQualifier]:
        qualifiers: List[TyQualifier] = []
        while True:
            if qualifier := self.parse_storage_qualifier():
                qualifiers.append(qualifier)
            else:
                break
        return qualifiers

    def parse_fn_arg(self) -> FnArg:
        ty_qualifier = self.parse_ty_qualifier()
        ty = self.parse_ty()
        name = self.parse_ident()
        return FnArg(name, ty, ty_qualifier)

    def parse_fn_args(self) -> List[FnArg]:
        self.expect(TokenKind.LParen)
        args: List[FnArg] = []
        while self.t and self.t.kind != TokenKind.RParen:
            args.append(self.parse_fn_arg())
            if self.t.kind == TokenKind.Comma:
                self.eat()
            else:
                break
        self.expect(TokenKind.RParen)
        return args

    def parse_block(self) -> Block:
        self.expect(TokenKind.LBrace)
        self.expect(TokenKind.RBrace)
        return Block()

    def parse_def(self) -> Def:
        ty = self.parse_ty()
        ident = self.parse_ident()
        if self.t.kind == TokenKind.LParen:
            args = self.parse_fn_args()
            block = self.parse_block()
            return Def(Fn(ident, args, ty, block))
        else:
            assert False, 'expected function definition'

    def parse(self) -> Module:
        defs: List[Def] = []
        while self.t:
            defs.append(self.parse_def())
        return Module(defs)


def main(argv: List[str]):
    arg0 = argv[0]
    argv = argv[1:]
    if not argv:
        usage(arg0)
    file = argv[0]
    with open(file, 'r') as f:
        src = f.read()
        tokens = tokenize(src)
        parser = Parser(tokens)
        ast = parser.parse()
        print(ast)


if __name__ == "__main__":
    main(sys.argv)
