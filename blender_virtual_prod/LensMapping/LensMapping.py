import os
import bpy
import mathutils

import numpy as np

from .LensFile import LensFile





class LensMapper:

    def __init__(self, lens_file=None, isOCV=False):
        self.lens_file = None
        self.isOCV = isOCV
        self.initialize(lens_file)

        
    def initialize(self, lens_file):
        print("initialize {}".format(lens_file))
        if lens_file is not None and lens_file != "":
            self.lens_file = LensFile()
            
            if lens_file.endswith(".json"):
                self.isOCV = False
        
            if os.path.exists(lens_file):
                print("receiver initialized with lens file {}".format(lens_file))
                self.lens_file.initialize(lens_file)
            else:
                print("path {} does not exist".format(lens_file))
                
                
    def getK1U(self, zoom, focus):
        # no lens file, return default value
        if self.lens_file is None:
            return 0
            
        if self.isOCV:
            return self.lens_file.getK1UndistortWidthNormalized(zoom, focus)
        return self.lens_file.getK1UndistortOCV(zoom, focus)
    
    
    def getK1D(self, zoom, focus):
        # no lens file, return default value
        if self.lens_file is None:
            return 0
        
        if self.isOCV:
            return self.lens_file.getK1DistortWidthNormalized(zoom, focus)
        return self.lens_file.getK1DistortOCV(zoom, focus)
    
    
    def getK2U(self, zoom, focus):
        # no lens file, return default value
        if self.lens_file is None:
            return 0
        
        if self.isOCV:
            return self.lens_file.getK2UndistortWidthNormalized(zoom, focus)
        return self.lens_file.getK2UndistortOCV(zoom, focus)
    
    
    def getK2D(self, zoom, focus):
        # no lens file, return default value
        if self.lens_file is None:
            return 0
        
        if self.isOCV:
            return self.lens_file.getK2DistortWidthNormalized(zoom, focus)
        return self.lens_file.getK2DistortOCV(zoom, focus)
    
    
    def getFocal(self, zoom, focus):
        # no lens file, return default value
        if self.lens_file is None:
            return 50 #mm
        
        return self.lens_file.getFocalMM(zoom, focus)
    
    
    def getFocus(self, zoom, focus):
        # no lens file, return default value
        if self.lens_file is None:
            return 1 #m
        
        return self.lens_file.getFocusDistanceM(zoom, focus)
    
    
    def getEPD(self, zoom, focus):
        # no lens file, return default value
        if self.lens_file is None:
            return 0 #m
        
        return self.lens_file.getNodal(zoom, focus)
    
    
    def getSensorWidth(self):
        # no lens file, return default value
        if self.lens_file is None:
            return 9.59
        
        return self.lens_file.getSensorWidth()
    
    
    def getCx(self):
        # no lens file, return default value
        if self.lens_file is None:
            return 0
        
        return self.lens_file.getCxPix()
    
    
    def getCy(self):
        # no lens file, return default value
        if self.lens_file is None:
            return 0
        
        return self.lens_file.getCyPix()


LENSMAPPER = LensMapper() #f initialize with empty mapper

# register methods for drivers
bpy.app.driver_namespace['getK1U']   = LENSMAPPER.getK1U
bpy.app.driver_namespace['getK1D']   = LENSMAPPER.getK1D
bpy.app.driver_namespace['getK2U']   = LENSMAPPER.getK2U
bpy.app.driver_namespace['getK2D']   = LENSMAPPER.getK2D
bpy.app.driver_namespace['getFocal'] = LENSMAPPER.getFocal
bpy.app.driver_namespace['getFocus'] = LENSMAPPER.getFocus
bpy.app.driver_namespace['getEPD']   = LENSMAPPER.getEPD
bpy.app.driver_namespace['getSensorWidth'] = LENSMAPPER.getSensorWidth
bpy.app.driver_namespace['getCx'] = LENSMAPPER.getCx
bpy.app.driver_namespace['getCy'] = LENSMAPPER.getCy


class LoadLensFileOp(bpy.types.Operator):
    bl_label = "Load Lens File Operator"
    bl_idname = "julouj_virtual_prod.lens_mapping_load_op"
    bl_description = "Load the lens file and declares driver aware conversion functions"

    def execute(self, context):
        global LENSMAPPER
        scene = context.scene
        props = scene.lens_mapping_props

        print("load lens file...")

        # blender uses mangled relative path notation
        lens_file = bpy.path.abspath(props.lensfile)
            
        print("lens file is {}".format(lens_file), os.path.exists(lens_file))
        if lens_file is not None and lens_file != "":
            if os.path.exists(lens_file):
                LENSMAPPER.initialize(lens_file)
                
                # re-register methods
                bpy.app.driver_namespace['getK1U']   = LENSMAPPER.getK1U
                bpy.app.driver_namespace['getK1D']   = LENSMAPPER.getK1D
                bpy.app.driver_namespace['getK2U']   = LENSMAPPER.getK2U
                bpy.app.driver_namespace['getK2D']   = LENSMAPPER.getK2D
                bpy.app.driver_namespace['getFocal'] = LENSMAPPER.getFocal
                bpy.app.driver_namespace['getFocus'] = LENSMAPPER.getFocus
                bpy.app.driver_namespace['getEPD']   = LENSMAPPER.getEPD
                bpy.app.driver_namespace['getSensorWidth'] = LENSMAPPER.getSensorWidth

        return {'FINISHED'}



