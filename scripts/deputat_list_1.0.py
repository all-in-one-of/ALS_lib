import hou
import os
import subprocess

# print 'ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
cmd = hou.pwd().parm('cmd').eval()
alfred = '//PROJECTS/Alisa_Film/HoudiniProject/Jobs/Research/deputat_tests/alf/test.alf'
# print 'unix {0} "{1}"'.format(cmd, alfred)
# hou.hscript('unix {0} "{1}"\npause'.format(cmd, alfred))
subprocess.Popen('{0} "{1}"'.format(cmd, alfred))

if __name__ == '__main__':
	print 'Deputat!'