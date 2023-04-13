from __future__ import annotations
from typing import Dict
from .Ast import *


class Sig:
    def __init__(self, args: List[Ty], ret_ty: Ty) -> None:
        self.args = args
        self.ret_ty = ret_ty


builtins = {
    'vec4': [
        Sig([Ty(TypeKind.Float)], Ty(TypeKind.Vec4)),
        Sig([Ty(TypeKind.Float)] * 4, Ty(TypeKind.Vec4)),
        Sig([Ty(TypeKind.Int)], Ty(TypeKind.Vec4)),
        Sig([Ty(TypeKind.Int)] * 4, Ty(TypeKind.Vec4)),
    ],
    'vec3': [
        Sig([Ty(TypeKind.Float)], Ty(TypeKind.Vec3)),
        Sig([Ty(TypeKind.Float)] * 3, Ty(TypeKind.Vec3)),
        Sig([Ty(TypeKind.Int)], Ty(TypeKind.Vec3)),
        Sig([Ty(TypeKind.Int)] * 3, Ty(TypeKind.Vec3)),
    ],
    'vec2': [
        Sig([Ty(TypeKind.Float)], Ty(TypeKind.Vec2)),
        Sig([Ty(TypeKind.Float)] * 2, Ty(TypeKind.Vec2)),
        Sig([Ty(TypeKind.Int)], Ty(TypeKind.Vec2)),
        Sig([Ty(TypeKind.Int)] * 2, Ty(TypeKind.Vec2)),
    ],
    'length': [
        Sig([Ty(TypeKind.Vec2)], Ty(TypeKind.Float)),
        Sig([Ty(TypeKind.Vec3)], Ty(TypeKind.Float)),
    ],
    'min': [
        Sig([Ty(TypeKind.Float)] * 2, Ty(TypeKind.Float)),
        Sig([Ty(TypeKind.Vec2)] * 2, Ty(TypeKind.Vec2)),
        Sig([Ty(TypeKind.Vec3)] * 2, Ty(TypeKind.Vec3)),
    ],
    'max': [
        Sig([Ty(TypeKind.Float)] * 2, Ty(TypeKind.Float)),
        Sig([Ty(TypeKind.Vec2)] * 2, Ty(TypeKind.Vec2)),
        Sig([Ty(TypeKind.Vec3)] * 2, Ty(TypeKind.Vec3)),
    ],
}


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
                    assert False
            case _:
                assert False, type(expr.kind)

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
