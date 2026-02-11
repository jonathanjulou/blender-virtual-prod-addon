import bpy
import mathutils
import numpy as np



def ZXY_to_quat(yaw, pitch, roll):
    yaw*=(np.pi/180)
    pitch*=-(np.pi/180)
    roll*=-(np.pi/180)

    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)

    q = np.zeros(4)
    q[0] = cy * cr * cp + sy * sr * sp
    q[1] = sy * cr * cp - cy * sr * sp
    q[2] = cy * sr * cp + sy * cr * sp
    q[3] = cy * cr * sp - sy * sr * cp

    return q




class InitCameraOp(bpy.types.Operator):
    bl_label = "Initialize Camera Hierarchy Operator"
    bl_idname = "julouj_virtual_prod.post_prod_tools_initialize_camera_op"
    bl_description = "Create a hierarchy with tracking origin, tracking gripper and camera"

    def execute(self, context):
        scene = context.scene
        props = scene.post_prod_tools_props

        # create the tracking empty
        tracking_origin = bpy.data.objects.new("TrackingOrigin", None)
        scene.collection.objects.link(tracking_origin)
        tracking_origin.empty_display_size = 2
        tracking_origin.empty_display_type = 'PLAIN_AXES'
        tracking_origin.location = (0, 0, 0)
        tracking_origin.rotation_euler = (0, 0, 0)

        # create the tracking empty
        tracking_gripper = bpy.data.objects.new("TrackingGripper", None)
        scene.collection.objects.link(tracking_gripper)
        tracking_gripper.empty_display_size = 2
        tracking_gripper.empty_display_type = 'PLAIN_AXES'
        tracking_gripper.location = (0, 0, 0)
        tracking_gripper.rotation_euler = (0, 0, 0)
        tracking_gripper.parent = tracking_origin

        # create the camera
        camera = bpy.data.cameras.new("Camera")

        # create the camera object
        obj_camera = bpy.data.objects.new("Camera", camera)
        obj_camera.location = (0, 0, 0)
        obj_camera.rotation_euler = (0, 0, 0)
        obj_camera.parent = tracking_gripper

        scene.collection.objects.link(obj_camera)

        props.tracking_origin = tracking_origin
        props.tracking_gripper = tracking_gripper
        props.camera = obj_camera

        return {'FINISHED'}







class ImportTrackingCSVOp(bpy.types.Operator):
    bl_label = "Import Tracking CSV Operator"
    bl_idname = "julouj_virtual_prod.post_prod_tools_import_tracking_csv_op"
    bl_description = "Import tracking data on selected camera using EZtrack CSV format"

    def execute(self, context):
        scene = context.scene
        props = scene.post_prod_tools_props

