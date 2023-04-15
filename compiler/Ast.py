from __future__ import annotations
from typing import List
from enum import Enum, auto


class Def:
    __match_args__ = ('kind', )

    def __init__(self, kind):
        self.kind = kind


class TypeKind(Enum):
    Int = auto()
    Float = auto()
    Void = auto()
    Vec2 = auto()
    Vec3 = auto()
    Vec4 = auto()

    def display_name(self) -> str:
        return self.name.lower()

    def is_vector(self) -> bool:
        match self:
            case TypeKind.Vec4 | TypeKind.Vec3 | TypeKind.Vec2: return True
            case _: return False

    def get_size(self) -> int:
        match self:
            case TypeKind.Vec3 | TypeKind.Vec4: return 3
            case TypeKind.Vec2: return 2
            case _: return 0


class Ty:
    __match_args__ = ('kind', )

    def __init__(self, kind: TypeKind):
        self.kind = kind

    def display_name(self) -> str:
        return self.kind.display_name()

    def is_vector(self) -> bool:
        return self.kind.is_vector()

    def get_size(self) -> int:
        return self.kind.get_size()

    def __eq__(self, __o: Ty) -> bool:
        if __o == None:
            return False
        return self.kind == __o.kind

    def __ne__(self, __o: Ty) -> bool:
        return not self.__eq__(__o)


class Ident:
    __match_args__ = ('name', )

    def __init__(self, name: str):
        self.name = name
        self.ty: Ty | None = None


class TyQualifier:
    def is_output(self) -> bool:
        raise NotImplementedError()


class StorageQualifier(Enum):
    Const = auto()
    In = auto()
    Out = auto()
    InOut = auto()

    def is_output(self) -> bool:
        match self:
            case StorageQualifier.Out | StorageQualifier.InOut:
                return True
            case _:
                return False


class Storage(TyQualifier):
    __match_args__ = ('kind', )

    def __init__(self, kind: StorageQualifier):
        self.kind = kind

    def is_output(self) -> bool:
        return self.kind.is_output()


class FnArg:
    __match_args__ = ('name', 'ty', 'ty_qualifiers', )

    def __init__(self, name: Ident, ty: Ty, ty_qualifiers: List[TyQualifier]):
        self.name = name
        self.ty = ty
        self.ty_qualifiers = ty_qualifiers


class Expr:
    __match_args__ = ('kind', )

    def __init__(self, kind):
        self.kind = kind


class BinaryKind(Enum):
    Add = auto()
    Sub = auto()
    Mul = auto()
    Div = auto()
    Eq = auto()
    NotEq = auto()

    def blender_op(self):
        match self:
            case BinaryKind.Add: return "ADD"
            case BinaryKind.Sub: return "SUBTRACT"
            case BinaryKind.Mul: return "MULTIPLY"
            case BinaryKind.Div: return "DIVIDE"
            case BinaryKind.Eq | BinaryKind.NotEq: return "COMPARE"
            case _: assert False, f"{self}"


class Binary:
    __match_args__ = ('left', 'right', 'kind', )

    def __init__(self, left: Expr, right: Expr, kind: BinaryKind):
        self.left = left
        self.right = right
        self.kind = kind
        self.ty: Ty | None = None


class Assign:
    __match_args__ = ('left', 'init', )

    def __init__(self, left: Expr, init: Expr):
        self.left = left
        self.init = init


class Int:
    __match_args__ = ('value', )

    def __init__(self, value: str):
        self.value = value


class Float:
    __match_args__ = ('value', )

    def __init__(self, value: str):
        self.value = value


class Call:
    __match_args__ = ('name', 'args', )

    def __init__(self, name: str, args: List[Expr]):
        self.name = name
        self.args = args
        self.sig: int | None = None


class Field:
    __match_args__ = ('name', 'field', )

    def __init__(self, name: Ident, field: Ident):
        self.name = name
        self.field = field


class Decl:
    __match_args__ = ('ty', 'decls', )

    def __init__(self, ty: Ty, decls: ExprStmt):
        self.ty = ty
        self.decls = decls


class ExprStmt:
    __match_args__ = ("exprs", )

    def __init__(self, exprs: List[Expr]):
        self.exprs = exprs


class Return:
    __match_args__ = ('expr', )

    def __init__(self, expr: Expr):
        self.expr = expr


class Stmt:
    def __init__(self, kind: ExprStmt
                 | Decl
                 | Return):
        self.kind = kind


class Block:
    def __init__(self, stmts: List[Stmt]):
        self.stmts = stmts


class FnSig:
    __match_args__ = ('args', 'ret_ty', )

    def __init__(self, args: List[FnArg], ret_ty: Ty):
        self.args = args
        self.ret_ty = ret_ty


class Fn:
    __match_args__ = ('name', 'sig', 'body', )

    def __init__(self, name: Ident, sig: FnSig, body: Block):
        self.name = name
        self.sig = sig
        self.body = body


class Module:
    def __init__(self, defs: List[Def]):
        self.defs = defs
