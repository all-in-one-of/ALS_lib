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
globs = {'JOB' : '{0}/Jobs/{1}'.format(HOUDINI_GLOB_PATH, shotInfo.group('job')) if shotInfo else '{}/Jobs/Main'.format(HOUDINI_GLOB_PATH),
		'MJOB' : HOUDINI_GLOB_PATH.replace('HoudiniProject', 'MayaProject'), #maya project path
		'ALS' : '{}/ALS_lib'.format(HOUDINI_GLOB_PATH)}
		       
if shotInfo:
	globs['SEQ'] = shotInfo.group('seq')
	globs['SH'] = shotInfo.group('sh')
	globs['SUB'] = shotInfo.group('sub')

	if globs['SEQ'] != '' and SH != '':
		shotDir = '{0}/{0}_{1}'.format(globs['SEQ'], globs['SH'])
		if SUB != '':
			shotDir += '_{}'.format(globs['SUB'])

		globs['RCPATH'] = '{0}/{1}'.format(RENDER_COMPOSE, shotDir)

		globs['HDATA'] = '{0}/data/{1}'.format(globs['JOB'], shotDir)
		globs['HDATA_globs'] = globs['HDATA']
		globs['DATA_STORE'] = '{0}/data_store/{1}/{2}'.format(HOUDINI_globs_PATH, shotInfo.group('job'), shotDir)
		if userInfo.user != 'default':
			globs['HDATA'] = globs['HDATA'].replace(HOUDINI_globs_PATH, 'Q:/houdini')

		globs['MDATA'] = '{0}/_Export'.format(globs['RCPATH'])
		globs['MCACHE'] = '{0}/cache/alembic/{1}'.format(globs['MJOB'], shotDir)
		globs['MSCENES'] = '{0}/{1}'.format(LOCAL_MAYA_SCENES, globs['SEQ'])

		globs['PLAY'] = '{0}/flipbook/{1}'.format(globs['JOB'], shotDir)
		globs['PERFORCE'] = '{0}/{1}.ma'.format(LOCAL_MAYA_SCENES, shotDir)
		globs['WRANGLE'] = '{0}/vex_wrangles/{1}'.format(globs['JOB'], shotDir)
		globs['PROXY'] = '{0}/proxy/{1}'.format(globs['JOB'], shotDir)
		globs['MRENDER'] = '{0}/OppositeLayer/MasterBeauty'.format(globs['RCPATH'])
		globs['LS'] = '{0}/RND_files/render_{1}_master/LS'.format(globs['MJOB'], globs['SEQ'])
		globs['REFPATH'] = '{0}/references/{1}'.format(globs['JOB'], shotDir)
else:
	hip = hou.expandString('$HIP')
	globs['HDATA'] = '{0}/data'.format(hip)
	globs['PLAY'] = '{0}/flipbook'.format(hip)
	globs['WRANGLE'] = '{0}/vex_wrangles'.format(hip)
	globs['PROXY'] = '{0}/proxy'.format(hip)
	globs['MCACHE'] = '{0}/alembic'.format(hip)

# #-------------- set houdini vaiables --------------
for key, val in globs.iteritems():
	hou.hscript('set -g {0}={1}'.format(key, val))

hou.hscript('unitlength 0.1')

import workCal
reload(workCal)
workCal.writeVisit(scenes=1)