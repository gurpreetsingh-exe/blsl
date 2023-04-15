from __future__ import annotations
from typing import Dict
from .Ast import *
from .bltin import *


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
            case Assign(left, init):
                self.check(init, expected_ty)
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
                        match kind:
                            case BinaryKind.Eq | BinaryKind.NotEq:
                                self.expect_ty(expected_ty, Ty(TypeKind.Int))
                            case _:
                                self.expect_ty(expected_ty, left_ty)
                    case True, False:
                        assert expected_ty == left_ty, self.expect_ty(
                            expected_ty, left_ty)
                    case False, True:
                        assert expected_ty == right_ty, self.expect_ty(
                            expected_ty, right_ty)
                    case _, _:
                        pass
                expr.kind.ty = expected_ty
            case Call(name, args):
                if name in builtins:
                    fns = builtins[name]
                    matches = False

                    i = 0
                    for i, fn in enumerate(fns):
                        if len(args) != len(fn.args):
                            continue

                        args_match = 0
                        for arg, exp_ty in zip(args, fn.args):
                            args_match += self.infer(arg) == exp_ty

                        if args_match != len(args):
                            continue
                        if expected_ty != fn.ret_ty:
                            continue

                        matches = True
                        break

                    if not matches:
                        assert False, f"no matching function call for `{name}`"
                    expr.kind.sig = i

                elif name in self.ty_env.fns:
                    print("fn:", self.ty_env.fns[name])
                    assert False
            case Field(Ident(name), Ident(field)):
                var = self.find_var(name)
                match var.kind:
                    case TypeKind.Int | TypeKind.Float:
                        assert False, f"`{var.kind.name.lower()}` has no field `{field}`"
                    case TypeKind.Vec2:
                        if field not in {'x', 'y'}:
                            assert False, f"`vec2` has no field `{field}`"
                        self.expect_ty(expected_ty, Tfloat)
                    case TypeKind.Vec3:
                        if field not in {'x', 'y', 'z'}:
                            assert False, f"`vec3` has no field `{field}`"
                        self.expect_ty(expected_ty, Tfloat)
                    case _:
                        assert False
            case Unary(_, expr):
                self.expect_ty(expected_ty, self.infer(expr))
            case _:
                assert False, f"{expr.kind}"

    def infer(self, expr: Expr) -> Ty:
        match expr.kind:
            case Assign(left, init):
                ty = self.infer(left)
                self.check(init, ty)
                return Ty(TypeKind.Void)
            case Int():
                return Ty(TypeKind.Int)
            case Float():
                return Ty(TypeKind.Float)
            case Ident(name):
                return self.find_var(name)
            case Binary(left, right, kind):
                left_ty = self.infer(left)
                right_ty = self.infer(right)
                if left_ty.is_vector() and right_ty.is_vector():
                    assert left_ty == right_ty, f"`{kind}` is not implemented for `{left_ty.display_name()}` and `{right_ty.display_name()}`"
                if left_ty.is_vector():
                    expr.kind.ty = left_ty
                    return left_ty
                else:
                    expr.kind.ty = right_ty
                    return right_ty
            case Call(name, args):
                if name in builtins:
                    fns = builtins[name]
                    matches = False

                    i = 0
                    for i, fn in enumerate(fns):
                        if len(args) != len(fn.args):
                            continue

                        args_match = 0
                        for arg, exp_ty in zip(args, fn.args):
                            args_match += self.infer(arg) == exp_ty

                        if args_match != len(args):
                            continue

                        matches = True
                        break

                    if not matches:
                        assert False, f"no matching function call for `{name}`"
                    expr.kind.sig = i
                    return fns[i].ret_ty

                elif name in self.ty_env.fns:
                    print("fn:", self.ty_env.fns[name])
                    assert False
                else:
                    assert False, name
            case Field(Ident(name), Ident(field)):
                var = self.find_var(name)
                match var.kind:
                    case TypeKind.Int | TypeKind.Float:
                        assert False, f"`{var.kind.name.lower()}` has no field `{field}`"
                    case TypeKind.Vec2:
                        if field not in {'x', 'y'}:
                            assert False, f"`vec2` has no field `{field}`"
                        return Tfloat
                    case TypeKind.Vec3:
                        if field not in {'x', 'y', 'z'}:
                            assert False, f"`vec3` has no field `{field}`"
                        return Tfloat
                assert False
            case Unary(_, expr):
                return self.infer(expr)
            case _:
                assert False, type(expr.kind)

    def visit_stmt(self, stmt: Stmt):
        match stmt.kind:
            case ExprStmt(exprs):
                for expr in exprs:
                    self.infer(expr)
            case Decl(ty, exprs):
                for expr in exprs.exprs:
                    match expr.kind:
                        case Assign(Expr(Ident(name)), init):
                            self.ty_env.bind(name, ty)
                            if init:
                                self.check(init, ty)
                        case _:
                            assert False
            case Return(expr):
                assert self.fn != None
                self.check(expr, self.fn.ret_ty)
            case _:
                assert False, stmt.kind

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
