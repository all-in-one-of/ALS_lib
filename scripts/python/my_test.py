import time
import os, sys
import shutil

def test():
	count = 0
	path = r'\\PROJECTS\Alisa_Film\HoudiniProject\Jobs\Main\scenes'
	for d, dirs, files in os.walk( path ) :
		if d.split('\\')[-1] == 'backup' :
			print d
			shutil.rmtree(d)
			# count += 1

if __name__ == '__main__':
	test()

    # grabovskiy::my_srcNode::1.0.3