# def import_CSV(scene, obj_tracking, obj_camera, camera, filepath_tracking_csv_data,
#                video_tc_start_h, video_tc_start_m, video_tc_start_s, video_tc_start_f,
#                framerate, video_tc_start_offset, tracking_tc_offset, overscan):
        obj_tracking = props.tracking_gripper
        obj_camera = props.camera

        # find camera associated to the camera object
        camera = obj_camera.data
        #camera = None
        #for cam in bpy.data.cameras:
        #    if cam.parent == obj_camera:
        #        camera = cam

        #if camera is None:
        #    print("ERROR: could not find camera associated to camera object")
        #    return {'FINISHED'}

        filepath_tracking_csv_data = props.tracking_CSV_path
        video_tc_start_h = props.timecode_h
        video_tc_start_m = props.timecode_m
        video_tc_start_s = props.timecode_s
        video_tc_start_f = props.timecode_f
        framerate = float(scene.render.fps)
        video_tc_start_offset = props.video_frame_offset
        tracking_tc_offset = props.tracking_frame_offset
        overscan = props.overscan

        max_frames = props.max_tracking_frames

        # convert TC to frames using framerate. expecting integer framerate, todo test behavior with drop frame
        video_tc_start = ((((video_tc_start_h*60)+video_tc_start_m)*60)+video_tc_start_s)*framerate+video_tc_start_f + video_tc_start_offset

        # clear all keyframes
        obj_tracking.animation_data_clear()
        obj_camera.animation_data_clear()
        camera.animation_data_clear()

        # align starting time
        tracking_starting_tc = 0
        with open(filepath_tracking_csv_data, "r") as f:
            for line in f:
                splitline = line.split(",")
                if (not line.startswith("Camera Model")) and len(splitline) > 2: # avoid empty lines

                    # TC of the frame, check against video start TC to align tracking
                    f = int(splitline[10])
                    s = int(splitline[11])
                    m = int(splitline[12])
                    h = int(splitline[13])

                    print(f,s,m,h)

                    tracking_starting_tc = ((((h*60)+m)*60)+s)*24+f
                    print("starting tracking tc read")
                    break

        print(tracking_starting_tc)
        print(video_tc_start)

        #current_frame = 1
        # video started before tracking
        #if VIDEO_TC_START < tracking_starting_tc:
        current_frame = tracking_starting_tc - video_tc_start + tracking_tc_offset
        n_frames = 0
        print(current_frame)




        # load frame by frame data
        with open(filepath_tracking_csv_data, "r") as f:
            for line in f:
                splitline = line.split(",")
                if (not line.startswith("Camera Model")) and len(splitline) > 2: # avoid empty lines
                    #print(current_frame)

                    # TC of the frame, check against video start TC to align tracking
                    f = int(splitline[10])
                    s = int(splitline[11])
                    m = int(splitline[12])
                    h = int(splitline[13])

                    tracking_frame_tc = ((((h*60)+m)*60)+s)*24+f


                    # read sensor size from file
                    sensor_width = float(splitline[6])
                    sensor_height = float(splitline[7])

                    # apply to belnder camera
                    camera.sensor_width = sensor_width*overscan
                    camera.sensor_height = sensor_width*overscan


                    # rotation
                    pan = -float(splitline[20])
                    tilt = float(splitline[21])
                    roll = float(splitline[22])

                    # position
                    x = float(splitline[24])/1000
                    y = float(splitline[25])/1000
                    z = float(splitline[26])/1000

                    # lens
                    entrance_pupil = -float(splitline[31])/1000 # Z points back in blender, invert entrance pupil offset
                    focal_length = float(splitline[34])
                    focus_distance = float(splitline[36])/1000


                    # transform to the blender referential
                    position_world = [x, y, z]
                    nodal_offset = [0, 0, entrance_pupil]

                    quat = ZXY_to_quat(pan, tilt-90, roll) # -90 to handle blender default camera orientation (toward the ground)
                    quat2 = np.array([quat[3],quat[0],quat[1],quat[2]])
                    rotation_world = mathutils.Quaternion(quat2)


                    # apply the transforms to the blender camera
                    obj_tracking.location = position_world

                    obj_tracking.rotation_mode = 'QUATERNION'
                    obj_tracking.rotation_quaternion = rotation_world

                    obj_tracking.keyframe_insert(data_path="rotation_quaternion", frame=current_frame)
                    obj_tracking.keyframe_insert(data_path="location", frame=current_frame)


                    # apply the lens data to the camera
                    obj_camera.location = nodal_offset

                    camera.lens = focal_length
                    camera.dof.focus_distance = focus_distance #- entrance_pupil

                    obj_camera.keyframe_insert(data_path="location", frame=current_frame)
                    camera.keyframe_insert(data_path="lens", frame=current_frame)
                    camera.dof.keyframe_insert(data_path="focus_distance", frame=current_frame)


                    # go to next frame
                    #scene.frame_set(current_frame)
                    current_frame += 1
                    n_frames += 1
                    # break if n_frames positive. Zero or Negative means no limit
                    if max_frames > 0 and n_frames > max_frames:
                        break

            return {'FINISHED'}



def register():
    bpy.utils.register_class(InitCameraOp)
    bpy.utils.register_class(ImportTrackingCSVOp)


def unregister():
    bpy.utils.unregister_class(InitCameraOp)
    bpy.utils.unregister_class(ImportTrackingCSVOp)
