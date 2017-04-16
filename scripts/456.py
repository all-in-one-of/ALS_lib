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
HIP = hou.expandString('$HIP')
HIPNAME = hou.expandString('$HIPNAME')
#rop cmd fix
if not HOUDINI_GLOB_PATH in HIP:
	try:
		HIP = '/'.join(sys.argv[1].split('\\')[:-1])
		HIPNAME = sys.argv[1].split('\\')[-1].replace('.hip', '')
	except(IndexError):
		print 'HIP variables are breaked!'
		pass

jobPat = re.compile('\/Jobs/(?P<job>[^\/]+)')
seqShPat = re.compile('(?P<seq>seq\d+)_(?P<sh>sh\d+)(?=_(?P<sub>sub\d+)|\/*|\/*)')
jobSearch = jobPat.search(HIP)
shotInfo = seqShPat.search(HIP)
try:
	job = jobSearch.group('job')
except(AttributeError):
	job = 'Main'

#------------- init variables -----------------
globs = {'JOB' : '{0}/Jobs/{1}'.format(HOUDINI_GLOB_PATH, job),
		'MJOB' : HOUDINI_GLOB_PATH.replace('HoudiniProject', 'MayaProject'),
		'ALS' : '{}/Libraries/ALS_lib'.format(HOUDINI_GLOB_PATH)}

		       
if shotInfo != None :
	globs['SEQ'] = shotInfo.group('seq')
	globs['SH'] = shotInfo.group('sh')
	globs['SUB'] = shotInfo.group('sub')

	if globs['SEQ'] != None:
		shotDir = '{0}/{0}_{1}'.format(globs['SEQ'], globs['SH'])
		if globs['SUB'] != None:
			shotDir += '_{}'.format(globs['SUB'])

		globs['RCPATH'] = '{0}/{1}'.format(RENDER_COMPOSE, shotDir)

		globs['HDATA'] = '{0}/data/{1}'.format(globs['JOB'], shotDir)
		globs['HDATA_GLOB'] = globs['HDATA']
		globs['DATA_STORE'] = '{0}/data_store/{1}/{2}'.format(HOUDINI_GLOB_PATH, job, shotDir)
		
		if userInfo.user != 'default':
			globs['HDATA'] = globs['HDATA'].replace(HOUDINI_GLOB_PATH, 'Q:/houdini')

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
		globs['_EXPORT'] = '{0}/_Export/{1}'.format(globs['JOB'], shotDir)
else:
	globs['HDATA'] = '{0}/data'.format(HIP)
	globs['MDATA'] = '{0}/geo'.format(HIP)
	globs['PLAY'] = '{0}/flipbook'.format(HIP)
	globs['WRANGLE'] = '{0}/vex_wrangles'.format(HIP)
	globs['PROXY'] = '{0}/proxy'.format(HIP)
	globs['MCACHE'] = '{0}/alembic'.format(HIP)
	globs['RCPATH'] = '{0}/render'.format(HIP)
	globs['REFPATH'] = '{0}/references'.format(HIP)
	globs['_EXPORT'] = '{0}/_Export'.format(HIP)

	#rop cmd fix
	globs['HIP'] = HIP
	globs['HIPNAME'] = HIPNAME
	globs['HIPFILE'] = '{}/{}'.format(HIP, HIPNAME)

# -------------- set houdini vaiables --------------
for key, val in globs.iteritems():
	hou.hscript('set -g {0}={1}'.format(key, val))

hou.hscript('unitlength 0.1')

import workCal
reload(workCal)
workCal.writeVisit(scenes=1)