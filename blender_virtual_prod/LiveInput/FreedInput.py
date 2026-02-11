import os
import bpy
import mathutils

import numpy as np

from .Freed import FreedReceiver


def ZYX_to_quat(yaw, pitch, roll):
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



class FreedReferential:

    def __init__(self, linked_object=None, is_camera=False, lens_file=None, camera=None):
        self.position_world = np.zeros(3)
        self.rotation_world = mathutils.Quaternion(np.zeros(4))
        self.zoom  = 0
        self.focus = 0
        self.current_frame = 1
        self.linked_object = linked_object
        self.is_camera = is_camera
        self.camera = camera
        
        if self.is_camera and self.camera is not None:
            # create custom curves for lens data
            self.camera.data['0_zoom'] = 0
            self.camera.data['0_focus'] = 0
            self.camera.data['K1 Undisto'] = 0.0000000000000001
            self.camera.data['K2 Undisto'] = 0.0000000000000001
            self.camera.data['K1 Disto'] = -0.0000000000000001
            self.camera.data['K2 Disto'] = -0.0000000000000001


    def updateCallback(self,data):
        """
            called at each received freed message
        """
        self.position_world[0] = data[0]/1000 # convert to meters
        self.position_world[1] = data[1]/1000
        self.position_world[2] = data[2]/1000

        yaw   = -data[3]
        pitch = data[4]
        roll  = data[5]

        quat = ZYX_to_quat(yaw, pitch-90, roll)
        quat2 = np.array([quat[3],quat[0],quat[1],quat[2]])
        self.rotation_world = mathutils.Quaternion(quat2)

        self.zoom = data[6]
        self.focus = data[7]

        if self.linked_object is not None:
            self.updateLinkedObject()


    def updateLinkedObject(self):
        """
            update linked object position and rotation and write to frames
        """
        self.linked_object.location = self.position_world

        quat = self.rotation_world
        self.linked_object.rotation_mode = 'QUATERNION'
        self.linked_object.rotation_quaternion = quat

        self.linked_object.keyframe_insert(data_path="rotation_quaternion", frame=self.current_frame)
        self.linked_object.keyframe_insert(data_path="location", frame=self.current_frame)
        
        self.update_camera()
        
        self.current_frame += 1
        
        
    def update_camera(self):
        if self.is_camera and self.camera is not None:
            self.camera.data['0_zoom'] = self.zoom
            self.camera.data['0_focus'] = self.focus
            self.camera.data.keyframe_insert(data_path='["0_zoom"]', frame=self.current_frame)
            self.camera.data.keyframe_insert(data_path='["0_focus"]', frame=self.current_frame)
            
            if 'getK1U' in bpy.app.driver_namespace:
                k1U_widthone = bpy.app.driver_namespace['getK1U'](self.zoom, self.focus)
                k1D_widthone = bpy.app.driver_namespace['getK1D'](self.zoom, self.focus)
                k2U_widthone = bpy.app.driver_namespace['getK2U'](self.zoom, self.focus)
                k2D_widthone = bpy.app.driver_namespace['getK2D'](self.zoom, self.focus)
                focal = bpy.app.driver_namespace['getFocal'](self.zoom, self.focus)
                focus = bpy.app.driver_namespace['getFocus'](self.zoom, self.focus)
                epd = bpy.app.driver_namespace['getEPD'](self.zoom, self.focus)
                
                self.camera.data['K1 Undisto'] = k1U_widthone
                self.camera.data['K2 Undisto'] = k2U_widthone
                self.camera.data['K1 Disto'] = k1D_widthone
                self.camera.data['K2 Disto'] = k2D_widthone
                self.camera.data.keyframe_insert(data_path='["K1 Undisto"]', frame=self.current_frame)
                self.camera.data.keyframe_insert(data_path='["K2 Undisto"]', frame=self.current_frame)
                self.camera.data.keyframe_insert(data_path='["K1 Disto"]', frame=self.current_frame)
                self.camera.data.keyframe_insert(data_path='["K2 Disto"]', frame=self.current_frame)
                
                # TODO add a try except here to handle object not being a camera
                self.camera.data.lens = focal
                self.camera.data.keyframe_insert(data_path='lens', frame=self.current_frame)
                
                self.camera.data.dof.focus_distance = focus
                self.camera.data.dof.keyframe_insert(data_path='focus_distance', frame=self.current_frame)
                
                self.camera.location = [0,0,-epd]
                self.camera.keyframe_insert(data_path="location", frame=self.current_frame)
                



