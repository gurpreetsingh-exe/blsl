from typing import List, Dict
from .Ast import *
from .tokenizer import Token, TokenKind, tokenize


storage_qualifiers: Dict[TokenKind, StorageQualifier] = {
    TokenKind.Const: StorageQualifier.Const,
    TokenKind.In: StorageQualifier.In,
    TokenKind.Out: StorageQualifier.Out,
    TokenKind.InOut: StorageQualifier.InOut,
}


binary_op: Dict[TokenKind, BinaryKind] = {
    TokenKind.Plus: BinaryKind.Add,
    TokenKind.Minus: BinaryKind.Sub,
    TokenKind.Asterisk: BinaryKind.Mul,
    TokenKind.Slash: BinaryKind.Div,
    TokenKind.EqEq: BinaryKind.Eq,
    TokenKind.NotEq: BinaryKind.NotEq,
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

    def peek(self) -> Token | None:
        if self.i < self.tokens_len - 2:
            return self.tokens[self.i + 1]

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

    def parse_primary(self) -> Expr:
        match self.t.kind:
            case TokenKind.Ident:
                next = self.peek()
                if not next:
                    assert False, "unexpected eof"
                match next.kind:
                    case TokenKind.LParen:
                        assert False, "function call"
                    case _:
                        assert False, "identifier"
            case _:
                assert False, "not implemented"

    def parse_unary(self) -> Expr:
        return self.parse_primary()

    def parse_factor(self) -> Expr:
        return self.parse_unary()

    def parse_term(self) -> Expr:
        return self.parse_factor()

    def parse_comparison_expr(self) -> Expr:
        return self.parse_term()

    def parse_assign_expr(self) -> Expr:
        left = self.parse_comparison_expr()
        while self.t.kind == TokenKind.Eq:
            self.eat()
            right = self.parse_assign_expr()
            left = Expr(Assign(left, right))
        return left

    def parse_conditional_expr(self) -> Expr:
        left = self.parse_assign_expr()
        while self.t.kind in [TokenKind.EqEq, TokenKind.NotEq]:
            op = binary_op[self.t.kind]
            self.eat()
            right = self.parse_assign_expr()
            left = Expr(Binary(left, right, op))
        return left

    def parse_expr(self) -> Expr:
        return self.parse_conditional_expr()

    def parse_expr_stmt(self) -> ExprStmt | None:
        exprs: List[Expr] = []
        while self.t.kind != TokenKind.Semi:
            exprs.append(self.parse_expr())
            if self.t.kind == TokenKind.Semi:
                break
            elif self.t.kind == TokenKind.Comma:
                self.eat()
                continue
            else:
                assert False, "parse_expr_stmt()"
        self.expect(TokenKind.Semi)
        return ExprStmt(exprs)

    def parse_decl_stmt(self) -> Decl:
        ty = self.parse_ty()
        name = self.parse_ident()
        if self.t.kind == TokenKind.Semi:
            self.eat()
            return Decl(name, ty, None)
        elif self.t.kind == TokenKind.Eq:
            self.eat()
            return Decl(name, ty, self.parse_expr())
        else:
            assert False

    def parse_stmt(self) -> Stmt | None:
        if ty := self.t.kind.get_ty():
            return Stmt(self.parse_decl_stmt())
        else:
            if stmt := self.parse_expr_stmt():
                return Stmt(stmt)

    def parse_block(self) -> Block:
        self.expect(TokenKind.LBrace)
        stmts: List[Stmt] = []
        while self.t and self.t.kind != TokenKind.RBrace:
            if stmt := self.parse_stmt():
                stmts.append(stmt)
        self.expect(TokenKind.RBrace)
        return Block(stmts)

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
