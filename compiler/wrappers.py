import bpy
from .Ast import TypeKind
from typing import Dict

class NodeTree:
    def __init__(self, name: str, ty: str):
        if tree := bpy.data.node_groups.get(name):
            bpy.data.node_groups.remove(tree)
        self._nt = bpy.data.node_groups.new(type=ty, name=name)
        self._ins = NodeTreeInputs(self)
        self._outs = NodeTreeOutputs(self)

    def add_node(self, ty) -> bpy.types.Node:
        return self._nt.nodes.new(type=ty)

    def add_input(self, name: str, ty: TypeKind):
        self._ins.add_sock(name, ty)

    def add_output(self, name: str, ty: TypeKind):
        self._outs.add_sock(name, ty)

    def link_to_output(self, name: str, sock: bpy.types.NodeSocket):
        to = self._outs.get(name)
        self._nt.links.new(sock, to)


def get_blender_socket_type(ty: TypeKind) -> str:
    match ty:
        case TypeKind.Void:
            return "NodeSocketVirtual"
        case TypeKind.Int:
            return "NodeSocketInt"
        case TypeKind.Float:
            return "NodeSocketFloat"
        case TypeKind.Vec4:
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

