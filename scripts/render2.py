import hou, sys
import time
import threading
from PySide2.QtCore import *
from PySide2.QtWidgets import *

class thread_render(QThread) :

    update = Signal(float)
    
    def __init__(self, rop, f, parent = None):
        super(thread_render, self).__init__(parent)
        self.rop = rop
        self.f = f
        
    def run(self):
        fr = list(self.f)
        fr[1] += 1
        for i in range(*fr):
            self.rop.render(frame_range = (i,i, fr[2]), verbose = True, output_progress = True)
            self.update.emit(time.time())

class my_render(QObject):
    def __init__(self, rop, f, parent=None):
        super(my_render, self).__init__(parent)
        self.rop = rop
        self.fr = f
        self.prev_time = time.time()
        self.rnd = thread_render( rop, self.fr )
        self.rnd.finished.connect(self.stopProcess)
        self.rnd.update.connect(self.checkUpdate)
        print '\n========================= Start process ======================================\n'
        self.rnd.start()

    def stopProcess(self):
        exit()
        print "Stop process natural"

    def checkUpdate(self, t):
        diff = t - self.prev_time 
        self.prev_time = t
        print "Frame rendered in {}".format(diff)
        if diff > 7 :
            print "Break process force"
            self.rnd.terminate()

class ClockThread(threading.Thread):
    def __init__(self, hip, node, fr):
        threading.Thread.__init__(self)
        self.hip = hip
        self,node = node
        self.fr = fr
        self.rop = self.loadScene()
        self.prevFrame = None

    def loadScene(self):
        print "Load scene {}".format(hip)
        hou.hipFile.load(hip)
        print "Scene loaded successfully"
        hippath = '/'.join(hip.split('\\')[:-1])
        hipname = hip.split('\\')[-1].replace('.hip', '')
        hou.hscript('set -g HIP={}'.format(hippath))
        hou.hscript('set -g HIPNAME={}'.format(hipname))
        hou.hscript('set -g HIPFILE={}/{}.hip'.format(hip, hipname))
        rop = hou.node(node)
        try:
            rop.parm('vm_verbose').set(4)
            rop.parm("vm_vexprofile").set(1)
            rop.parm("vm_alfprogress").set(1)

        except(AttributeError):
            try:
                rop.parm("alfprogress").set(1)
            except(AttributeError):
                pass

        return rop

    def run(self):
        fr = list(self.fr)
        fr[1] += 1
        print 'Start rendering process'
        # for i in range(*fr):
        #     self.prevFrame = time.time()
        #     self.rop.render(frame_range = (i,i,fr[2]), verbose = True, output_progress = True)
        self.rop.render(frame_range = (self.fr), verbose = True, output_progress = True)
        exit()
        print 'Normal exit!'

def checkState(thr):
    t = time.time()
    diff = t - prev_time
    if diff > 7:
        print "Force exit!"
        sys.exit()
    else:
        prev_time = t

try:
    hip =  sys.argv[1]
    node = sys.argv[2]
    f = (int(sys.argv[3]),
         int(sys.argv[4]),
         int(sys.argv[5]))

    print "Load scene..."
    hou.hipFile.load(hip)
    hippath = '/'.join(hip.split('\\')[:-1])
    hipname = hip.split('\\')[-1].replace('.hip', '')
    hou.hscript('set -g HIP={}'.format(hippath))
    hou.hscript('set -g HIPNAME={}'.format(hipname))
    hou.hscript('set -g HIPFILE={}/{}.hip'.format(hip, hipname))
    rop = hou.node(node)
    try:
        rop.parm('vm_verbose').set(4)
        rop.parm("vm_vexprofile").set(1)
        rop.parm("vm_alfprogress").set(1)

    except(AttributeError):
        try:
            rop.parm("alfprogress").set(1)
        except(AttributeError):
            pass

    print "Prepare render process"
    #app = QApplication.instance()

    #rnd = my_render(rop, f)
    rnd = ClockThread(rop, f)
    rnd.start()
    #sys.exit(app.exec_())
#     exit()

except(IndexError):
    print 'Bad args:'
    for arg in sys.argv:
        print arg