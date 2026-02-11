# https://blender.stackexchange.com/questions/57306/how-to-create-a-custom-ui

import bpy

from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty,
                       FloatVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

from bpy.types import Panel, Menu, Operator, PropertyGroup


# all classes defined in this file
CLASSES = []




# ========================================================== Scene Properties


class LensMapperProperties(PropertyGroup):        
    camera: PointerProperty(
        name = "Camera",
        description = "camera to apply the lens drivers to",
        type = bpy.types.Object
        )
        
    lensfile: StringProperty(
        name = "Lens File",
        description = "lens file path (Open Lens File format)",
        default="",
        subtype='FILE_PATH'
        )
        
    #lensmapper: PointerProperty(
    #    name = "Lens Mapper",
    #    description = "custom python object storing the lens file and methods to evaluate it",
    #    type = bpy.types.Object
    #    )
CLASSES.append(LensMapperProperties)




# ========================================================== Operators

# pass




# ========================================================== Menus


class LensMappingUi(bpy.types.Panel):
    bl_label = "[BVP] Lens Mapping"
    bl_idname = "julouj_virtual_prod.lens_mapping_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene.lens_mapping_props, "lensfile", text="Lens File")
        layout.operator("julouj_virtual_prod.lens_mapping_load_op", text="Load Lens File")
        layout.prop(context.scene.lens_mapping_props, "camera", text="Lens Target")
        layout.operator("julouj_virtual_prod.lens_mapping_setup_drivers_op", text="Setup Drivers on Camera")
CLASSES.append(LensMappingUi)




# ========================================================== Registration


def register():
    # register all new classes
    for new_class in CLASSES:
        bpy.utils.register_class(new_class)

    # instantiate our custom properties in the "freed" scene property
    bpy.types.Scene.lens_mapping_props = PointerProperty(type=LensMapperProperties)


def unregister():
    # remove all new classes
    for class_to_remove in reversed(CLASSES):
        bpy.utils.unregister_class(class_to_remove)

    # throw our custom properties into the darkness of memory freeing oblivion
    del bpy.types.Scene.lens_mapping_props



if __name__ == "__main__":
    register()
