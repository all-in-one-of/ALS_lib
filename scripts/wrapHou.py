import os
import sys
import subprocess
import re

#------------------------- users init -----------------------------------
sep = re.search('\/|\\\\', sys.argv[0] ).group()
pythonPath = '/'.join( sys.argv[0].split(sep)[0:-1] + ['python',] )
sys.path.append(pythonPath)
import userInfo

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
if userInfo.profile == 'Anton':
    ROOT_DIR = 'D:'

HOUDINI_INSTALL_PATH='C:/Houdini{}/Houdini_'.format(HOUDINI_MAJOR_RELEASE)
HOUDINI_GLOB_PATH = "{0}/HoudiniProject".format(ROOT_DIR)
LIB_PATH = '{0}/Libraries'.format(HOUDINI_GLOB_PATH)
ALS_PATH = '{0}/ALS_lib'.format(LIB_PATH)
PW_PATH = '{0}/PW_lib'.format(LIB_PATH)
QLIB_PATH = '{0}/qLib'.format(LIB_PATH)
try:
    PYTHONPATH = os.environ['PYTHONPATH']
except(KeyError):
    PYTHONPATH = ''
#
HFS = HOUDINI_INSTALL_PATH + HOUDINI_BUILD
os.environ['HFS'] = HFS 
HB = HFS + '/bin'

#------------------------- get shot information ----------------------------
seqShPat = re.compile('\\\\(?P<job>[^\\\\]*)\\\\seq\d+\\\\(?P<seq>seq\d+)_(?P<sh>sh\d+)(?=_(?P<sub>sub\d+)|\\\\*|\/*)')
# print seqShPat.search(r'D:\HoudiniProjects\scenes\seq000\seq000_sh000').groups()

try:
    filePath = sys.argv[2]
    shotInfo = seqShPat.search(filePath)
    if shotInfo:
        job = shotInfo.group('job')
        seq = shotInfo.group('seq')
        sh = shotInfo.group('sh')
        sub = shotInfo.group('sub')
        shotDir = '{0}/{0}_{1}_{2}'.format(seq, sh, sub) if sub else '{0}/{0}_{1}'.format(seq, sh)
        localDir = '{0}{1}/scenes/{2}'.format(HOUDINI_GLOB_PATH, job, shotDir)
    else:
        localDir = ''

except IndexError:
    filePath = ''
    localDir = ''

#--------------------------- set environment variables ---------------------
globs = {}
globs['PATH'] = [HB, os.environ['PATH']]
globs['HOUDINI_PATH'] = ['{0}'.format(HOUDINI_GLOB_PATH), 
                         localDir,
                         ALS_PATH,
                         QLIB_PATH, '&']

globs['PYTHONPATH'] =  ['{0}/hqt'.format(PW_PATH),
                        '{0}/pw_Houdini_VEX_Editor'.format(PW_PATH),
                        '{0}/pw_MultiScriptEditor'.format(PW_PATH),
                         PYTHONPATH,]

globs['HOUDINI_OTLSCAN_PATH'] = ['{0}/otls/{1}'.format(ALS_PATH, i) for i in ['OBJ', 'SOP', 'DOP', 'ROP']] + ['@/otls']
globs['HOUDINI_OTLSCAN_PATH'] += ['{0}/otls/{1}'.format(QLIB_PATH, i) for i in ['base', 'experimental', 'future', 'graveyard']]

for key, val in globs.iteritems():
    os.environ[key] = os.path.pathsep.join(val)

os.environ['HOUDINI_SPLASH_FILE']= "{0}/icons/houdini15_splash_Anton_Grabovskiy_var1.tif".format(ALS_PATH)
os.environ['VISUAL'] = "C:/Program Files/Sublime Text 3/sublime_text.exe"
os.environ['HOUDINI_USER_PREF_DIR'] = '{0}/preference/{1}/houdini___HVER__'.format(HOUDINI_GLOB_PATH, userInfo.user)
os.environ['HOUDINI_CONSOLE_LINES'] = "1024"
    
if __name__ == '__main__':        
    startpath = ('\"{0}/houdinifx.exe\" {1}'.format(HB, filePath))
    print startpath
    subprocess.Popen(startpath)