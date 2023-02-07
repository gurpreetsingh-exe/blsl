from __future__ import annotations
import bpy
from .Ast import *
from .wrappers import NodeTree, Value, ValueKind
from typing import Dict, List


def vec4_to_vec4(value: List[Value | bpy.types.NodeSocket], nt: NodeTree) -> bpy.types.Node:
    node = nt.add_node('ShaderNodeCombineXYZ')
    for i in range(3):
        val = value[i]
        nt.link(val, node.inputs[i])
    return node


def float_to_vec4(value: Value | bpy.types.NodeSocket, nt: NodeTree) -> bpy.types.Node:
    node = nt.add_node('ShaderNodeCombineXYZ')
    for i in range(3):
        nt.link(value, node.inputs[i])
    return node


def gen_vec4(sig: int, args: List[Value | bpy.types.NodeSocket], nt: NodeTree) -> bpy.types.Node:
    match sig:
        case 0:
            return float_to_vec4(args[0], nt)
        case 1:
            return vec4_to_vec4(args, nt)
        case _:
            assert False


def gen_vec3(sig: int, args: List[Value | bpy.types.NodeSocket], nt: NodeTree) -> bpy.types.Node:
    match sig:
        case 0:
            return float_to_vec4(args[0], nt)
        case 1:
            return vec4_to_vec4(args, nt)
        case _:
            assert False


def float_to_vec2(value: Value | bpy.types.NodeSocket, nt: NodeTree) -> bpy.types.Node:
    node = nt.add_node('ShaderNodeCombineXYZ')
    for i in range(2):
        nt.link(value, node.inputs[i])
    return node


def vec2_to_vec2(value: List[Value | bpy.types.NodeSocket], nt: NodeTree) -> bpy.types.Node:
    node = nt.add_node('ShaderNodeCombineXYZ')
    for i in range(2):
        val = value[i]
        nt.link(val, node.inputs[i])
    return node


def gen_vec2(sig: int, args: List[Value | bpy.types.NodeSocket], nt: NodeTree) -> bpy.types.Node:
    match sig:
        case 0:
            return float_to_vec2(args[0], nt)
        case 1:
            return vec2_to_vec2(args, nt)
        case _:
            assert False


builtins = {
    'vec4': gen_vec4,
    'vec3': gen_vec3,
    'vec2': gen_vec2,
}


class Env:
    def __init__(self, paren_env: Env | None = None):
        self.parent: Env | None = paren_env
        self.bindings: Dict[str, bpy.types.NodeSocket] = {}
        self.ctx: FnSig | None = None

    def bind(self, name: str, sock: bpy.types.NodeSocket):
        if name in self.bindings:
            assert False, f"`{name}` is already defined"
        self.bindings[name] = sock

    def get(self, name: str) -> bpy.types.NodeSocket:
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            assert False


class NodeGen:
    def __init__(self, module: Module, ctx: bpy.types.Context):
        self.module = module
        self.ctx = ctx
        self.env = Env()
        match self.ctx.space_data:
            case bpy.types.SpaceNodeEditor():
                self.nt = self.ctx.space_data.node_tree
            case _:
                assert False, "unreachable"

    @property
    def tree_type(self) -> str:
        return self.nt.bl_idname

    def add_param(self, arg: FnArg, nt: NodeTree):
        match arg:
            case FnArg(Ident(name), Ty(kind), ty_qualifiers):
                for qual in ty_qualifiers:
                    if qual.is_output():
                        nt.add_output(name, kind)
                    break
                sock = nt.add_input(name, kind)
                self.env.bind(name, sock)

    def gen_expr(self, expr: Expr, nt: NodeTree) -> bpy.types.NodeSocket | Value:
        match expr.kind:
            case Int(value):
                return Value(ValueKind.Int, int(value))
            case Float(value):
                return Value(ValueKind.Float, float(value))
            case Ident(name):
                return self.env.get(name)
            case Binary(left, right, kind):
                assert expr.kind.ty != None
                l = self.gen_expr(left, nt)
                r = self.gen_expr(right, nt)
                ntype = None
                if expr.kind.ty.is_vector():
                    node = nt.add_node("ShaderNodeVectorMath")
                    ntype = bpy.types.ShaderNodeVectorMath
                else:
                    node = nt.add_node("ShaderNodeMath")
                    ntype = bpy.types.ShaderNodeMath
                assert isinstance(node, ntype)
                node.operation = kind.blender_op()
                nt.link(l, node.inputs[0], expr.kind.ty)
                nt.link(r, node.inputs[1], expr.kind.ty)
                match kind:
                    case BinaryKind.NotEq:
                        out = nt.add_node("ShaderNodeMath")
                        out.operation = "SUBTRACT"
                        nt.link(Value(ValueKind.Int, 1), out.inputs[0])
                        nt.link(node.outputs[0], out.inputs[1])
                        node = out
                return node.outputs[0]
            case Call(name, args):
                assert expr.kind.sig != None
                if name in builtins:
                    gen_args = [self.gen_expr(arg, nt) for arg in args]
                    node = builtins[name](expr.kind.sig, gen_args, nt)
                else:
                    node = nt.add_group()
                    node.node_tree = bpy.data.node_groups.get(name)
                return node.outputs[0]
            case _:
                assert False, f"{expr.kind}"

    def gen_node_tree(self, block: Block, nt: NodeTree):
        for stmt in block.stmts:
            match stmt.kind:
                case ExprStmt(exprs):
                    for expr in exprs:
                        self.gen_expr(expr, nt)
                case Decl(Ident(name), _, init):
                    if init:
                        sock = self.gen_expr(init, nt)
                        self.env.bind(name, sock)
                case Return(expr):
                    sock_out = self.gen_expr(expr, nt)
                    match sock_out:
                        case Value(_, data):
                            sock = nt._outs.get('ret')
                            sock.default_value = data
                        case _:
                            nt.link_to_output('ret', sock_out)
                case _:
                    assert False, f"{stmt.kind}"

    def emit(self, clear=False):
        for deff in self.module.defs:
            match deff:
                case Def(Fn(Ident(name), FnSig(args, Ty(ret_ty)), body)):
                    if clear:
                        self.nt.nodes.clear()
                    nt = NodeTree(name, self.tree_type)
                    match self.tree_type:
                        case 'ShaderNodeTree':
                            node = self.nt.nodes.new('ShaderNodeGroup')
                        case 'GeometryNodeTree':
                            node = self.nt.nodes.new('GeometryNodeGroup')
                        case _:
                            assert False, f"{self.tree_type}"

                    match node:
                        case bpy.types.ShaderNodeGroup() | bpy.types.GeometryNodeGroup():
                            node.node_tree = nt._nt
                        case _:
                            assert False, "not implemented"
                    for arg in args:
                        self.add_param(arg, nt)
                    if ret_ty != TypeKind.Void:
                        nt.add_output('ret', ret_ty)
                    self.gen_node_tree(body, nt)
                    return nt._nt.nodes
