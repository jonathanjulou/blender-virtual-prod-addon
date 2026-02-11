# https://blender.stackexchange.com/questions/57306/how-to-create-a-custom-ui

import bpy

from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty,
                       FloatVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

from bpy.types import Panel, Menu, Operator, PropertyGroup


#from PostProdTools_ImportCSV import initialize_camera_hierarchy, import_CSV


# all classes defined in this file
CLASSES = []




# ========================================================== Scene Properties


class PostProdToolsProperties(PropertyGroup):
    plate_path: StringProperty(
        name = "Video Plate Path",
        description="path to the video plate from the camera",
        default = "",
        subtype='FILE_PATH'
        )

    stmaps_path: StringProperty(
        name = "ST-maps Folder Path",
        description="path to the folder containing the sampled ST-maps",
        default = "",
        subtype='FILE_PATH'
        )

    tracking_CSV_path: StringProperty(
        name = "EZtrack CSV File Path",
        description="path to the tracking CSV file",
        default = "",
        subtype='FILE_PATH'
        )

    tracking_origin: PointerProperty(
        name = "Tracking Origin",
        description = "tracking origin, the zero of the tracking. It's an empty that can be moved in the scene to move the whole tracking",
        type = bpy.types.Object
        )

    tracking_gripper: PointerProperty(
        name = "Tracking Gripper",
        description = "tracking gripper, where the tracking is applied. It receives all position/rotation data",
        type = bpy.types.Object
        )

    camera: PointerProperty(
        name = "Camera",
        description = "camera that will drive the lens distortion (using its focal length and focus distance) and receive lens tracking data",
        type = bpy.types.Object
        )

    timecode_h: IntProperty(
        name = "Timecode Hour",
        description = "video start TC hour",
        default = 0
        )

    timecode_m: IntProperty(
        name = "Timecode Minute",
        description = "video start TC minute",
        default = 0
        )

    timecode_s: IntProperty(
        name = "Timecode Second",
        description = "video start TC second",
        default = 0
        )

    timecode_f: IntProperty(
        name = "Timecode Frame",
        description = "video start TC frame",
        default = 0
        )

    video_frame_offset: IntProperty(
        name = "Video Frame Offset",
        description = "video frame offset",
        default = 0
        )

    tracking_frame_offset: IntProperty(
        name = "Tracking Frame Offset",
        description = "tracking frame offset",
        default = 0
        )

    max_tracking_frames: IntProperty(
        name = "Max Tracking Frames",
        description = "maximum number of imported tracking frames. 0 means no limit",
        default = 0
        )

    render_width: IntProperty(
        name = "Render Width",
        description = "base render width in pixels",
        default = 1920
        )

    render_height: IntProperty(
        name = "Render Height",
        description = "base render height in pixels",
        default = 1080
        )

    overscan: FloatProperty(
        name = "Overscan",
        description = "overscan ratio to account for distortion. Render resolution will be scaled from base resolution by that factor",
        default = 1
        )
CLASSES.append(PostProdToolsProperties)




# ========================================================== Operators


class ApplyResolutionOp(Operator):
    bl_label = "Apply Resolution Operator"
    bl_idname = "julouj_virtual_prod.post_prod_tools_apply_resolution_op"
    bl_description = "Apply base resolution + overscan in output settings. Will overwrite the current render resolution"

    def execute(self, context):
        scene = context.scene
        props = scene.post_prod_tools_props

        new_width = props.render_width * props.overscan
        new_height = props.render_height * props.overscan

        scene.render.resolution_x = int(new_width)
        scene.render.resolution_y = int(new_height)

        print("Applied new render resolution: {}x{}".format(new_width, new_height))

        return {'FINISHED'}
CLASSES.append(ApplyResolutionOp)


# ========================================================== Menus


class PostProdToolsUi(bpy.types.Panel):
    bl_label = "[BVP] Post Prod Tools"
    bl_idname = "julouj_virtual_prod.post_prod_tools_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
CLASSES.append(PostProdToolsUi)


class TimecodeUi(bpy.types.Panel):
    bl_label = "Timecode Settings"
    bl_parent_id = "julouj_virtual_prod.post_prod_tools_ui"
    bl_idname = "julouj_virtual_prod.post_prod_tools_timecode_settings_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        props = context.scene.post_prod_tools_props

        layout.prop(props, "timecode_h")
        layout.prop(props, "timecode_m")
        layout.prop(props, "timecode_s")
        layout.prop(props, "timecode_f")
