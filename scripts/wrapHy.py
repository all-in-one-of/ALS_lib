from wrapHou import *
try :
    file = sys.argv[2]
except :
    file = ''

if __name__ == '__main__':       
    startpath = ('\"%s/hython\" %s' % (HB, file))
    subprocess.call(startpath)