class SetupCamDriversOp(bpy.types.Operator):
    bl_label = "Setup Camera Drivers Operator"
    bl_idname = "julouj_virtual_prod.lens_mapping_setup_drivers_op"
    bl_description = "Apply a set of drivers on a camera to control focal length and focus distance from normalized zoom and focus controls"

    def execute(self, context):
        global LENSMAPPER
        scene = context.scene
        props = scene.lens_mapping_props

        print("apply driver setup...")

        cam = props.camera
        if cam is not None and cam.type == 'CAMERA':
            # create custom curves for lens data (control and distortion)
            cam.data['0_zoom'] = 0
            cam.data['0_focus'] = 0
            #cam.data['Focal Length'] = 0.0
            #cam.data['Focus Distance'] = 0.0
            #cam.data['Entrance Pupil'] = 0.0
            cam.data['K1 Undisto'] = 0.0000000000000001
            cam.data['K2 Undisto'] = 0.0000000000000001
            cam.data['K1 Disto'] = -0.0000000000000001
            cam.data['K2 Disto'] = -0.0000000000000001
            cam.data['Cx'] = 0
            cam.data['Cy'] = 0
            
            # put right sensor size
            cam.data.sensor_fit = "HORIZONTAL"
            cam.data.sensor_width = LENSMAPPER.getSensorWidth()
            
            # create drivers
            focal_driver = cam.data.driver_add("lens").driver
            focal_driver.expression = 'getFocal(bpy.data.cameras["{}"]["0_zoom"],bpy.data.cameras["{}"]["0_focus"])'.format(cam.data.name, cam.data.name)
            
            focus_driver = cam.data.dof.driver_add("focus_distance").driver
            focus_driver.expression = 'getFocus(bpy.data.cameras["{}"]["0_zoom"],bpy.data.cameras["{}"]["0_focus"])'.format(cam.data.name, cam.data.name)
            
            focal_driver = cam.data.driver_add('["K1 Undisto"]').driver
            focal_driver.expression = 'getK1U(bpy.data.cameras["{}"]["0_zoom"],bpy.data.cameras["{}"]["0_focus"])'.format(cam.data.name, cam.data.name)
            
            focal_driver = cam.data.driver_add('["K2 Undisto"]').driver
            focal_driver.expression = 'getK2U(bpy.data.cameras["{}"]["0_zoom"],bpy.data.cameras["{}"]["0_focus"])'.format(cam.data.name, cam.data.name)
            
            focal_driver = cam.data.driver_add('["K1 Disto"]').driver
            focal_driver.expression = 'getK1D(bpy.data.cameras["{}"]["0_zoom"],bpy.data.cameras["{}"]["0_focus"])'.format(cam.data.name, cam.data.name)
            
            focal_driver = cam.data.driver_add('["K2 Disto"]').driver
            focal_driver.expression = 'getK2D(bpy.data.cameras["{}"]["0_zoom"],bpy.data.cameras["{}"]["0_focus"])'.format(cam.data.name, cam.data.name)
            
            focal_driver = cam.data.driver_add('["Cx"]').driver
            focal_driver.expression = 'getCx()'.format(cam.data.name, cam.data.name)
            
            focal_driver = cam.data.driver_add('["Cy"]').driver
            focal_driver.expression = 'getCy()'.format(cam.data.name, cam.data.name)
            
            focal_driver = cam.driver_add("location", 2).driver
            focal_driver.expression = '-getEPD(bpy.data.cameras["{}"]["0_zoom"],bpy.data.cameras["{}"]["0_focus"])'.format(cam.data.name, cam.data.name)
        else:
            print("object {} is not a camera".format(cam))
            
        print(LENSMAPPER)

        return {'FINISHED'}



def register():
    bpy.utils.register_class(LoadLensFileOp)
    bpy.utils.register_class(SetupCamDriversOp)


def unregister():
    bpy.utils.unregister_class(LoadLensFileOp)
    bpy.utils.unregister_class(SetupCamDriversOp)
