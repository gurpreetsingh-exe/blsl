import bpy
from .Ast import *
from .wrappers import NodeTree


class NodeGen:
    def __init__(self, module: Module, ctx: bpy.types.Context):
        self.module = module
        self.ctx = ctx
        self.nt = self.ctx.space_data.node_tree

    def add_param(self, arg: FnArg, nt: NodeTree):
        match arg:
            case FnArg(Ident(name), Ty(kind), ty_qualifiers):
                for qual in ty_qualifiers:
                    if qual.is_output():
                        nt.add_output(name, kind)
                        break
                nt.add_input(name, kind)

    def emit(self):
        for deff in self.module.defs:
            match deff:
                case Def(Fn(Ident(name), args, ret_ty, body)):
                    self.nt.nodes.clear()
                    nt = NodeTree(name, 'ShaderNodeTree')
                    node = self.nt.nodes.new('ShaderNodeGroup')
                    for arg in args:
                        self.add_param(arg, nt)

                    node.node_tree = nt._nt

