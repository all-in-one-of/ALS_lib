import os,sys,subprocess, socket, platform
system = platform.system()

user = os.path.expandvars("%userprofile%").split('\\')[-1]
users = [ 'a.grabovski', 'a.krylevsky' ]

SOLIDANGLE = '//PROJECTS/Alisa_Film/HoudiniProject/Solidangle/htoa/htoa-1.14.3_r9b05dbe_houdini-16.0.557'

HOUDINI_MAJOR_RELEASE = '16' 
HOUDINI_MINOR_RELEASE = '0' 
HOUDINI_BUILD_VERSION = '557' 
HOUDINI_PACK_VERSION  = ''
# 
HOUDINI_INSTALL_PATH='C:/Houdini16/Houdini_'
# if socket.gethostname() == "os_01" or socket.gethostname() == "rrw01":
#     HOUDINI_INSTALL_PATH='C:/Program Files/Side Effects Software/Houdini '
    
    
HOUDINI_GLOB_PATH = "//PROJECTS/Alisa_Film/HoudiniProject"
if system == "Linux" :
    HOUDINI_INSTALL_PATH = '/opt/hfs'
    HOUDINI_GLOB_PATH = "/projects/Alisa_Film/HoudiniProject"

if HOUDINI_PACK_VERSION :
    HOUDINI_BUILD = '%s.%s.%s.%s'%( 
    HOUDINI_MAJOR_RELEASE, 
    HOUDINI_MINOR_RELEASE, 
    HOUDINI_BUILD_VERSION,
    HOUDINI_PACK_VERSION)
else :
    HOUDINI_BUILD = '%s.%s.%s'%( 
    HOUDINI_MAJOR_RELEASE, 
    HOUDINI_MINOR_RELEASE, 
    HOUDINI_BUILD_VERSION)
    
# 
HFS = HOUDINI_INSTALL_PATH + HOUDINI_BUILD
os.environ['HFS']=HFS 

# 
HB = HFS + '/bin'
os.environ['PATH']=os.path.pathsep.join([HB,os.environ['PATH']])


#
file = None
localDir = None
try :
    file = sys.argv[1]
    sep = "\\" if system == "Windows" else "/"
    partsList = file.split("\\")
    for part in partsList :
        if "_sh" in part :
            shPath = part.split("_")
            seq  = shPath[0]
            sh = shPath[1]
            localDir = "%s/%s_%s" % ( seq, seq, sh )
            break
except :
    file = ''
#

os.environ['HOUDINI_PATH'] = os.path.pathsep.join(['%s'%HOUDINI_GLOB_PATH,'&'])
os.environ['HOUDINI_SCRIPT_PATH'] = os.path.pathsep.join(['%s/scripts/'%HOUDINI_GLOB_PATH,'@/scripts'])
os.environ['HOUDINI_OTLSCAN_PATH']= os.path.pathsep.join(['%s/hda/'%HOUDINI_GLOB_PATH,
                                                          '%s/hda/OBJ/'%HOUDINI_GLOB_PATH,
                                                          '%s/hda/SOP/'%HOUDINI_GLOB_PATH,
                                                          '%s/hda/DOP/'%HOUDINI_GLOB_PATH,
                                                          '%s/hda/Octane/'%HOUDINI_GLOB_PATH,
                                                          '%s/hda/ROP/'%HOUDINI_GLOB_PATH, '@/otls'])
os.environ['HOUDINI_VEX_PATH']= os.path.pathsep.join(['%s/vex/^'%HOUDINI_GLOB_PATH,'@/vex/^'])
os.environ['HOUDINI_DSO_PATH']= os.path.pathsep.join(['%s/dso/^'%HOUDINI_GLOB_PATH,'@/dso'])
os.environ['HOUDINI_GALLERY_PATH']= os.path.pathsep.join(['%s/gallery/'%HOUDINI_GLOB_PATH,'@/gallery'])
os.environ['HOUDINI_TOOLBAR_PATH']= os.path.pathsep.join(['%s/toolbar/'%HOUDINI_GLOB_PATH,'@/toolbar'])

os.environ['HOUDINI_SPLASH_FILE']= "%s/icons/houdini15_splash_Anton_Grabovskiy_var2.tif"%HOUDINI_GLOB_PATH
os.environ['VISUAL']= "C:/Program Files/Sublime Text 2/sublime_text.exe"


os.environ['HOUDINI_USER_PREF_DIR'] = '%s/preference/%s/houdini___HVER__'% ( HOUDINI_GLOB_PATH, user )

os.environ['HOUDINI_CONSOLE_LINES'] = "1024"
#os.environ['HOUDINI_UISCALE'] = '20'


if localDir :
    os.environ['HOUDINI_OTLSCAN_PATH'] = '%s/hda/%s;'%(HOUDINI_GLOB_PATH, localDir) + os.environ['HOUDINI_OTLSCAN_PATH']
    os.environ['HOUDINI_GALLERY_PATH'] = '%s/gallery/%s;'%(HOUDINI_GLOB_PATH, localDir) + os.environ['HOUDINI_GALLERY_PATH']

os.environ[ 'PYTHON_PANEL_PATH' ] = '%s/python_panels;' % HOUDINI_GLOB_PATH

# htoa config start
# os.environ['PATH']=os.path.pathsep.join([HB,os.environ['PATH'], '{}/scripts/bin'.format(SOLIDANGLE) ])
# os.environ['HOUDINI_PATH'] = os.path.pathsep.join([SOLIDANGLE, os.environ['HOUDINI_PATH']])
# htoa config end

    
if __name__ == '__main__':        
    startpath = ('\"%s/houdinifx\" %s' % (HB, file))
    #print socket.gethostname()
    #print startpath
    subprocess.Popen(startpath)