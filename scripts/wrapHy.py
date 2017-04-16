from wrapHou import *
import sys
kwargs = {'HB' :HB}
try:
    kwargs['file'] = sys.argv[2]
except(IndexError):
    kwargs['file'] = ''

try:
    kwargs['hip'] =  sys.argv[3]
    kwargs['node'] = sys.argv[4]
    kwargs['f1'] = sys.argv[5]
    kwargs['f2'] = sys.argv[6]
    kwargs['f3'] = sys.argv[7]
except(IndexError):
    kwargs['hip'] = ''
    kwargs['node'] = ''
    kwargs['f1'] = ''
    kwargs['f2'] = ''
    kwargs['f3'] = ''

if __name__ == '__main__':       
    startpath = '\"{HB}/hython.exe\" "{file}" "{hip}" "{node}" {f1} {f2} {f3}'.format(**kwargs)
    subprocess.call(startpath)