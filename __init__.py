bl_info = {
    "name": "BLSL Compiler",
    "category": "Node",
    "blender": (3, 0, 0),
    "version": (0, 0, 1),
}

import bpy
from bpy.types import (
    Panel,
    Operator,
    PropertyGroup,
    WindowManager)

from .compiler.Parser import parser_from_src, parser_from_file
from .compiler.nodegen import NodeGen
from .compiler.typechk import TyChecker
from beeprint import pp

try:
    node_align = __import__("Node Align")
except ImportError:
    print("\"Node Align\" not found, nodes will not be aligned")

class BLSL_PT_Panel(Panel):
    bl_idname = "BLSL_PT_Panel"
    bl_label = "GLSL Compiler"
    bl_region_type = "UI"
    bl_space_type = "NODE_EDITOR"
    bl_category = "GLSL Compiler"

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "tree_type") and \
            context.space_data.tree_type in {'ShaderNodeTree', 'GeometryNodeTree'} and \
            context.space_data.node_tree

    def draw(self, context):
        gc = context.window_manager.blsl_compiler
        layout = self.layout
        layout.use_property_decorate = False
        row = layout.row(align=True)
        row.prop(gc, "source_type", expand=True)
        if gc.source_type == "EXTERNAL":
            row = layout.row(align=True)
            row = row.column()
            row.prop(gc, "filepath", text="")
        elif gc.source_type == "INTERNAL":
            row = layout.row(align=True)
            row = row.column()
            row.prop(gc, "text_prop", text="")
        row = row.column()
        row.operator("blsl_compiler.compile")

        row = layout.row(align=True)
        row.prop(gc, "debug_ast_output")
        row.prop(gc, "debug_token_output")


class BLSL_OT_compile(Operator):
    bl_idname = "blsl_compiler.compile"
    bl_label = "Compile"

    @classmethod
    def poll(cls, context):
        gc = context.window_manager.blsl_compiler
        return \
            (gc.source_type == "INTERNAL" and gc.text_prop) or \
            (gc.source_type == "EXTERNAL" and gc.filepath)

    def dump_ast(self, ast):
        print("======= AST dump start =======")
        pp(ast, max_depth=20)
        print("======== AST dump end ========")

    def execute(self, context):
        gc = context.window_manager.blsl_compiler
        if gc.source_type == "INTERNAL":
            parser = parser_from_src(gc.text_prop.as_string())
        elif gc.source_type == "EXTERNAL":
            parser = parser_from_file(gc.filepath)
        else:
            assert False

        ast = parser.parse()
        if gc.debug_ast_output:
            self.dump_ast(ast)
        TyChecker(ast)
        nodes = NodeGen(ast, context).emit()
        if 'node_align' in globals():
            node_align.operators.distribute_nodes(nodes, None, "HORIZONTAL")
        return {'FINISHED'}


class BLSLCompiler(PropertyGroup):
    source_type: bpy.props.EnumProperty(name="Source Type", items=[
        ("INTERNAL", "Internal", ""),
        ("EXTERNAL", "External", ""),
    ])

    text_prop: bpy.props.PointerProperty(type=bpy.types.Text)
    filepath: bpy.props.StringProperty(name="Source file", subtype="FILE_PATH", default="")

    debug_ast_output: bpy.props.BoolProperty(name="AST output", default=False)
    debug_token_output: bpy.props.BoolProperty(name="Token output", default=False)


classes = [
    BLSL_PT_Panel,
    BLSLCompiler,
    BLSL_OT_compile,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    WindowManager.blsl_compiler = bpy.props.PointerProperty(type=BLSLCompiler)


def unregister():
    del WindowManager.blsl_compiler

    for cls in classes:
        bpy.utils.unregister_class(cls)