class ModalOperator(bpy.types.Operator):
    bl_idname = "julouj_virtual_prod.freed_input_modal_operator"
    bl_label = "Main Loop to Receive FreeD Data"

    def initialize(self, context):
        print("Start")

        self.n_trackers = 0
        self.tracker_frames = []
        self.receivers = []

        self.tracker_ips = []   # add trackers ip here
        self.tracker_ports = [] # add trackers ports here
        self.tracker_objects = [] # add scene objects corresponding to trackers
        self.cam = None # add scene objects corresponding to trackers


        if type(context.scene.freed_receiver_0["posetarget"]) == bpy.types.Object:
            self.tracker_ips.append(context.scene.freed_receiver_0.ip)
            self.tracker_ports.append(int(context.scene.freed_receiver_0.port))
            self.tracker_objects.append(context.scene.freed_receiver_0.posetarget)
            self.cam = context.scene.freed_receiver_0.lenstarget

        if type(context.scene.freed_receiver_1["posetarget"]) == bpy.types.Object:
            self.tracker_ips.append(context.scene.freed_receiver_1.ip)
            self.tracker_ports.append(int(context.scene.freed_receiver_1.port))
            self.tracker_objects.append(context.scene.freed_receiver_1.posetarget)

        if type(context.scene.freed_receiver_2["posetarget"]) == bpy.types.Object:
            self.tracker_ips.append(context.scene.freed_receiver_2.ip)
            self.tracker_ports.append(int(context.scene.freed_receiver_2.port))
            self.tracker_objects.append(context.scene.freed_receiver_2.posetarget)

        if type(context.scene.freed_receiver_3["posetarget"]) == bpy.types.Object:
            self.tracker_ips.append(context.scene.freed_receiver_3.ip)
            self.tracker_ports.append(int(context.scene.freed_receiver_3.port))
            self.tracker_objects.append(context.scene.freed_receiver_3.posetarget)


        self.n_trackers = len(self.tracker_ips)
        if self.n_trackers == 0:
            print("no objects targeted, running in the darkness of the void")

        for i in range(self.n_trackers):
            tracked_object = self.tracker_objects[i]
            if tracked_object is not None:
                # remove all animation data
                if tracked_object.animation_data: #Check for presence of animation data.
                    tracked_object.animation_data.action = None

                # link object to freed receiver
                self.tracker_frames.append(FreedReferential(tracked_object,
                                                            is_camera = i==0,
                                                            camera = self.cam
                                                            ))

                # freed input
                self.receivers.append(FreedReceiver(self.tracker_ips[i], self.tracker_ports[i], self.tracker_frames[i].updateCallback))
                self.receivers[i].start()


    def __del__(self):
        self.stop()


    def stop(self):
        try:
            for i in range(self.n_trackers):
                try:
                    self.receivers[i].stop()
                except:
                    print("could not close receiver for tracker on port", self.tracker_ports[i])
        except:
            pass

        print("End")


    def execute(self, context):
        context.scene.virtual_prod_props.is_running = True
        self.initialize(context)

        return {'FINISHED'}


    def modal(self, context, event): # executed in the event loop, as long as 'RUNNING_MODAL' or 'PASS_THROUGH' has been issued
        if event.type == 'ESC' or not context.scene.virtual_prod_props.is_running: # press escape to end
            self.stop()
            context.scene.virtual_prod_props.is_running = False
            return {'FINISHED'}

        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        self.execute(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}



def register():
    bpy.utils.register_class(ModalOperator)


def unregister():
    bpy.utils.unregister_class(ModalOperator)
