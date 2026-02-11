import bpy
import os
import mathutils
import addon_utils
import numpy as np



class AddDistortCompOp(bpy.types.Operator):
    bl_label = "Initialize Camera Hierarchy Operator"
    bl_idname = "julouj_virtual_prod.post_prod_tools_add_distort_comp_op"
    bl_description = "Create a compositing nodegraph that distorts the CG over the plate"

    def execute(self, context):
        scene = context.scene
        props = scene.post_prod_tools_props

        input_video_path = props.plate_path
        overscan = props.overscan


        # switch on nodes and get reference
        scene.use_nodes = True
        tree  = scene.node_tree
        links = tree.links
        nodes = tree.nodes

        # clear default nodes
        #for node in tree.nodes:
        #    tree.nodes.remove(node)


        # --------------------------------------------------------------- Load ST-maps
        # stmaps_frame = nodes.new(type='NodeFrame')
        # stmaps_frame.label = "ST-maps"
        #
        # img = bpy.data.images.load(os.path.join(STMAPS_FOLDER, "distort_Calibration_Z5.592mm_F578mm.exr"), check_existing=False)  # Load the image in data
        #
        # # create stmap image node
        # stmap_node = nodes.new(type='CompositorNodeImage')
        # stmap_node.image = img
        # stmap_node.location = -1000,0
        # stmap_node.parent = stmaps_frame



        # --------------------------------------------------------------- Create Video Plate Input
        img_frame = nodes.new(type='NodeFrame')
        img_frame.label = "Video Plate"

        # create input image node
        img_node = nodes.new(type='CompositorNodeImage')
        if os.path.exists(input_video_path):
            img = bpy.data.images.load(input_video_path, check_existing=False)  # Load the image in data
            img_node.image = img
        img_node.location = 500,700
        img_node.parent = img_frame

        img_viewer = nodes.new(type='CompositorNodeViewer')
        img_viewer.location = 500,900
        img_viewer.parent = img_frame

        link_img_viewer = links.new(img_node.outputs[0], img_viewer.inputs[0])
        
        
        # -------------------------------------------------------------- Create Render Layer
        
        render_frame = nodes.new(type='NodeFrame')
        render_frame.label = "Video Plate"
        
        render_node = nodes.new(type='CompositorNodeRLayers')
        render_node.location = 0,500
        render_node.parent = render_frame
        
        render_viewer = nodes.new(type='CompositorNodeViewer')
        render_viewer.location = 0,900
        render_viewer.parent = render_frame

        link_render_viewer = links.new(render_node.outputs[0], render_viewer.inputs[0])



        """
        # --------------------------------------------------------------- Create Main Pipeline
        sepXYZ_frame = nodes.new(type='NodeFrame')
        sepXYZ_frame.label = "RGBA channels encode distortion. RG: undistort, BA : distort"
        sepXYZ = nodes.new(type="CompositorNodeSeparateXYZ")
        sepXYZ.parent = sepXYZ_frame
        sepXYZ.location = 0,0

        #link_stmaps_sepXYZ = links.new(stmap_node.outputs[0], sepXYZ.inputs[0])

        multAdd_frame = nodes.new(type='NodeFrame')
        multAdd_frame.label = "Map has origin at the top left. Blender expects bottom left"
        multAdd = nodes.new(type="CompositorNodeMath")
        multAdd.operation = "MULTIPLY_ADD"
        multAdd.parent = multAdd_frame
        multAdd.location = 200,-300
        multAdd.inputs[1].default_value = -1
        multAdd.inputs[2].default_value = 1

        link_sepXYZ_multAdd = links.new(sepXYZ.outputs[1], multAdd.inputs[0])

        cmbXYZ_frame = nodes.new(type='NodeFrame')
        cmbXYZ_frame.label = "Apply ST map. Blender requires Z=1 on for this to work"
        cmbXYZ = nodes.new(type="CompositorNodeCombineXYZ")
        cmbXYZ.parent = cmbXYZ_frame
        cmbXYZ.location = 500,0
        cmbXYZ.inputs[2].default_value = 1

        link_sepXYZ_cmbXYZ  = links.new(sepXYZ.outputs[0],  cmbXYZ.inputs[0])
        link_multAdd_cmbXYZ = links.new(multAdd.outputs[0], cmbXYZ.inputs[1])

        mapUV = nodes.new(type="CompositorNodeMapUV")
        mapUV.parent = cmbXYZ_frame
        mapUV.location = 700,0

        link_img_mapUV   = links.new(img_node.outputs[0],  mapUV.inputs[0])
        link_cmbXYZ_mapUV  = links.new(cmbXYZ.outputs[0],  mapUV.inputs[1])


    
        # --------------------------------------------------------------- Distortion Test Block
        distoTest_frame = nodes.new(type='NodeFrame')
        distoTest_frame.label = "View the effect of distortion"

        nodistoScale = nodes.new(type="CompositorNodeScale")
        nodistoScale.parent = distoTest_frame
        nodistoScale.space = "RENDER_SIZE"
        nodistoScale.location = 900,700

        link_img_nodisto = links.new(img_node.outputs[0], nodistoScale.inputs[0])

        nodisto_viewer = nodes.new(type='CompositorNodeViewer')
        nodisto_viewer.location = 1100,700
        nodisto_viewer.parent = distoTest_frame

        link_nodisto_viewer = links.new(nodistoScale.outputs[0], nodisto_viewer.inputs[0])

        distoScale = nodes.new(type="CompositorNodeScale")
        distoScale.parent = distoTest_frame
        distoScale.space = "RENDER_SIZE"
        distoScale.location = 900,500

        link_mapuv_disto = links.new(mapUV.outputs[0], distoScale.inputs[0])

        disto_viewer = nodes.new(type='CompositorNodeViewer')
        disto_viewer.location = 1100,500
        disto_viewer.parent = distoTest_frame

        link_disto_viewer = links.new(distoScale.outputs[0], disto_viewer.inputs[0])
        """
        
        
        
        # --------------------------------------------------------------- Brown-Conrady Distortion Block
        stmaps_frame = nodes.new(type='NodeFrame')
        stmaps_frame.label = "Screen Coordinates"
        
        ADDON_FOLDER = ""
        for mod in addon_utils.modules():
            print(mod.bl_info.get("name"), mod.__file__)
            if "Virtual Prod" in mod.bl_info.get("name"):
                ADDON_FOLDER = os.path.dirname(mod.__file__)
                print(ADDON_FOLDER)
        
        # create stmap image node
        stmap_node = nodes.new(type='CompositorNodeImage')
        if os.path.exists(os.path.join(ADDON_FOLDER, "ScreenCoords.tif")):
            img = bpy.data.images.load(os.path.join(ADDON_FOLDER, "ScreenCoords.tif"), check_existing=False)  # Load the image in data
            stmap_node.image = img
        stmap_node.location = -2400,0
        stmap_node.parent = stmaps_frame
        stmap_node.image.colorspace_settings.name = 'Non-Color'
        
        
        renderScale = nodes.new(type="CompositorNodeScale")
        renderScale.parent = stmaps_frame
        renderScale.space = "RENDER_SIZE"
        renderScale.location = -2200,0

        link_mapuv_scale = links.new(stmap_node.outputs[0], renderScale.inputs[0])


        overscanScale = nodes.new(type="CompositorNodeScale")
        overscanScale.parent = stmaps_frame
        overscanScale.space = "RELATIVE"
        overscanScale.location = -2000,0
        
        link_scale_osscale = links.new(renderScale.outputs[0], overscanScale.inputs[0])
        
        
        divOs = nodes.new(type="CompositorNodeMath")
        divOs.parent = stmaps_frame
        divOs.operation = "DIVIDE"
        divOs.inputs[0].default_value = 1
        divOs.location = -2000,-200
        
        link_divos_osscale = links.new(divOs.outputs[0], overscanScale.inputs[1])
        link_divos_osscale = links.new(divOs.outputs[0], overscanScale.inputs[2])
        
        
        sepXYZ_frame = nodes.new(type='NodeFrame')
        sepXYZ_frame.label = "RGBA channels encode distortion. RG: undistort, BA : distort"
        
        sepXYZ = nodes.new(type="CompositorNodeSeparateXYZ")
        sepXYZ.parent = sepXYZ_frame
        sepXYZ.location = -1800,0

        link_stmaps_sepXYZ = links.new(overscanScale.outputs[0], sepXYZ.inputs[0])
        
        
        x_sub_half = nodes.new(type="CompositorNodeMath")
        x_sub_half.operation = "SUBTRACT"
        x_sub_half.location = -1600,0
        x_sub_half.parent = sepXYZ_frame
        x_sub_half.inputs[0].default_value = 1
        x_sub_half.inputs[1].default_value = 0.5
        
        link_sepXYZ_xSubHalf = links.new(sepXYZ.outputs[0], x_sub_half.inputs[0])
        
        
        y_sub_half = nodes.new(type="CompositorNodeMath")
        y_sub_half.operation = "SUBTRACT"
        y_sub_half.location = -1600,-200
        y_sub_half.parent = sepXYZ_frame
        y_sub_half.inputs[0].default_value = 1
        y_sub_half.inputs[1].default_value = 0.5
        
        link_sepXYZ_ySubHalf = links.new(sepXYZ.outputs[1], y_sub_half.inputs[0])
        
        
        #aspect_value = nodes.new(type="CompositorNodeValue")
        #aspect_value.location = -1600,-500
        #aspect_value.label = "Aspect Ratio"
        #aspect_value.outputs[0].default_value = 16/9
        
        # compute aspect ratio
        aspect_value = nodes.new(type="CompositorNodeMath")
        aspect_value.operation = "DIVIDE"
        aspect_value.label = "Aspect Ratio"
        aspect_value.location = -1800,-400
        aspect_value.inputs[0].default_value = 1920
        aspect_value.inputs[1].default_value = 1080
        
        #link_rx_aspect = links.new(rx_value.outputs[0], aspect_value.inputs[0])
        #link_ry_aspect = links.new(ry_value.outputs[0], aspect_value.inputs[1])
        
        
        
        y_aspect_div = nodes.new(type="CompositorNodeMath")
        y_aspect_div.operation = "DIVIDE"
        y_aspect_div.location = -1400,-200
        y_aspect_div.parent = sepXYZ_frame
        y_aspect_div.inputs[0].default_value = 1
        y_aspect_div.inputs[1].default_value = 0.5
        
        link_ySubHalf_yAspectDiv = links.new(y_sub_half.outputs[0], y_aspect_div.inputs[0])
        link_aspect_yAspectDiv = links.new(aspect_value.outputs[0], y_aspect_div.inputs[1])
        
        
        r2_frame = nodes.new(type='NodeFrame')
        r2_frame.label = "Radius pow 2"
        
        
        x_sq_mult = nodes.new(type="CompositorNodeMath")
        x_sq_mult.operation = "MULTIPLY"
        x_sq_mult.location = -1200,800
        x_sq_mult.parent = r2_frame
        x_sq_mult.inputs[0].default_value = 1
        x_sq_mult.inputs[1].default_value = 0.5
        
        link_xSub_xSq = links.new(x_sub_half.outputs[0], x_sq_mult.inputs[0])
        link_xSub_xSq2 = links.new(x_sub_half.outputs[0], x_sq_mult.inputs[1])
        
        
        y_sq_mult = nodes.new(type="CompositorNodeMath")
        y_sq_mult.operation = "MULTIPLY"
        y_sq_mult.location = -1200,600
        y_sq_mult.parent = r2_frame
        y_sq_mult.inputs[0].default_value = 1
        y_sq_mult.inputs[1].default_value = 0.5
        
        link_ySub_ySq = links.new(y_aspect_div.outputs[0], y_sq_mult.inputs[0])
        link_ySub_ySq2 = links.new(y_aspect_div.outputs[0], y_sq_mult.inputs[1])
        
        
        r2_add = nodes.new(type="CompositorNodeMath")
        r2_add.operation = "ADD"
        r2_add.location = -1000,800
        r2_add.parent = r2_frame
        r2_add.inputs[0].default_value = 1
        r2_add.inputs[1].default_value = 0.5 
        
        link_xSq_r2A = links.new(x_sq_mult.outputs[0], r2_add.inputs[0])
        link_ySq_r2A = links.new(y_sq_mult.outputs[0], r2_add.inputs[1])

        
        
        r4_frame = nodes.new(type='NodeFrame')
        r4_frame.label = "Radius pow 4"
        
        r4_mult = nodes.new(type="CompositorNodeMath")
        r4_mult.operation = "MULTIPLY"
        r4_mult.location = -700,800
        r4_mult.parent = r4_frame
        r4_mult.inputs[0].default_value = 1
        r4_mult.inputs[1].default_value = 0.5
        
        link_r2A_r4M = links.new(r2_add.outputs[0], r4_mult.inputs[0])
        link_r2A_r4M2 = links.new(r2_add.outputs[0], r4_mult.inputs[1])
        
        
        k1_frame = nodes.new(type='NodeFrame')
        k1_frame.label = "K1 displacement"
        
        k2_frame = nodes.new(type='NodeFrame')
        k2_frame.label = "K2 displacement"
        
        k1_node = nodes.new(type="CompositorNodeValue")
        k1_node.location = -1000,400
        k1_node.label = "K1 Disto"
        k1_node.parent = k1_frame
        k1_node.outputs[0].default_value = 0
        
        k2_node = nodes.new(type="CompositorNodeValue")
        k2_node.location = -1000,200
        k2_node.label = "K2 Disto"
        k2_node.parent = k2_frame
        k2_node.outputs[0].default_value = 0
        
        
        k1_mult = nodes.new(type="CompositorNodeMath")
        k1_mult.operation = "MULTIPLY"
        k1_mult.location = -800,400
        k1_mult.parent = k1_frame
        
        link_r2_k1Mult = links.new(r2_add.outputs[0], k1_mult.inputs[0])
        link_k1_k1Mult = links.new(k1_node.outputs[0], k1_mult.inputs[1])
        
        
        k2_mult = nodes.new(type="CompositorNodeMath")
        k2_mult.operation = "MULTIPLY"
        k2_mult.location = -600,200
        k2_mult.parent = k2_frame
        
        link_r4_k2Mult = links.new(r4_mult.outputs[0], k2_mult.inputs[0])
        link_k1_k2Mult = links.new(k2_node.outputs[0], k2_mult.inputs[1])
        
        
        
        cpt_frame = nodes.new(type='NodeFrame')
        cpt_frame.label = "Apply distortion to coords"
        
        
        oneplusk1 = nodes.new(type="CompositorNodeMath")
        oneplusk1.operation = "ADD"
        oneplusk1.location = -400,600
        oneplusk1.parent = cpt_frame
        oneplusk1.inputs[0].default_value = 1
        
        link_1pk1_k1 = links.new(k1_mult.outputs[0], oneplusk1.inputs[1])
        
        oneplusk1plusk2 = nodes.new(type="CompositorNodeMath")
        oneplusk1plusk2.operation = "ADD"
        oneplusk1plusk2.location = -400,400
        oneplusk1plusk2.parent = cpt_frame
        
        link_1pk1pk2_k2   = links.new(k2_mult.outputs[0], oneplusk1plusk2.inputs[0])
        link_1pk1pk2_1pk1 = links.new(oneplusk1.outputs[0], oneplusk1plusk2.inputs[1])
        
        
        distXM = nodes.new(type="CompositorNodeMath")
        distXM.operation = "MULTIPLY"
        distXM.location = -400,200
        distXM.parent = cpt_frame
        
        link_1pk1pk2_distXM = links.new(oneplusk1plusk2.outputs[0], distXM.inputs[0])
        link_x_distXM = links.new(x_sub_half.outputs[0], distXM.inputs[1])
        
        
        distYM = nodes.new(type="CompositorNodeMath")
        distYM.operation = "MULTIPLY"
        distYM.location = -400,0
        distYM.parent = cpt_frame
        
        link_1pk1pk2_distYM = links.new(oneplusk1plusk2.outputs[0], distYM.inputs[0])
        link_y_distYM = links.new(y_aspect_div.outputs[0], distYM.inputs[1])
        
        
        
        
        cmbXYZ_frame = nodes.new(type='NodeFrame')
        cmbXYZ_frame.label = "Recombine coordinates. Blender requires Z=1."
        
        
        y_aspect_mult = nodes.new(type="CompositorNodeMath")
        y_aspect_mult.operation = "MULTIPLY"
        y_aspect_mult.location = -200,-200
        y_aspect_mult.parent = cmbXYZ_frame
        y_aspect_mult.inputs[1].default_value = 0.5
        
        link_distYM_yAspM = links.new(distYM.outputs[0], y_aspect_mult.inputs[0])
        link_aspect_yAspectDiv = links.new(aspect_value.outputs[0], y_aspect_mult.inputs[1])
        
        
        
        
        
        
        # --------------------------------------------------------------- Compute Overscan Block
        overscan_frame = nodes.new(type='NodeFrame')
        overscan_frame.label = "Divide ST coords according to Overscan"
        overscan_frame.parent = cmbXYZ_frame

        os_value = nodes.new(type="CompositorNodeValue")
        os_value.parent = overscan_frame
        os_value.location = 0,-300
        os_value.label = "Overscan"
        os_value.outputs[0].default_value = overscan
        
        link_os_divos = links.new(os_value.outputs[0], divOs.inputs[1])

        os_divide_x = nodes.new(type="CompositorNodeMath")
        os_divide_x.operation = "DIVIDE"
        os_divide_x.parent = overscan_frame
        os_divide_x.location = 0,0
        os_divide_x.inputs[0].default_value = 1
        
        os_divide_y = nodes.new(type="CompositorNodeMath")
        os_divide_y.operation = "DIVIDE"
        os_divide_y.parent = overscan_frame
        os_divide_y.location = 0,200
        os_divide_y.inputs[0].default_value = 1

        link_os_value_divide0 = links.new(distXM.outputs[0], os_divide_x.inputs[0])
        link_os_value_divide1 = links.new(y_aspect_mult.outputs[0], os_divide_y.inputs[0])
        link_os_value_divide2 = links.new(os_value.outputs[0], os_divide_x.inputs[1])
        link_os_value_divide3 = links.new(os_value.outputs[0], os_divide_y.inputs[1])
        
        
        
        # --------------------------------------------------------------- CenterShift Block
        centershift_frame = nodes.new(type='NodeFrame')
        centershift_frame.label = "Centershift"
        #centershift_frame.parent = cmbXYZ_frame

        cx_value = nodes.new(type="CompositorNodeValue")
        cx_value.parent = centershift_frame
        cx_value.location = 0,-600
        cx_value.label = "Cx"
        cx_value.outputs[0].default_value = 0
        
        cy_value = nodes.new(type="CompositorNodeValue")
        cy_value.parent = centershift_frame
        cy_value.location = 0,-800
        cy_value.label = "Cy"
        cy_value.outputs[0].default_value = 0
        
        
        cx_invert = nodes.new(type="CompositorNodeMath")
        cx_invert.operation = "MULTIPLY"
        cx_invert.parent = centershift_frame
        cx_invert.location = 200,-600
        cx_invert.inputs[0].default_value = 1
        cx_invert.inputs[1].default_value = -1
        
        link_cx_value_invert = links.new(cx_value.outputs[0], cx_invert.inputs[0])
        
        
        # get image size
        rx_value = nodes.new(type="CompositorNodeValue")
        rx_value.parent = centershift_frame
        rx_value.location = -400,-600
        rx_value.label = "Resolution X"
        rx_value.outputs[0].default_value = 1920
        
        ry_value = nodes.new(type="CompositorNodeValue")
        ry_value.parent = centershift_frame
        ry_value.location = -400,-800
        ry_value.label = "Resolution Y"
        ry_value.outputs[0].default_value = 1080
        
        rx_half = nodes.new(type="CompositorNodeMath")
        rx_half.operation = "DIVIDE"
        rx_half.parent = centershift_frame
        rx_half.location = -200,-600
        rx_half.inputs[0].default_value = 1920
        rx_half.inputs[1].default_value = 2
        
        ry_half = nodes.new(type="CompositorNodeMath")
        ry_half.operation = "DIVIDE"
        ry_half.parent = centershift_frame
        ry_half.location = -200,-800
        ry_half.inputs[0].default_value = 1080
        ry_half.inputs[1].default_value = 2
        
        link_rx_half = links.new(rx_value.outputs[0], rx_half.inputs[0])
        link_ry_half = links.new(ry_value.outputs[0], ry_half.inputs[0])
        
        
        cx_add_halfres = nodes.new(type="CompositorNodeMath")
        cx_add_halfres.operation = "ADD"
        cx_add_halfres.parent = centershift_frame
        cx_add_halfres.location = 400,-600
        cx_add_halfres.inputs[0].default_value = 1
        cx_add_halfres.inputs[1].default_value = 960
        
        cy_add_halfres = nodes.new(type="CompositorNodeMath")
        cy_add_halfres.operation = "ADD"
        cy_add_halfres.parent = centershift_frame
        cy_add_halfres.location = 400,-800
        cy_add_halfres.inputs[0].default_value = 1
        cy_add_halfres.inputs[1].default_value = 540
        
        link_cx_add_halfres = links.new(cx_invert.outputs[0], cx_add_halfres.inputs[0])
        link_cy_add_halfres = links.new(cy_value.outputs[0], cy_add_halfres.inputs[0])
        link_rx_add_halfres = links.new(rx_half.outputs[0], cx_add_halfres.inputs[1])
        link_ry_add_halfres = links.new(ry_half.outputs[0], cy_add_halfres.inputs[1])
        
        
        cx_divide_res = nodes.new(type="CompositorNodeMath")
        cx_divide_res.operation = "DIVIDE"
        cx_divide_res.parent = centershift_frame
        cx_divide_res.location = 600,-600
        cx_divide_res.inputs[0].default_value = 1
        cx_divide_res.inputs[1].default_value = 1920
        
        cy_divide_res = nodes.new(type="CompositorNodeMath")
        cy_divide_res.operation = "DIVIDE"
        cy_divide_res.parent = centershift_frame
        cy_divide_res.location = 600,-800
        cy_divide_res.inputs[0].default_value = 1
        cy_divide_res.inputs[1].default_value = 1080
        
        link_cx_divide_res = links.new(cx_add_halfres.outputs[0], cx_divide_res.inputs[0])
        link_cy_divide_res = links.new(cy_add_halfres.outputs[0], cy_divide_res.inputs[0])
        link_rx_divide_res = links.new(rx_value.outputs[0], cx_divide_res.inputs[1])
        link_ry_divide_res = links.new(ry_value.outputs[0], cy_divide_res.inputs[1])
        
        
        
        
        # link aspect ratio
        link_rx_aspect = links.new(rx_value.outputs[0], aspect_value.inputs[0])
        link_ry_aspect = links.new(ry_value.outputs[0], aspect_value.inputs[1])
        
        
        
        
        x_add_half = nodes.new(type="CompositorNodeMath")
        x_add_half.operation = "ADD"
        x_add_half.location = 200,200
        x_add_half.parent = cmbXYZ_frame
        x_add_half.inputs[1].default_value = 0.5
        
        link_distXM_xAddH= links.new(os_divide_x.outputs[0], x_add_half.inputs[0])
        
        
        y_add_half = nodes.new(type="CompositorNodeMath")
        y_add_half.operation = "ADD"
        y_add_half.location = 200,0
        y_add_half.parent = cmbXYZ_frame
        y_add_half.inputs[1].default_value = 0.5
        
        link_yAspM_yAddH= links.new(os_divide_y.outputs[0], y_add_half.inputs[0])
        
        # link Centershift
        link_cx_x_add_half = links.new(cx_divide_res.outputs[0], x_add_half.inputs[1])
        link_cy_y_add_half = links.new(cy_divide_res.outputs[0], y_add_half.inputs[1])
        
        
        
   
        
        
        
        
        
        cmbXYZ = nodes.new(type="CompositorNodeCombineXYZ")
        cmbXYZ.parent = cmbXYZ_frame
        cmbXYZ.location = 500,0
        cmbXYZ.inputs[2].default_value = 1

        link_sepXYZ_cmbXYZ  = links.new(x_add_half.outputs[0],  cmbXYZ.inputs[0])
        link_sepXYZ_cmbXYZ_2 = links.new(y_add_half.outputs[0], cmbXYZ.inputs[1])

        mapUV = nodes.new(type="CompositorNodeMapUV")
        mapUV.parent = cmbXYZ_frame
        mapUV.location = 700,0

        link_render_mapUV   = links.new(render_node.outputs[0],  mapUV.inputs[0])
        link_cmbXYZ_mapUV  = links.new(cmbXYZ.outputs[0],  mapUV.inputs[1])


        """
        # --------------------------------------------------------------- Compute Overscan Block
        overscan_frame = nodes.new(type='NodeFrame')
        overscan_frame.label = "Do overscan now as this will be used as ref later for CG"

        os_value = nodes.new(type="CompositorNodeValue")
        os_value.parent = overscan_frame
        os_value.location = 1000,-300
        os_value.outputs[0].default_value = overscan

        os_divide = nodes.new(type="CompositorNodeMath")
        os_divide.operation = "DIVIDE"
        os_divide.parent = overscan_frame
        os_divide.location = 1200,-300
        os_divide.inputs[0].default_value = 1

        link_os_value_divide = links.new(os_value.outputs[0], os_divide.inputs[1])



        # --------------------------------------------------------------- Apply Overscan Block
        scale_frame = nodes.new(type='NodeFrame')
        scale_frame.label = "Scale the undistorted plate to render size including overscan"
        # render size should account for overscan, put render size in plugin and overwrite
        # the size in render settings

        renderScale = nodes.new(type="CompositorNodeScale")
        renderScale.parent = scale_frame
        renderScale.space = "RENDER_SIZE"
        renderScale.location = 1100,100

        link_mapuv_scale = links.new(mapUV.outputs[0], renderScale.inputs[0])

        overscanScale = nodes.new(type="CompositorNodeScale")
        overscanScale.parent = scale_frame
        overscanScale.space = "RELATIVE"
        overscanScale.location = 1300,100

        link_rs_os = links.new(renderScale.outputs[0], overscanScale.inputs[0])
        link_os_1 = links.new(os_divide.outputs[0], overscanScale.inputs[1])
        link_os_2 = links.new(os_divide.outputs[0], overscanScale.inputs[2])
        """
        """
        platerenderScale = nodes.new(type="CompositorNodeScale")
        platerenderScale.parent = scale_frame
        platerenderScale.space = "RENDER_SIZE"
        platerenderScale.location = 1100,300

        link_mapuv_scale = links.new(img_node.outputs[0], platerenderScale.inputs[0])

        plateoverscanScale = nodes.new(type="CompositorNodeScale")
        plateoverscanScale.parent = scale_frame
        plateoverscanScale.space = "RELATIVE"
        plateoverscanScale.location = 1300,300

        link_rs_os = links.new(platerenderScale.outputs[0], plateoverscanScale.inputs[0])
        link_os_1 = links.new(os_divide.outputs[0], plateoverscanScale.inputs[1])
        link_os_2 = links.new(os_divide.outputs[0], plateoverscanScale.inputs[2])
        """
        
        
        # --------------------------------------------------------------- Compositing Block
        comp_frame = nodes.new(type='NodeFrame')
        comp_frame.label = "Scale the undistorted plate to render size including overscan"
        
        compAO = nodes.new(type="CompositorNodeAlphaOver")
        compAO.parent = comp_frame
        compAO.location = 1600,0
        
        link_img_ao = links.new(img_node.outputs[0], compAO.inputs[1])
        link_render_ao = links.new(mapUV.outputs[0], compAO.inputs[2])



        # --------------------------------------------------------------- Output Block
        output_frame = nodes.new(type='NodeFrame')
        output_frame.label = "Output"

        output_reroute = nodes.new(type='NodeReroute')
        output_reroute.location = 1950,10
        output_reroute.parent = output_frame

        link_reroute_viewer = links.new(compAO.outputs[0], output_reroute.inputs[0])

        output_viewer = nodes.new(type='CompositorNodeViewer')
        output_viewer.location = 2000,100
        output_viewer.parent = output_frame

        link_reroute_viewer = links.new(output_reroute.outputs[0], output_viewer.inputs[0])

        comp_node = tree.nodes.new('CompositorNodeComposite')
        comp_node.location = 2000,0
        comp_node.parent = output_frame

        link_reroute_output = links.new(output_reroute.outputs[0], comp_node.inputs[0])

        # link nodes
        #link = links.new(stmap_node.outputs[0], comp_node.inputs[0])
        return {'FINISHED'}



def register():
    bpy.utils.register_class(AddDistortCompOp)


def unregister():
    bpy.utils.unregister_class(AddDistortCompOp)
