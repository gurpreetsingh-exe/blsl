from __future__ import annotations
from typing import Dict
from .Ast import *


class TyEnv:
    def __init__(self, paren_env: TyEnv | None = None) -> None:
        self.parent: TyEnv | None = paren_env
        self.bindings: Dict[str, Ty] = {}
        self.fns: Dict[str, FnSig] = {}
        self.ctx: FnSig | None = None

    def def_fn(self, name: str, fn: FnSig):
        if name in self.fns:
            assert False, f"`{name}` is already defined"
        self.fns[name] = fn

    def bind(self, name: str, ty: Ty):
        if name in self.bindings:
            assert False, f"`{name}` is already defined"
        self.bindings[name] = ty

    def get(self, name: str) -> Ty | None:
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            return self.parent.get(name)


class TyChecker:
    def __init__(self, module: Module) -> None:
        self.module = module
        self.ty_env = TyEnv()
        self.fn: FnSig | None = None
        self._check()

    def assert_eq(self, ty: Ty, kind: TypeKind) -> bool:
        if ty.kind == kind:
            return True
        else:
            assert False, f"expected `{ty.display_name()}` found `{kind.display_name()}`"

    def find_var(self, name: str) -> Ty:
        ty = self.ty_env.get(name)
        if ty:
            return ty
        else:
            assert False, f"`{name}` is not defined"

    def expect_ty(self, expected_ty: Ty, found_ty: Ty):
        return f"expected `{expected_ty.display_name()}` found `{found_ty.display_name()}`"

    def check(self, expr: Expr, expected_ty: Ty):
        match expr.kind:
            case Int():
                self.assert_eq(expected_ty, TypeKind.Int)
            case Float():
                self.assert_eq(expected_ty, TypeKind.Float)
            case Ident(name):
                ty = self.find_var(name)
                self.assert_eq(expected_ty, ty.kind)
                expr.kind.ty = expected_ty
            case Binary(left, right, kind):
                left_ty = self.infer(left)
                right_ty = self.infer(right)
                match left_ty.is_vector(), right_ty.is_vector():
                    case True, True:
                        assert left_ty == right_ty, f"`{kind}` is not implemented for `{left_ty.display_name()}` and `{right_ty.display_name()}`"
                        assert expected_ty == left_ty, self.expect_ty(expected_ty, left_ty)
                    case True, False:
                        assert expected_ty == left_ty, self.expect_ty(expected_ty, left_ty)
                    case False, True:
                        assert expected_ty == right_ty, self.expect_ty(expected_ty, right_ty)
                    case _, _:
                        pass
                expr.kind.ty = expected_ty
            case _:
                assert False, f"{expr.kind}"

    def infer(self, expr: Expr) -> Ty:
        match expr.kind:
            case Int():
                return Ty(TypeKind.Int)
            case Float():
                return Ty(TypeKind.Float)
            case Ident(name):
                return self.find_var(name)
            case Binary(left, right, kind):
                if (l := self.infer(left)) != (r := self.infer(right)):
                    assert False, f'{kind} is not implement for `{l}` and `{r}`'
                return l
            case _:
                assert False, f"{expr.kind}"

    def visit_stmt(self, stmt: Stmt):
        match stmt.kind:
            case ExprStmt(exprs):
                for expr in exprs:
                    self.infer(expr)
            case Decl(Ident(name), ty, init):
                self.ty_env.bind(name, ty)
                if init:
                    self.check(init, ty)
            case Return(expr):
                assert self.fn != None
                self.check(expr, self.fn.ret_ty)

    def visit_block(self, block: Block):
        tmp_env = self.ty_env
        self.ty_env = TyEnv(tmp_env)
        if fn := tmp_env.ctx:
            for arg in fn.args:
                match arg:
                    case FnArg(Ident(name), ty, _):
                        self.ty_env.bind(name, ty)
        tmp_env.ctx = None
        for stmt in block.stmts:
            self.visit_stmt(stmt)
        self.ty_env = tmp_env

    def _check(self):
        for deff in self.module.defs:
            match deff.kind:
                case Fn(Ident(name), sig, body):
                    self.ty_env.ctx = sig
                    self.fn = sig
                    self.ty_env.def_fn(name, sig)
                    self.visit_block(body)

