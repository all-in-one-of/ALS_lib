import hou
import sys
import os # platform
import re

import userInfo
import fileUtils

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
LOCAL_DATA_PATH = 'Q:/houdini'
LOCAL_MAYA_SCENES = 'Q:/Film/Scenes'
RENDER_COMPOSE = '//POST/film/RenderCompose'

#
seqShPat = re.compile('\/(?P<job>[^\/]*)\/[^\/]+\/seq\d+\/(?P<seq>seq\d+)_(?P<sh>sh\d+)(?=_(?P<sub>sub\d+)|\/*|\/*)')
#parse hip path
hipPath = hou.hipFile.path()
shotInfo = seqShPat.search(hipPath)


# #------------- init variables -----------------
glob = {'JOB' : '{0}/{1}'.format(HOUDINI_GLOB_PATH, shotInfo.group('job')) if shotInfo else '{}/Main'.format(HOUDINI_GLOB_PATH),
		'MJOB' : HOUDINI_GLOB_PATH.replace('HoudiniProject', 'MayaProject'),} #maya project path
		       
if shotInfo:
	glob['SEQ'] = shotInfo.group('seq')
	glob['SH'] = shotInfo.group('sh')
	glob['SUB'] = shotInfo.group('sub')

	if glob['SEQ'] != '' and SH != '':
		shotDir = '{0}/{0}_{1}'.format(glob['SEQ'], glob['SH'])
		if SUB != '':
			shotDir += '_{}'.format(glob['SUB'])

		glob['RCPATH'] = '{0}/{1}'.format(RENDER_COMPOSE, shotDir)

		glob['HDATA'] = '{0}/data/{1}'.format(glob['JOB'], shotDir)
		glob['HDATA_GLOB'] = glob['HDATA']
		glob['DATA_STORE'] = '{0}/data_store/{1}/{2}'.format(HOUDINI_GLOB_PATH, shotInfo.group('job'), shotDir)
		if userInfo.user != 'default':
			glob['HDATA'] = glob['HDATA'].replace(HOUDINI_GLOB_PATH, 'Q:/houdini')

		glob['MDATA'] = '{0}/_Export'.format(glob['RCPATH'])
		glob['MCACHE'] = '{0}/cache/alembic/{1}'.format(glob['MJOB'], shotDir)
		glob['MSCENES'] = '{0}/{1}'.format(LOCAL_MAYA_SCENES, glob['SEQ'])

		glob['PLAY'] = '{0}/flipbook/{1}'.format(glob['JOB'], shotDir)
		glob['PERFORCE'] = '{0}/{1}.ma'.format(LOCAL_MAYA_SCENES, shotDir)
		glob['WRANGLE'] = '{0}/vex_wrangles/{1}'.format(glob['JOB'], shotDir)
		glob['PROXY'] = '{0}/proxy/{1}'.format(glob['JOB'], shotDir)
		glob['MRENDER'] = '{0}/OppositeLayer/MasterBeauty'.format(glob['RCPATH'])
		glob['LS'] = '{0}/RND_files/render_{1}_master/LS'.format(glob['MJOB'], glob['SEQ'])
		glob['REFPATH'] = '{0}/references/{1}'.format(glob['JOB'], shotDir)
else:
	hip = hou.expandString('$HIP')
	glob['HDATA'] = '{0}/data'.format(hip)
	glob['PLAY'] = '{0}/flipbook'.format(hip)
	glob['WRANGLE'] = '{0}/vex_wrangles'.format(hip)
	glob['PROXY'] = '{0}/proxy'.format(hip)
	glob['MCACHE'] = '{0}/alembic'.format(hip)

# #-------------- set houdini vaiables --------------
for key, val in glob.iteritems():
	hou.hscript('set -g {0}={1}'.format(key, val))

hou.hscript('unitlength 0.1')

import workCal
reload(workCal)
workCal.writeVisit(scenes=1)