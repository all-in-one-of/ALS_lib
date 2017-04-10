import os
import sys
import subprocess
import re

profile = os.path.expandvars("%userprofile%").split('\\')[-1]
users = {'a.grabovski' : 'a.grabovski',
         'a.krylevsky' : 'a.krylevsky',
         'Anton'       : 'a.grabovski',}

user  = users[profile] if profile in users else 'default'

#------------------------- get version string ----------------------------
try:
    HOUDINI_BUILD = sys.argv[1]
except IndexError:
    HOUDINI_BUILD = '16.0.557'

vpat = re.compile('(?P<maj>\d+)\.(?P<min>\d+)\.(?P<build>\d+)(?=$|\.(?P<pack>\d+))') #pattern for build version
vers = vpat.match(HOUDINI_BUILD)

HOUDINI_MAJOR_RELEASE = vers.group('maj')
HOUDINI_MINOR_RELEASE = vers.group('min')
HOUDINI_BUILD_VERSION = vers.group('build')
HOUDINI_PACK_VERSION  = vers.group('pack')

#--------------------------- get project and bin path ----------------------
ROOT_DIR = '//PROJECTS/Alisa_Film'
if profile == 'Anton':
    ROOT_DIR = 'D:'

HOUDINI_INSTALL_PATH='C:/Houdini{}/Houdini_'.format(HOUDINI_MAJOR_RELEASE)
HOUDINI_GLOB_PATH = "{0}/HoudiniProject".format(ROOT_DIR)
ALS_PATH = '{0}/ALS_lib'.format(HOUDINI_GLOB_PATH)
#
HFS = HOUDINI_INSTALL_PATH + HOUDINI_BUILD
os.environ['HFS'] = HFS 
HB = HFS + '/bin'

#------------------------- get shot information ----------------------------
seqShPat = re.compile('\\\\(?P<proj>[^\\\\]*)\\\\seq\d+\\\\(?P<seq>seq\d+)_(?P<sh>sh\d+)(?=_(?P<sub>sub\d+)|\\\\*|\/*)')
# print seqShPat.search(r'D:\HoudiniProjects\scenes\seq000\seq000_sh000').groups()

try:
    filePath = sys.argv[1]
    shotInfo = seqShPat.search(filePath)
    proj = shotInfo.group('proj')
    seq = shotInfo.group('seq')
    sh = shotInfo.group('sh')
    sub = shotInfo.group('sub')
    shotDir = '{0}/{0}_{1}_{2}'.format(seq, sh, sub) if sub else '{0}/{0}_{1}'.format(seq, sh)
    localDir = '{0}{1}/scenes/{2}'.format(HOUDINI_GLOB_PATH, proj, shotDir)

except IndexError:
    filePath = ''
    localDir = ''

#--------------------------- set environment variables ---------------------
def setGlobVar(varName, valList):
    os.environ[varName] = os.path.pathsep.join(valList)
#
PATH = [HB, os.environ['PATH']]
HOUDINI_PATH = ['{0}'.format( HOUDINI_GLOB_PATH ), localDir, '&']
HOUDINI_DSO_PATH = ['{0}/dso/'.format(HOUDINI_GLOB_PATH),'@/dso']
HOUDINI_GALLERY_PATH = ['{0}/gallery/'.format(ALS_PATH),'@/gallery']
HOUDINI_OTLSCAN_PATH = ['{0}/otls/{1}'.format(ALS_PATH, i) for i in ['OBJ', 'SOP', 'DOP', 'ROP']] + ['@/otls']
HOUDINI_SCRIPT_PATH = ['{0}/scripts'.format(ALS_PATH), '@/scripts']
HOUDINI_TOOLBAR_PATH = ['{0}/toolbar/'.format(ALS_PATH),'@/toolbar']
HOUDINI_VEX_PATH = ['{0}/vex/^'.format(ALS_PATH),'@/vex/^']
PYTHON_PANEL_PATH = ['{0}/python_panels'.format(ALS_PATH), '&']

setGlobVar('PATH', PATH)
setGlobVar('HOUDINI_PATH', HOUDINI_PATH)
setGlobVar('HOUDINI_DSO_PATH', HOUDINI_DSO_PATH)
setGlobVar('HOUDINI_GALLERY_PATH', HOUDINI_GALLERY_PATH)
setGlobVar('HOUDINI_OTLSCAN_PATH', HOUDINI_OTLSCAN_PATH)
setGlobVar('HOUDINI_SCRIPT_PATH', HOUDINI_SCRIPT_PATH)
setGlobVar('HOUDINI_TOOLBAR_PATH', HOUDINI_TOOLBAR_PATH)
setGlobVar('HOUDINI_VEX_PATH', HOUDINI_VEX_PATH)
setGlobVar('PYTHON_PANEL_PATH', PYTHON_PANEL_PATH)

os.environ['HOUDINI_SPLASH_FILE']= "{0}/icons/houdini15_splash_Anton_Grabovskiy_var1.tif".format(ALS_PATH)
os.environ['VISUAL'] = "C:/Program Files/Sublime Text 3/sublime_text.exe"
os.environ['HOUDINI_USER_PREF_DIR'] = '{0}/preference/{1}/houdini___HVER__'.format(HOUDINI_GLOB_PATH, user)
os.environ['HOUDINI_CONSOLE_LINES'] = "1024"
    
if __name__ == '__main__':        
    startpath = ('\"{0}/houdinifx.exe\" {1}'.format(HB, filePath))
    subprocess.Popen(startpath)