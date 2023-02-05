import importlib
import pathlib
import os
from beeprint import pp
from .compiler.typechk import TyChecker
from .compiler.nodegen import NodeGen
from .compiler.Parser import parser_from_src, parser_from_file
import bpy
from bpy.types import (
    Panel,
    Operator,
    PropertyGroup,
    WindowManager)
import numpy as np

bl_info = {
    "name": "BLSL Compiler",
    "category": "Node",
    "blender": (3, 0, 0),
    "version": (0, 0, 1),
}


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
        row.operator("blsl_compiler.run_tests")

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
        TyChecker(ast)
        if gc.debug_ast_output:
            self.dump_ast(ast)
        nodes = NodeGen(ast, context).emit(clear=True)
        if 'node_align' in globals():
            node_align.operators.distribute_nodes(nodes, None, "HORIZONTAL")
        return {'FINISHED'}


class BLSL_OT_run_tests(Operator):
    bl_idname = "blsl_compiler.run_tests"
    bl_label = "Run Tests"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return hasattr(space, 'node_tree') and space.node_tree.bl_idname == 'GeometryNodeTree'

    def execute(self, context):
        addon_dir = pathlib.Path(__package__).parent
        tests_dir = os.path.join(addon_dir, 'tests')
        passed = 0
        failed = 0
        skipped = 0
        print()
        for file in pathlib.Path(tests_dir).iterdir():
            if file.suffix != '.py':
                continue

            # skipped tests
            match file.stem:
                case "":
                    continue

            test_ = importlib.import_module(f'.{file.stem}', 'blsl.tests')
            for test in test_._:
                if test.get('skip', False):
                    skipped += 1
                    print(
                        f"\x1b[1;33m[WARN]\x1b[0m {file}: \"{test['title']}\" skipped")
                    continue

                parser = parser_from_src(test['src'])
                ast = parser.parse()
                TyChecker(ast)
                NodeGen(ast, context).emit()
                nt = context.space_data.node_tree
                obj = context.object
                group_out = nt.nodes['Group Output']
                node = nt.nodes[-1]
                sockets = 0
                for output in node.outputs:
                    nt.links.new(output, group_out.inputs[-1])
                    sock = group_out.inputs[-2]
                    sockets += 1
                    name = f"{sock.identifier}_attribute_name"
                    obj.modifiers['tests'][name] = sock.name
                    deps = context.evaluated_depsgraph_get()
                    _obj = obj.evaluated_get(deps)
                    __attr = _obj.data.attributes[sock.name]
                    attr = __attr.data
                    size = len(attr)
                    data = None
                    storage_type = None
                    match ty := __attr.data_type:
                        case 'INT':
                            data = [0] * size
                            storage_type = 'value'
                        case 'FLOAT':
                            data = [0.0] * size
                            storage_type = 'value'
                        case 'FLOAT_VECTOR':
                            size *= 3
                            data = [0.0] * size
                            storage_type = 'vector'
                        case _:
                            assert False, f"{ty}"
                    attr.foreach_get(storage_type, data)
                    assert len(data) == size
                    if storage_type == 'vector':
                        data = np.reshape(data, (1, 3)).tolist()
                    expected = test['output'][sock.name]
                    if data[0] != expected:
                        print(
                            f"\x1b[1;31m[ERR]\x1b[0m {file}: \"{test['title']}\" failed")
                        print(f"    expected: {expected}")
                        print(f"    output: {data[0]}")
                        failed += 1
                    else:
                        passed += 1
                for sock in range(sockets):
                    nt.outputs.remove(nt.outputs[-1])
                nt.nodes.remove(node)
        print()
        if failed:
            plural = "s" if failed > 1 else ""
            print(
                f"  \x1b[1;31m[ERR]\x1b[0m {failed} test{plural} failed", end="")
        else:
            print(f"  \x1b[1;32m[OK]\x1b[0m {passed} tests passed", end="")
        if skipped:
            print(f", {skipped} skipped")
        else:
            print()

        return {'FINISHED'}


class BLSLCompiler(PropertyGroup):
    source_type: bpy.props.EnumProperty(name="Source Type", items=[
        ("INTERNAL", "Internal", ""),
        ("EXTERNAL", "External", ""),
    ])

    text_prop: bpy.props.PointerProperty(type=bpy.types.Text)
    filepath: bpy.props.StringProperty(
        name="Source file", subtype="FILE_PATH", default="")

    debug_ast_output: bpy.props.BoolProperty(name="AST output", default=False)
    debug_token_output: bpy.props.BoolProperty(
        name="Token output", default=False)


classes = [
    BLSL_PT_Panel,
    BLSLCompiler,
    BLSL_OT_compile,
    BLSL_OT_run_tests,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    WindowManager.blsl_compiler = bpy.props.PointerProperty(type=BLSLCompiler)


def unregister():
    del WindowManager.blsl_compiler

    for cls in classes:
        bpy.utils.unregister_class(cls)
