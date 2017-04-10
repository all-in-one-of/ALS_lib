import hou, json, os.path

lightTypes = {"pointLight"       : "point",
              "spotLight"        : "point",
              "directionalLight" : "distant",
              "areaLight"        : "grid",}

shapeTypes = {"Rectangle" : "grid",
              "Disc"      : "disk",
              "Sphere"    : "sphere",
              "Cylinder"  : "tube",
              "Custom"    : "geo",}
              
decayRates = {"None" : "none",
              "linear_distance" : "half",
              "linear" : "half",
              "quadratic_distance" : "physical",
              "quadratic" : "physical",
              "cubic_distance" : "physical",
              "cubic" : "physical",
              None : "none",}
              
  

def clearKeys(node) :
    for child in node.children() :
        if not "lookat_stereo" in child.name() :
            parm_tuple = child.parms()
            for parm in parm_tuple :
                parm.deleteAllKeyframes()
                parm.revertToDefaults()

def objSetKey( parm, frame, value ) :
    key = hou.Keyframe()
    key.setFrame(frame)
    key.setValue(value)
    parm.setKeyframe(key)

def lightImport() :
    node = hou.pwd()
    clearKeys(node)
    file = node.parm("json").eval()
    if os.path.isfile(file) :
        jsonData = open(file, "r")
        lightData = json.load(jsonData)
        
        type        = lightData[1]["lightNodeType"]
        shape       = lightData[1]["lightAreaShape"]
        mentalArea  = lightData[1]["lightUseArea"]
        pos         = lightData[1]["lightPos"]
        rot         = lightData[1]["lightRotate"]
        size        = lightData[1]["lightScale"]
        color       = lightData[1]["lightColor"]
        intensity   = lightData[1]["lightIntesity"]
        decay       = lightData[1]["lightDecayRate"]
        cone        = lightData[1]["lightConeAngle"]
        penumbra    = lightData[1]["lightPenumbraAngle"]
        fr          = len(pos)
        
        light = node.node("light")
        
        light.parm( "light_type" ).set(lightTypes[type])
        light.parm( "atten_type" ).set(decayRates[decay])
        
        if mentalArea : 
            light.parm( "light_type" ).set("grid")
        if shape and type == "spotLight" :
            light.parm("light_type").set(shapeTypes[shape])
            light.parm("coneenable").set(1)
            if mentalArea : light.parm("singlesided").set(1)
        if shape and type == "areaLight" :
            light.parm("light_type").set(shapeTypes[shape])
            #if mentalArea : light.parm("singlesided").set(1)
        
        iter = 0
        #print fr
        for frame in range(1, fr+1) :
            objSetKey( light.parm("tx"), frame, pos[iter][0] )
            objSetKey( light.parm("ty"), frame, pos[iter][1] )
            objSetKey( light.parm("tz"), frame, pos[iter][2] )
            
            objSetKey( light.parm("rx"), frame, rot[iter][0] )
            objSetKey( light.parm("ry"), frame, rot[iter][1] )
            objSetKey( light.parm("rz"), frame, rot[iter][2] )
            
            objSetKey( light.parm("light_colorr"), frame, color[iter][0] )
            objSetKey( light.parm("light_colorg"), frame, color[iter][1] )
            objSetKey( light.parm("light_colorb"), frame, color[iter][2] )
            
            objSetKey( light.parm("light_intensity"), frame, intensity[iter] )
            
            if mentalArea : 
                objSetKey( light.parm("areasize1"), frame, size[iter][0] * 2 )
                objSetKey( light.parm("areasize2"), frame, size[iter][1] * 2 )
            if shape and type == "spotLight" :
                objSetKey( light.parm("coneangle"), frame, cone[iter] )
                objSetKey( light.parm("conedelta"), frame, penumbra[iter] )
                
            iter += 1

def camImport() :
    node = hou.pwd()
    clearKeys(node)
    file = node.parm("json").eval()
    if os.path.isfile(file) :
        jsonData = open(file, "r")
        camData = json.load(jsonData)
        
        res      = camData[1]["resolution"]
        fr       = camData[1]["frames"]
        pos      = camData[1]["camPos"]
        look     = camData[1]["camCentInt"]
        up       = camData[1]["camUpVector"]
        focal    = camData[1]["camFocal"]
        aperture = camData[1]["camAperture"]
        clip     = camData[1]["camClip"]
        fdist    = camData[1]["camFocusDistance"]
        fstop    = camData[1]["camFStop"]
        mblur    = camData[1]["motionBlurBy"]
        p_dist   = camData[1]["p_distance"]
        p_rad    = camData[1]["p_radius"]
        camType  = "stereocamrig"
        
        paralax  = camData[1]["camStereoParallax"]
        ditance  = camData[1]["camStereoDistance"]
        
        if not paralax :
            camType = "cam"
            
        origin = node.node("origin")
        lookat = node.node("lookat")    
        cams = [ None, None, None ]
        
        for child in node.children() :
            if child.type() == hou.nodeType(hou.objNodeTypeCategory(), "cam" ) and child.name() == 'cam' :
                cams[0] = child
            if child.type() == hou.nodeType(hou.objNodeTypeCategory(), "cam" ) and child.name() == 'persp' :
                cams[1] = child
            if child.type() == hou.nodeType(hou.objNodeTypeCategory(), "stereocamrig" ) :
                cams[2] = child
                
        for cam in cams :  
            cam.parm("resx").set(res[0])
            cam.parm("resy").set(res[1])
            cam.parm("shutter").set(mblur[0] * 0.4)
            cam.parm("lookatpath").set("../lookat")
            lens = cam.node('./shopnet1/miDOF_lens')
            if lens :
                cam.parm( 'projection' ).set(4)
                cam.parm( 'vm_lensshader' ).set('./shopnet1/miDOF_lens')
            
            iter = 0
            for frame in fr :
                objSetKey( cam.parm("upx"), frame, up[iter][0] )
                objSetKey( cam.parm("upy"), frame, up[iter][1] )
                objSetKey( cam.parm("upz"), frame, up[iter][2] )
                objSetKey( cam.parm("focal"), frame, focal[iter] )
                objSetKey( cam.parm("aperture"), frame, aperture[iter][0] * 25.4 )
                objSetKey( cam.parm("near"), frame, clip[iter][0] )
                objSetKey( cam.parm("far"),  frame, clip[iter][1] )
                objSetKey( cam.parm("focus"),  frame, fdist[iter] )
                objSetKey( cam.parm("fstop"),  frame, fstop[iter] )
                
                if lens :
                    objSetKey( lens.parm("focus"), frame, p_dist[iter] )
                    objSetKey( lens.parm("radius"), frame, p_rad[iter] )
                
                if camType == "stereocamrig" and cam == cams[1] :
                    objSetKey( cam.parm("ZPS"),  frame, paralax[iter] )
                    objSetKey( cam.parm("interaxial"),  frame, ditance[iter] )
                iter += 1
                
        cams[2].parm("lookatpath").set("../lookat_stereo")
                    
        iter = 0
        for frame in fr :
            objSetKey( origin.parm("tx"), frame, pos[iter][0] )
            objSetKey( origin.parm("ty"), frame, pos[iter][1] )
            objSetKey( origin.parm("tz"), frame, pos[iter][2] )
            
            objSetKey( lookat.parm("tx"), frame, look[iter][0] )
            objSetKey( lookat.parm("ty"), frame, look[iter][1] )
            objSetKey( lookat.parm("tz"), frame, look[iter][2] )
            iter += 1