from typing import List
from enum import Enum, auto


class Def:
    __match_args__ = ('kind', )

    def __init__(self, kind):
        self.kind = kind


class TypeKind(Enum):
    Int = auto()
    Void = auto()
    Vec4 = auto()


class Ty:
    __match_args__ = ('kind', )

    def __init__(self, kind: TypeKind):
        self.kind = kind


class Ident:
    __match_args__ = ('name', )

    def __init__(self, name: str):
        self.name = name


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
    def __init__(self, kind):
        self.kind = kind


class BinaryKind(Enum):
    Add = auto()
    Sub = auto()
    Mul = auto()
    Div = auto()
    Eq = auto()
    NotEq = auto()


class Binary:
    def __init__(self, left: Expr, right: Expr, op: BinaryKind):
        self.left = left
        self.right = right
        self.op = op


class Assign:
    def __init__(self, left: Expr, init: Expr):
        self.left = left
        self.init = init


class Decl:
    def __init__(self, name: Ident, ty: Ty, init: Expr | None):
        self.name = name
        self.ty = ty
        self.init = init


class ExprStmt:
    def __init__(self, exprs: List[Expr]):
        self.exprs = exprs


class Stmt:
    def __init__(self, kind: ExprStmt | Decl):
        self.kind = kind


class Block:
    def __init__(self, stmts: List[Stmt]):
        self.stmts = stmts


class Fn:
    __match_args__ = ('name', 'args', 'ret_ty', 'body', )

    def __init__(self, name: Ident, args: List[FnArg], ret_ty: Ty, body: Block):
        self.name = name
        self.args = args
        self.ret_ty = ret_ty
        self.body = body


class Module:
    def __init__(self, defs: List[Def]):
        self.defs = defs
