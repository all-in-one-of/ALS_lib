# import hou, os, platform
# system = platform.system()
# user = os.path.expandvars("%userprofile%").split('\\')[-1]
# users = [ 'a.grabovski', 'a.krylevsky' ]
# job = os.environ['HOUDINI_PATH'].split("%s" % ( ":" if system == "Linux" else ";" ) )[0] 

# mayajob = "//PROJECTS/Alisa_Film/MayaProject"
# if system == "Linux" : mayajob = mayajob.replace( "//PROJECTS", "/projects" )
# hou.hscript('set -g "%s"="%s"' % ('JOB',  job    ) )
# hou.hscript('set -g "%s"="%s"' % ('MJOB', mayajob) )
# hipPath = hou.hipFile.path()
# partsList = hipPath.split("/")
# #------------- init variables -----------------
# seq  = ''
# sh = ''
# rcpath = ''
# HDataPath = ''
# Data_Server = ''
# HDataStore = ''
# MDataPath = ''
# MCachePath = ''
# mScenesPath = ''
# flipPath = ''
# perforce = ''
# vexPath = ''
# simPath = ''
# proxyPath = ''
# renderPath = ''
# lightSetup = ''
# refPath = ''
# #--------------- parse path ------------------
# for part in partsList :
#     if "_sh" in part :
#         shPath = part.split("_")
#         seq  = shPath[0]
#         sh = shPath[1]
#         break
# #------------------ create dirs ----------------        
# if seq != '' :
#     rcpath = "//POST/film/RenderCompose/%s/%s_%s" % (seq, seq, sh)
#     if system == "Linux" : rcpath = rcpath.replace( "//POST", "/post" )
#     HDataPath = "%s/data/%s/%s_%s" % ( job, seq, seq, sh )
#     Data_Server = HDataPath
#     HDataStore = "%s/data_store/%s/%s_%s" % ( job, seq, seq, sh )
#     if user in users :
#         HDataPath = HDataPath.replace( job, 'Q:/houdini' )
#     MDataPath = "%s/_Export" % ( rcpath )
#     MCachePath = "%s/cache/alembic/%s/%s_%s" % ( mayajob, seq, seq, sh )
#     mScenesPath = ( "Q:/Film/Scenes/%s" % ( seq ) )
#     flipPath = ( "%s/flip/%s/%s_%s" % ( job, seq, seq, sh ))
#     perforce = ( "Q:/Film/Scenes/%s/%s_%s.ma" % ( seq, seq, sh ) )
#     vexPath  = ( "%s/vex_wrangles/%s/%s_%s" % ( job, seq, seq, sh ) )
#     simPath = ( "%s/sim/%s/%s_%s" % ( job, seq, seq, sh ) )
#     proxyPath = ( "%s/proxy/%s/%s_%s" % ( job, seq, seq, sh ) )
#     renderPath = ( '%s/OppositeLayer/MasterBeauty' % rcpath )
#     lightSetup = ( '%s/RND_files/render_%s_master/LS' % ( mayajob, seq ) )
#     refPath = ( "%s/references/%s/%s_%s" % ( job, seq, seq, sh ))
#     pathList = [ rcpath, HDataPath, HDataStore, MDataPath, MCachePath, flipPath, vexPath, simPath, proxyPath, refPath ]
#     for pathDir in pathList :
#         if not os.path.exists( pathDir ) :
#             lst = pathDir.replace("//","##").split("/")
#             current = []
#             for num, part in enumerate( lst ) :
#                 current.append(part)
#                 pathString = "/".join(current).replace("##", "//")
#                 currentPath =  pathString if system == "Windows" else "/" + pathString
#                 if not os.path.exists( currentPath ) :
#                     try :
#                         os.mkdir( currentPath )
#                     except :
#                         pass

# #-------------- set houdini vaiables --------------
# hou.hscript('set -g "%s"="%s"' % ('SEQ', seq ))
# hou.hscript('set -g "%s"="%s"' % ('SH', sh ))
# hou.hscript('set -g "%s"="%s"' % ('RCPATH', rcpath))
# hou.hscript('set -g "%s"="%s"' % ('HDATA', HDataPath))
# hou.hscript('set -g "%s"="%s"' % ('HDATA_GLOB', Data_Server))
# hou.hscript('set -g "%s"="%s"' % ('DATA_STORE', HDataStore))
# hou.hscript('set -g "%s"="%s"' % ('SIMPATH', simPath))
# hou.hscript('set -g "%s"="%s"' % ('PROXY', proxyPath))
# hou.hscript('set -g "%s"="%s"' % ('MDATA', MDataPath))
# hou.hscript('set -g "%s"="%s"' % ('MCACHE', MCachePath))
# hou.hscript('set -g "%s"="%s"' % ('MSCENES', mScenesPath))
# hou.hscript('set -g "%s"="%s"' % ('PLAY', flipPath))
# hou.hscript('set -g "%s"="%s"' % ('WRANGLE', vexPath))
# hou.hscript('set -g "%s"="%s"' % ('PERFORCE', perforce))
# hou.hscript('set -g "%s"="%s"' % ('MRENDER', renderPath))
# hou.hscript('set -g "%s"="%s"' % ('LS', lightSetup))
# hou.hscript('set -g "%s"="%s"' % ('REFPATH', refPath))

# hou.hscript('unitlength 0.1')

# import workCal
# reload(workCal)
# workCal.writeVisit( scenes = 1 )
# '''
# if not os.path.exists( "%s/sceneDump.json" % MDataPath ) and seq != '' :
#     if os.path.exists( perforce ) :
#         import maya_import
#         reload( maya_import )
#         hou.session.x = maya_import.maya_scene(fromnode = False)
#         hou.session.x.open()
# '''