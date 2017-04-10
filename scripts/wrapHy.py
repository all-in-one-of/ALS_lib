from startFilm16 import *

file = None
try :
    file = sys.argv[1]
except :
    file = ''

if __name__ == '__main__':       
    startpath = ('\"%s/hython\" %s' % (HB, file))
    subprocess.call(startpath)