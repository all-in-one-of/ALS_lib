print "XXXXXXXXXXXXXXXX"
import maya.standalone
maya.standalone.initialize(name='python')
#from pymel.core import *
import maya.cmds as cmds
import sys, time
import json
import xml.etree.ElementTree as ET
import re

if "\\\\Projects\\TOOLS\\MAYA\\scripts\\mr_asa\\" not in sys.path:
    sys.path.append("\\\\Projects\\TOOLS\\MAYA\\scripts\\mr_asa\\")

import abcExport
reload(abcExport)

scene      = sys.argv[1]
start      = sys.argv[2]
end        = sys.argv[3]
abc        = sys.argv[4]
light      = sys.argv[5]
cam        = sys.argv[6]
exportPath = sys.argv[7]
abcFile    = sys.argv[8]
mode       = sys.argv[9]
select     = sys.argv[10]
smooth     = sys.argv[11]
smoothIter = sys.argv[12]
checkMblur = sys.argv[13]
stepsize  = sys.argv[14]
xml_path  = '//PROJECTS/tools/MAYA/scripts/MA/RENDER_PROJECTS.xml'

################################################## mr_asa script #############################################
def read_projects():
    projects = []
    tree = ET.parse(xml_path)
    for i in tree.getroot():
        project = {'name': i.attrib['name'], }
        for j in i:
            if len(j) == 0:
                project[j.tag] = j.text
            else:
                project[j.tag] = [dict([(k.tag, k.text) for k in j]), ]
        projects.append(project)
    return projects

def find(f, seq):
    for item in seq:
        if f(item):
            return item

def find_project(scenepath):
    print "scenepath",scenepath
    all_projects = read_projects()
    project = find(lambda i: re.match(i['scene_pattern'], scenepath, re.I), all_projects)
    return project

################################################## mr_asa script #############################################
'''
def dumpAllObjects() :
    meshes = []
    lights = []
    cams = []

    for name in cmds.ls( type = "mesh", l = True ) :
        meshes.append(name)
    for name in cmds.ls( type = "light", l = True ) :
        lights.append(name)
    for name in cmds.ls( type = "camera", l = True ) :
        cams.append(name)

    with open(exportPath + "/sceneDump.json", 'w') as outfile:
        json.dump({ "cameras":cams,
                    "lights" :lights,
                    "meshes" :meshes }, outfile, indent=4)

    print "Successfully write sceneDump.json file..."
'''

def selectObjects( objects ) :
    for obj in objects :
        obj = obj.strip('"')
        curobj = cmds.ls( obj )
        if curobj : cmds.select( curobj[0], add=True )
        else :
            print "====================================\nNot existing object %s\nAbc export was canseled!\n====================================" % obj
            return None
    selection = cmds.ls( sl = True )
    print "Select objects: %s" % selection
    return selection

def abcWrite() :
    try : cmds.loadPlugin("AbcExport.mll",quiet=1)
    except : pass

    basename = abcFile.split( "/" )[-1].split( ".abc" )[0]
    objects = select.replace(" ", "").split(',')
    f1 = int( start )
    f2 = int( end )

    if mode == "json" :
        jsonData = open("%s/%s.json" % (exportPath, basename), "r")
        sceneData = json.load(jsonData)
        frames = sceneData['frames']
        f1 = frames[0]
        f2 = frames[1]
        objects = sceneData['objects']

    selectObjects(objects)
    print "Exporting %s. (Frame range = %d-%d)" % ( abcFile, f1, f2 )
    print stepsize, float( stepsize )
    abcExport.applyConvertGeom("True",
        extDirectory = exportPath,
        extFileName = basename,
        extCheckSmooth = False if smooth == "0" else True,
        extIterSmooth = int( smoothIter ),
        extFrameRange = [ f1, f2 ],
        extCamAnable = [False,False,False], #[ nead cam export, alembic, fbx ]
        extCheckBlurSubsamples = int( checkMblur ),
        extValFrameStep = float( stepsize ),
        )
    print "Successfully write alembic cache file...$$"

def exportCam() :
    abcExport.convertToJson("camA",
        extDirectory=exportPath, 
        extFrameRange=[int( start ),int( end )] )
    print "Successfully export camA..."

def exportLights() :
    abcExport.convertToJson("lights",
        extDirectory=exportPath, 
        extFrameRange=[int( start ),int( end )],
         )
    print "Successfully export all lights..."

def prepareRenderer( scenepath ) :
    renderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
    if renderer != "mentalRay" :
        project_xml = find_project(scenepath)
        blur = float(project_xml["motion_blur_by"])
        #print "Motion blur be ==> %s" % blur
        try : cmds.loadPlugin("Mayatomr.mll",quiet=1)
        except : pass
        cmds.setAttr('defaultRenderGlobals.ren', 'mentalRay', type='string')
        cmds.setAttr( "miDefaultOptions.motionBlurBy", blur )

def timeline() :
    return [cmds.playbackOptions(q=True, minTime=True), cmds.playbackOptions(q=True, maxTime=True)]

#-------------------------------------------------------------------
print "Initialize maya standalone..."
if abc == "1" :
    cmds.file(scene, open = 1, force = 1)
    #dumpAllObjects()
    
else :
    cmds.file(scene, open = 1, force = 1, lrd = 'none' )

if checkMblur == "1" :
    for i in range( 100 ):
        print "Set defaultRenderGlobals to mentalRay..."
    prepareRenderer( scene )

if abc    == "1" : abcWrite()
if light == "1" : exportLights()
if cam    == "1" : exportCam()
tl = timeline()
#-------------------------------------------------------------------
print "$$========== Successfully completed operation! ==========$$"
print '========== Timeline start - %s; end - %s ==========$$' % ( tl[0], tl[1] )
