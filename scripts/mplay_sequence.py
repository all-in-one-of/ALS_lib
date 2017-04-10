import sys
import subprocess
import re

def mplay(path):
    cmd = ''
    folder = '\\'.join(path.split('\\')[0:-1])
    file = path.split('\\')[-1]
    x = re.compile('(?P<base>[^\/]+)\.((?P<fexp>\$F\d)|(?P<num>\d+))\.(?P<ext>\w+)')
    fInfo = x.search(file)
    if fInfo :
        base = fInfo.group('base')
        num  = fInfo.group('num')
        fexp = fInfo.group('fexp')
        ext  = fInfo.group('ext')
        frameExp = fexp if fexp else "$F%d"%len(num)
        pathexp = '{0}\\{1}.{2}.{3}'.format(folder, base, frameExp, ext)
        cmd = 'mplay "{0}"'.format(pathexp)
        subprocess.Popen(cmd)
        print cmd
    else:
        print 'Bad file path {0}'.format(path)

if __name__ == '__main__':
    try :
        path = sys.argv[1].replace("/", "\\")        
    except IndexError :
        path = ''
        # path = r'\\POST\film\RenderCompose\seq011\seq011_sh008\OppositeLayer\MasterBeauty\OL_MasterBeauty.0019.exr'

    mplay(path)