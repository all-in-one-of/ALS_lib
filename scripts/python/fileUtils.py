import os
import sys
import errno

def createDir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def cleanEmptyDirs(root):
	for d, dirs, files in os.walk( root ):
		if not files and not dirs:
			print 'remove {}'.format(d)
			os.rmdir(d)
		else:
			print '    not empty dir {}'.format(d)

if __name__ == '__main__':
	pass
	test = 'D:/HoudiniProject'
	cleanEmptyDirs(test)
	