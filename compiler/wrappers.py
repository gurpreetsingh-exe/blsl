from __future__ import annotations
import bpy
from .Ast import TypeKind
from enum import Enum, auto


class ValueKind(Enum):
    Float = auto()
    Int = auto()
    Vector2 = auto()
    Vector3 = auto()
    Vector4 = auto()


class Value:
    __match_args__ = ('kind', 'data', )

    def __init__(self, kind, data):
        self.kind = kind
        self.data = data


class NodeTree:
    def __init__(self, name: str, ty: str):
        if tree := bpy.data.node_groups.get(name):
            bpy.data.node_groups.remove(tree)
        self.tree_type = ty
        self._nt = bpy.data.node_groups.new(type=ty, name=name)
        self._ins = NodeTreeInputs(self)
        self._outs = NodeTreeOutputs(self)

    def add_node(self, ty) -> bpy.types.Node:
        node = self._nt.nodes.new(type=ty)
        for inp in node.inputs:
            if type(inp) == bpy.types.NodeSocketVirtual:
                continue
            inp.default_value = 0.0
        return node

    def add_group(self) -> bpy.types.Node:
        match self.tree_type:
            case 'ShaderNodeTree':
                return self.add_node('ShaderNodeGroup')
            case 'GeometryNodeTree':
                return self.add_node('GeometryNodeGroup')
            case _:
                assert False, f"{self.tree_type}"

    def add_input(self, name: str, ty: TypeKind):
        self._ins.add_sock(name, ty)

    def add_output(self, name: str, ty: TypeKind):
        self._outs.add_sock(name, ty)

    def link_to_output(self, name: str, sock: bpy.types.NodeSocket):
        to = self._outs.get(name)
        self._nt.links.new(sock, to)

    def link(self, from_: Value | bpy.types.NodeSocket, to: bpy.types.NodeSocket):
        match from_:
            case Value(kind, data):
                match kind:
                    case ValueKind.Int | ValueKind.Float:
                        to.default_value = data
                    case _:
                        assert False, kind
            case bpy.types.NodeSocket():
                self._nt.links.new(from_, to)


def get_blender_socket_type(ty: TypeKind) -> str:
    match ty:
        case TypeKind.Void:
            return "NodeSocketVirtual"
        case TypeKind.Int:
            return "NodeSocketInt"
        case TypeKind.Float:
            return "NodeSocketFloat"
        case TypeKind.Vec4 | TypeKind.Vec3 | TypeKind.Vec2:
            return "NodeSocketVector"


class NodeTreeInputs:
    def __init__(self, nt: NodeTree):
        self._grp_in = nt.add_node('NodeGroupInput')
        self._in = nt._nt.inputs

    def add_sock(self, name: str, ty: TypeKind):
        self._in.new(type=get_blender_socket_type(ty), name=name)

    def get(self, name: str) -> bpy.types.NodeSocket:
        return self._grp_in.outputs[name]


class NodeTreeOutputs:
    def __init__(self, nt: NodeTree):
        self._grp_out = nt.add_node('NodeGroupOutput')
        self._out = nt._nt.outputs

    def add_sock(self, name: str, ty: TypeKind):
        self._out.new(type=get_blender_socket_type(ty), name=name)

    def get(self, name: str) -> bpy.types.NodeSocket:
        return self._grp_out.inputs[name]
