from __future__ import annotations
import bpy
from .Ast import *
from .wrappers import NodeTree
from typing import Dict


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

    def add_param(self, arg: FnArg, nt: NodeTree):
        match arg:
            case FnArg(Ident(name), Ty(kind), ty_qualifiers):
                for qual in ty_qualifiers:
                    if qual.is_output():
                        nt.add_output(name, kind)
                        break
                nt.add_input(name, kind)

    def gen_expr(self, expr: Expr, nt: NodeTree) -> bpy.types.NodeSocket:
        match expr.kind:
            case Int(value) | Float(value):
                node = nt.add_node("ShaderNodeValue")
                node.outputs[0].default_value = float(value)
                return node.outputs[0]
            case Ident(name):
                return self.env.get(name)
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
                    nt.link_to_output('ret', sock_out)
                case _:
                    assert False, f"{stmt.kind}"

    def emit(self):
        for deff in self.module.defs:
            match deff:
                case Def(Fn(Ident(name), FnSig(args, Ty(ret_ty)), body)):
                    self.nt.nodes.clear()
                    nt = NodeTree(name, 'ShaderNodeTree')
                    node = self.nt.nodes.new('ShaderNodeGroup')
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

