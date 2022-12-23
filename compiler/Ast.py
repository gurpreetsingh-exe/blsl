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


class Block:
    def __init__(self):
        pass


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
