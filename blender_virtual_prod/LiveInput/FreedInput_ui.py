# https://blender.stackexchange.com/questions/57306/how-to-create-a-custom-ui

import bpy

from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty,
                       FloatVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

from bpy.types import Panel, Menu, Operator, PropertyGroup


# all classes defined in this file
CLASSES = []




# ========================================================== Scene Properties


class FreedReceiverProperties(PropertyGroup):
    ip: StringProperty(
        name = "IP",
        description="receiver ip",
        default = "0.0.0.0",
        )

    port: StringProperty(
        name = "Port",
        description="receiver port",
        default = "5000",
        )

    posetarget: PointerProperty(
        name = "Pose Target",
        description = "object linked to the freed receiver for pose",
        type = bpy.types.Object
        )
        
    lenstarget: PointerProperty(
        name = "Lens Target",
        description = "object linked to the freed receiver for lens",
        type = bpy.types.Object
        )

CLASSES.append(FreedReceiverProperties)




class SceneProperties(PropertyGroup):
    is_running: BoolProperty(
        name="Is Running",
        description="Are freed receivers already running ?",
        default = False
        )

CLASSES.append(SceneProperties)




# ========================================================== Operators


class StartOp(Operator):
    bl_label = "Start Receiving Operator"
    bl_idname = "julouj_virtual_prod.freed_input_start_op"
    bl_description = "Start receiving FreeD data"

    def execute(self, context):
        scene = context.scene
        freed = scene.virtual_prod_props

        print("starting freed receiving...")

        while not freed.is_running:
            bpy.ops.julouj_virtual_prod.freed_input_modal_operator('INVOKE_DEFAULT')

        return {'FINISHED'}
CLASSES.append(StartOp)


class StopOp(Operator):
    bl_label = "Stop Receiving Operator"
    bl_idname = "julouj_virtual_prod.freed_input_stop_op"
    bl_description = "Stop receiving FreeD data"

    def execute(self, context):
        scene = context.scene
        freed = scene.virtual_prod_props

        print("stopping freed receiving...")

        freed.is_running = False

        return {'FINISHED'}
CLASSES.append(StopOp)




# ========================================================== Menus


class BlenderFreedUi(bpy.types.Panel):
    bl_label = "[BVP] Live FreeD Input"
    bl_idname = "julouj_virtual_prod.freed_input_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        layout.operator("julouj_virtual_prod.freed_input_start_op", text="Start")
        layout.operator("julouj_virtual_prod.freed_input_stop_op", text="Stop")
CLASSES.append(BlenderFreedUi)








class ReceiverListUi(bpy.types.Panel):
    bl_label = "Tracking Receivers"
    bl_parent_id = "julouj_virtual_prod.freed_input_ui"
    bl_idname = "julouj_virtual_prod.freed_input_receiver_list_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
CLASSES.append(ReceiverListUi)


class FreedReceiverUi_0(bpy.types.Panel):
    bl_label = "Freed Receiver 0 (Camera)"
    bl_parent_id = "julouj_virtual_prod.freed_input_receiver_list_ui"
    bl_idname = "julouj_virtual_prod.freed_input_freed_receiver_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        self.layout.prop(context.scene.freed_receiver_0, "ip")
        self.layout.prop(context.scene.freed_receiver_0, "port")
        self.layout.prop(context.scene.freed_receiver_0, "posetarget", text="Pose Target")
        self.layout.prop(context.scene.freed_receiver_0, "lenstarget", text="Lens Target")
CLASSES.append(FreedReceiverUi_0)


class FreedReceiverUi_1(bpy.types.Panel):
    bl_label = "Freed Receiver 1"
    bl_parent_id = "julouj_virtual_prod.freed_input_receiver_list_ui"
    bl_idname = "julouj_virtual_prod.freed_input_freed_receiver_ui_1"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        self.layout.prop(context.scene.freed_receiver_1, "ip")
        self.layout.prop(context.scene.freed_receiver_1, "port")
        self.layout.prop(context.scene.freed_receiver_1, "posetarget")
CLASSES.append(FreedReceiverUi_1)


class FreedReceiverUi_2(bpy.types.Panel):
    bl_label = "Freed Receiver 2"
    bl_parent_id = "julouj_virtual_prod.freed_input_receiver_list_ui"
    bl_idname = "julouj_virtual_prod.freed_input_freed_receiver_ui_2"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        self.layout.prop(context.scene.freed_receiver_2, "ip")
        self.layout.prop(context.scene.freed_receiver_2, "port")
        self.layout.prop(context.scene.freed_receiver_2, "posetarget")
CLASSES.append(FreedReceiverUi_2)


class FreedReceiverUi_3(bpy.types.Panel):
    bl_label = "Freed Receiver 3"
    bl_parent_id = "julouj_virtual_prod.freed_input_receiver_list_ui"
    bl_idname = "julouj_virtual_prod.freed_input_freed_receiver_ui_3"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        self.layout.prop(context.scene.freed_receiver_3, "ip")
        self.layout.prop(context.scene.freed_receiver_3, "port")
        self.layout.prop(context.scene.freed_receiver_3, "posetarget")
CLASSES.append(FreedReceiverUi_3)




"""
class LensFilesListUi(bpy.types.Panel):
    bl_label = "Lens File"
    bl_parent_id = "julouj_virtual_prod.freed_input_ui"
    bl_idname = "julouj_virtual_prod.freed_input_lens_files_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        self.layout.prop(context.scene.freed_receiver_0, "lensfile", text="Lens File")
        self.layout.prop(context.scene.freed_receiver_0, "lenstarget", text="Lens Target")
        #self.layout.prop(context.scene.freed_receiver_1, "lensfile", text="R-2 Lens File")
        #self.layout.prop(context.scene.freed_receiver_2, "lensfile", text="R-3 Lens File")
        #self.layout.prop(context.scene.freed_receiver_3, "lensfile", text="R-4 Lens File")
        self.layout.operator("julouj_virtual_prod.freed_input_start_op", text="Start")
CLASSES.append(LensFilesListUi)
"""


# ========================================================== Registration


def register():
    # register all new classes
    for new_class in CLASSES:
        bpy.utils.register_class(new_class)

    # instantiate our custom properties in the "freed" scene property
    bpy.types.Scene.virtual_prod_props = PointerProperty(type=SceneProperties)
    bpy.types.Scene.freed_receiver_0 = PointerProperty(type=FreedReceiverProperties)
    bpy.types.Scene.freed_receiver_1 = PointerProperty(type=FreedReceiverProperties)
    bpy.types.Scene.freed_receiver_2 = PointerProperty(type=FreedReceiverProperties)
    bpy.types.Scene.freed_receiver_3 = PointerProperty(type=FreedReceiverProperties)


def unregister():
    # remove all new classes
    for class_to_remove in reversed(CLASSES):
        bpy.utils.unregister_class(class_to_remove)

    # throw our custom properties into the darkness of memory freeing oblivion
    del bpy.types.Scene.virtual_prod_props



if __name__ == "__main__":
    register()
