from .Ast import *

Tfloat = Ty(TypeKind.Float)
Tint = Ty(TypeKind.Int)
vec2 = Ty(TypeKind.Vec2)
vec3 = Ty(TypeKind.Vec3)
vec4 = Ty(TypeKind.Vec4)


class Sig:
    def __init__(self, args: List[Ty], ret_ty: Ty) -> None:
        self.args = args
        self.ret_ty = ret_ty


builtins = {
    'vec4': [
        Sig([Tfloat], vec4),
        Sig([Tfloat] * 4, vec4),
        Sig([Tint], vec4),
        Sig([Tint] * 4, vec4),
    ],
    'vec3': [
        Sig([Tfloat], vec3),
        Sig([Tfloat] * 3, vec3),
        Sig([Tint], vec3),
        Sig([Tint] * 3, vec3),
    ],
    'vec2': [
        Sig([Tfloat], vec2),
        Sig([Tfloat] * 2, vec2),
        Sig([Tint], vec2),
        Sig([Tint] * 2, vec2),
    ],
    'length': [
        Sig([vec2], Tfloat),
        Sig([vec3], Tfloat),
    ],
    'min': [
        Sig([Tfloat] * 2, Tfloat),
        Sig([vec2] * 2, vec2),
        Sig([vec3] * 2, vec3),
        Sig([vec2, Tfloat], vec2),
        Sig([vec3, Tfloat], vec3),
    ],
    'max': [
        Sig([Tfloat] * 2, Tfloat),
        Sig([vec2] * 2, vec2),
        Sig([vec3] * 2, vec3),
        Sig([vec2, Tfloat], vec2),
        Sig([vec3, Tfloat], vec3),
    ],
    'abs': [
        Sig([Tfloat], Tfloat),
        Sig([vec2], vec2),
        Sig([vec3], vec3),
    ],
    'dot': [
        Sig([vec2, vec2], Tfloat),
        Sig([vec3, vec3], Tfloat),
    ],
    'clamp': [
        Sig([Tfloat, Tfloat, Tfloat], Tfloat),
    ],
}
