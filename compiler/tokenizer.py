import doctest
from typing import List, Dict
from enum import Enum, auto
from .Ast import TypeKind


class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value


class TokenKind(Enum):
    IntLit = auto()
    FloatLit = auto()
    Ident = auto()

    Int = auto()
    Float = auto()
    Void = auto()
    Vec2 = auto()
    Vec3 = auto()
    Vec4 = auto()

    Return = auto()
    Const = auto()
    In = auto()
    Out = auto()
    InOut = auto()

    LParen = auto()
    RParen = auto()
    LBrace = auto()
    RBrace = auto()
    Comma = auto()
    Eq = auto()
    Semi = auto()
    Plus = auto()
    Minus = auto()
    Asterisk = auto()
    Slash = auto()
    Period = auto()
    EqEq = auto()
    NotEq = auto()

    def get_ty(self) -> TypeKind | None:
        match self:
            case TokenKind.Int: return TypeKind.Int
            case TokenKind.Float: return TypeKind.Float
            case TokenKind.Void: return TypeKind.Void
            case TokenKind.Vec2: return TypeKind.Vec2
            case TokenKind.Vec3: return TypeKind.Vec3
            case TokenKind.Vec4: return TypeKind.Vec4


keywords: Dict[str, TokenKind] = {
    'int': TokenKind.Int,
    'float': TokenKind.Float,
    'void': TokenKind.Void,
    'vec2': TokenKind.Vec2,
    'vec3': TokenKind.Vec3,
    'vec4': TokenKind.Vec4,
    'const': TokenKind.Const,
    'in': TokenKind.In,
    'out': TokenKind.Out,
    'inout': TokenKind.InOut,
    'return': TokenKind.Return,
}


punc: Dict[str, TokenKind] = {
    '(': TokenKind.LParen,
    ')': TokenKind.RParen,
    '{': TokenKind.LBrace,
    '}': TokenKind.RBrace,
    ',': TokenKind.Comma,
    '=': TokenKind.Eq,
    ';': TokenKind.Semi,
    '+': TokenKind.Plus,
    '-': TokenKind.Minus,
    '*': TokenKind.Asterisk,
    '/': TokenKind.Slash,
    '.': TokenKind.Period,
    '==': TokenKind.EqEq,
    '!=': TokenKind.NotEq,
}


def tokenize(src: str) -> List[Token]:
    """
    >>> tokens = tokenize("void main()")
    >>> len(tokens)
    4
    >>> [token.kind.name for token in tokens]
    ['Void', 'Ident', 'LParen', 'RParen']
    >>> tokens = tokenize("__main20 .20 20.0")
    >>> len(tokens)
    4
    >>> [token.kind.name for token in tokens]
    ['Ident', 'Period', 'IntLit', 'FloatLit']
    >>>
    """

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
        elif c.isalpha() or c == '_':
            begin = i
            while i < len(src) and (src[i].isalnum() or src[i] == '_'):
                i += 1
            add_token(TokenKind.Ident, begin, i)
        elif c.isdigit():
            begin = i
            is_float = False
            while i < len(src) and (src[i].isdigit() or src[i] == '.'):
                if src[i] == '.':
                    if not is_float:
                        is_float = True
                    else:
                        assert False, "unexpected `.`"
                i += 1
            add_token(
                TokenKind.FloatLit if is_float else TokenKind.IntLit, begin, i)
        elif c in punc:
            if c == '/' and src[i + 1] == '/':
                while src[i] != '\n':
                    i += 1
                continue
            add_token(punc[c], i, i + 1)
            i += 1
        else:
            i += 1

    return tokens


doctest.testfile("tokenizer.py", globs=globals())
