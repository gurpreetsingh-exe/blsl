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
    Vec4 = auto()

    def display_name(self) -> str:
        return self.name.lower()


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
    def __init__(self, left: Expr, right: Expr, kind: BinaryKind):
        self.left = left
        self.right = right
        self.kind = kind
        self.ty: Ty | None = None


class Assign:
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


class Decl:
    __match_args__ = ('name', 'ty', 'init', )

    def __init__(self, name: Ident, ty: Ty, init: Expr | None):
        self.name = name
        self.ty = ty
        self.init = init


class ExprStmt:
    __match_args__ = ("exprs", )

    def __init__(self, exprs: List[Expr]):
        self.exprs = exprs


class Return:
    __match_args__ = ('expr', )

    def __init__(self, expr: Expr):
        self.expr = expr


class Stmt:
    def __init__(self, kind: \
            ExprStmt \
            | Decl \
            | Return \
    ):
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
