from typing import List, Dict
from .Ast import *
from .tokenizer import Token, TokenKind, tokenize


storage_qualifiers: Dict[TokenKind, StorageQualifier] = {
    TokenKind.Const: StorageQualifier.Const,
    TokenKind.In: StorageQualifier.In,
    TokenKind.Out: StorageQualifier.Out,
    TokenKind.InOut: StorageQualifier.InOut,
}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.tokens_len = len(self.tokens)
        self.t: Token = self.tokens[self.i]

    def eat(self):
        if self.i < self.tokens_len - 1:
            self.i += 1
            self.t = self.tokens[self.i]
        else:
            self.t = None  # type: ignore

    def expect(self, kind: TokenKind) -> Token:
        if self.t.kind == kind:
            t = self.t
            self.eat()
            return t
        else:
            assert False, f"expected `{kind}`, found `{self.t.kind}`"

    def parse_ty(self) -> Ty:
        match ty := self.t.kind.get_ty():
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


def parser_from_src(src: str) -> Parser:
    tokens = tokenize(src)
    return Parser(tokens)


def parser_from_file(filepath: str) -> Parser:
    with open(filepath, 'r') as f:
        src = f.read()
        return parser_from_src(src)