CLASSES.append(TimecodeUi)


class RenderResolutionUi(bpy.types.Panel):
    bl_label = "Render Resolution Settings"
    bl_parent_id = "julouj_virtual_prod.post_prod_tools_ui"
    bl_idname = "julouj_virtual_prod.post_prod_tools_render_resolution_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        props = context.scene.post_prod_tools_props

        layout.prop(props, "render_width")
        layout.prop(props, "render_height")
        layout.prop(props, "overscan")

        layout.operator("julouj_virtual_prod.post_prod_tools_apply_resolution_op", text="Apply Resolution")
CLASSES.append(RenderResolutionUi)


class CameraSetupUi(bpy.types.Panel):
    bl_label = "Camera Setup"
    bl_parent_id = "julouj_virtual_prod.post_prod_tools_ui"
    bl_idname = "julouj_virtual_prod.post_prod_tools_camera_setup_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        props = context.scene.post_prod_tools_props

        layout.operator("julouj_virtual_prod.post_prod_tools_initialize_camera_op", text="Initialize Camera Hierarchy")

        layout.prop(props, "tracking_origin")
        layout.prop(props, "tracking_gripper")
        layout.prop(props, "camera")

CLASSES.append(CameraSetupUi)


class ImportTrackingCSVUi(bpy.types.Panel):
    bl_label = "Import EZtrack CSV"
    bl_parent_id = "julouj_virtual_prod.post_prod_tools_ui"
    bl_idname = "julouj_virtual_prod.post_prod_tools_import_csv_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        props = context.scene.post_prod_tools_props

        layout.prop(props, "tracking_CSV_path")
        layout.prop(props, "tracking_frame_offset")
        layout.prop(props, "video_frame_offset")
        layout.prop(props, "max_tracking_frames")

        layout.operator("julouj_virtual_prod.post_prod_tools_import_tracking_csv_op", text="Import EZtrack CSV")
CLASSES.append(ImportTrackingCSVUi)


class CompositeUi(bpy.types.Panel):
    bl_label = "Compositing Presets"
    bl_parent_id = "julouj_virtual_prod.post_prod_tools_ui"
    bl_idname = "julouj_virtual_prod.post_prod_tools_composite_ui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        props = context.scene.post_prod_tools_props

        layout.prop(props, "plate_path")
        #layout.prop(props, "stmaps_path")
        layout.prop(props, "camera")
        layout.prop(props, "overscan")

        layout.operator("julouj_virtual_prod.post_prod_tools_add_undistort_comp_op", text="Add Undistort Plate Comp Graph")
        layout.operator("julouj_virtual_prod.post_prod_tools_add_distort_comp_op", text="Add Distort CG Over Plate Comp Graph")
CLASSES.append(CompositeUi)


# class CompositeUndistortUi(bpy.types.Panel):
#     bl_label = "Undistortion Compositing Preset"
#     bl_parent_id = "julouj_virtual_prod.post_prod_tools_ui"
#     bl_idname = "julouj_virtual_prod.post_prod_tools_composite_undistort_ui"
#     bl_space_type = 'PROPERTIES'
#     bl_region_type = 'WINDOW'
#     bl_context = "output"
#
#     def draw(self, context):
#         layout = self.layout
#         props = context.scene.post_prod_tools_props
#
#         layout.prop(props, "plate_path")
#         layout.prop(props, "stmaps_path")
#         layout.prop(props, "camera")
#         layout.prop(props, "overscan")
# CLASSES.append(CompositeUi)





# ========================================================== Registration


def register():
    # register all new classes
    for new_class in CLASSES:
        bpy.utils.register_class(new_class)

    # instantiate our custom properties in the "freed" scene property
    bpy.types.Scene.post_prod_tools_props = PointerProperty(type=PostProdToolsProperties)


def unregister():
    # remove all new classes
    for class_to_remove in reversed(CLASSES):
        bpy.utils.unregister_class(class_to_remove)

    # throw our custom properties into the darkness of memory freeing oblivion
    del bpy.types.Scene.post_prod_tools_props



if __name__ == "__main__":
    register()
