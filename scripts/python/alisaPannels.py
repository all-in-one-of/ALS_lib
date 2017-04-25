from hutil.Qt.QtCore import *
from hutil.Qt.QtUiTools import *
from hutil.Qt.QtWidgets import *

import hou
import toolutils
import itertools
import subprocess
import os
import socket
import datetime
import subprocess
import re

import hqt
import dataCleaner2
import fileUtils

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
P4 = "C:/Program Files/Perforce/p4"
PYTHON = "C:/Python27_64/python.exe"
UPDATEASSETS = "//PROJECTS/Alisa_Film/HoudiniProject/scripts/p4update.py"
SYNC = "C:/Program Files/FreeFileSync/FreeFileSync.exe"
SYNC_BATCH = "//PROJECTS/Alisa_Film/HoudiniProject/data_sinc.ffs_batch"
SYNC_GUI = "//PROJECTS/Alisa_Film/HoudiniProject/data_sinc.ffs_gui"
LOCAL = 'Q:/Houdini'

def createPath(path) :
    current = []
    for num, part in enumerate(path.split('/')) :
        current.append(part)
        pathString = "/".join(current)
        if not os.path.exists(pathString) :
            try :
                os.mkdir(pathString)
            except :
                pass

class XXX(QWidget):
    def __init__(self, parent = None):
        super(XXX, self).__init__(parent)
        h = QHBoxLayout(self)
        ui_file_path = "{0}/scripts/widgets/projectBrowser.ui".format(hou.expandString('$ALS'))
        loader = QUiLoader()
        self.widget = loader.load(ui_file_path)
        self.widget.jobButton.clicked.connect(self.yyy)
        h.addWidget(self.widget)
        #jobButton = widget.findChild(QPushButton, 'jobButton')
        #jobButton.clicked.connect(self.yyy)

    def yyy(self):
        print 456

class projectBrowser (QWidget) :
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ui_file_path = "{0}/scripts/widgets/projectBrowser.ui".format(hou.expandString('$ALS'))
        loader = QUiLoader()
        self.widget = loader.load(ui_file_path)

        self.widget.jobField.setText(hou.expandString('$JOB'))
        self.widget.mjobField.setText(hou.expandString('$MJOB'))
        self.widget.hdataField.setText(hou.expandString('$HDATA'))
        self.widget.mcacheField.setText(hou.expandString('$MCACHE'))
        self.widget.mdataField.setText(hou.expandString('$MDATA'))
        self.widget.mscenesField.setText(hou.expandString('$MSCENES'))
        self.widget.flipField.setText(hou.expandString('$PLAY'))
        self.widget.rcField.setText(hou.expandString('$RCPATH'))
        self.widget.refField.setText(hou.expandString('$REFPATH'))

        self.widget.jobButton.clicked.connect(self._projDir)
        self.widget.mjobButton.clicked.connect(self._mprojDir)
        self.widget.hdataButton.clicked.connect(self._dataDir)
        self.widget.mdataButton.clicked.connect(self._mDataDir)
        self.widget.mcacheButton.clicked.connect(self._mCacheDir)
        self.widget.mscenesButton.clicked.connect(self._mScenesDir)
        self.widget.flipButton.clicked.connect(self._flipDir)
        self.widget.rcButton.clicked.connect(self._rcpathDir)
        self.widget.refButton.clicked.connect(self._referenceDir)
        self.widget.localDataButton.clicked.connect(self._dataLocalDir)
        self.widget.storageButton.clicked.connect(self._dataStorageDir)
        self.widget.sceneButton.clicked.connect(self._openScene)

        h = QHBoxLayout(self)
        h.setContentsMargins(0,0,0,0)
        h.addWidget(self.widget)
        self.widget.setStyleSheet(hqt.get_h14_style())

    def test( self ):
        print self.widget.jobButton.clicked.connect(self._projDir)

    def openPath(self, field, var, create_dir=False):
        field.setText(hou.expandString(var))
        path = field.text().replace('/', '\\')
        if create_dir:
            fileUtils.createDir(path)
        os.startfile(path)
        
    def _projDir(self) :
        self.openPath(self.widget.jobField, '$JOB')
    def _mprojDir(self) :
        self.openPath(self.widget.mjobField, '$MJOB')
    def _dataDir(self) :
        self.openPath(self.widget.hdataField, '$HDATA_GLOB', True)
    def _mDataDir(self) :
        self.openPath(self.widget.mdataField, '$MDATA', True)
    def _mCacheDir(self) :
        self.openPath(self.widget.mcacheField, '$MCACHE', True)
    def _mScenesDir(self) :
        self.openPath(self.widget.mscenesField, '$MSCENES')
    def _flipDir(self) :
        self.openPath(self.widget.flipField, '$PLAY', True)
    def _rcpathDir(self) :
        self.openPath(self.widget.rcField, '$RCPATH', True)
    def _referenceDir(self) :
        self.openPath(self.widget.refField, '$REFPATH', True)

    # non standart functions
        
    def _dataLocalDir(self) :
        self.widget.hdataField.setText(hou.expandString('$HDATA_GLOB'))
        path = self.widget.hdataField.text().replace(self.widget.jobField.text(), LOCAL).replace('/', '\\')
        os.startfile(path)
        
    def _dataStorageDir(self) :
        self.widget.hdataField.setText(hou.expandString('$HDATA_GLOB'))
        path = hou.expandString('$DATA_STORE').replace('/', '\\')
        fileUtils.createDir(path)
        os.startfile(path)
        
    def _openScene(self) :
        bat = hou.expandString('$ALS') + '/scripts/maya2016-x64_open_scene.cmd'
        scene = hou.expandString('$PERFORCE')
        path = hou.hipFile.path()
        curSeq = '%s_%s' % (hou.hscriptExpression('$SEQ'), hou.hscriptExpression('$SH'))
        if not curSeq in path or curSeq == '_' :
            hou.ui.displayMessage('Environment does not match to scene path!\nTry agayn when reload be completed.')
            userfuncs.reloadScene()
            return
        print "[ %s ] Synchronize assets in perforce..." % datetime.datetime.now().strftime('%H:%M:%S')
        assetsCmd = "%s %s" % (PYTHON, UPDATEASSETS)
        assets = subprocess.Popen([ 'p4', 'sync', '-q', 'Q:/Film/Assets/...' ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        assets.wait()
        sync = assets.communicate()
        print sync[0]

        print "[ %s ] Synchronize scene in perforce..." % datetime.datetime.now().strftime('%H:%M:%S')        
        p4sync = subprocess.Popen([ 'p4', 'sync', '-q', scene ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        p4sync.wait()
        sync = p4sync.communicate()
        print sync[0]
        
        p4stat = subprocess.Popen([ 'p4', 'fstat', '-q', scene ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        p4stat.wait()
        fstat = p4stat.communicate()
        print fstat[0]
        fstatArray = [ i.replace('... ', '').replace('\r', '') for i in fstat[0].split('\n') ]
        fstatDict = dict((i.split(' ')[0], i.split(' ')[-1]) for i in fstatArray)
        otherOpen = fstatDict.has_key('otherOpen')
        
        doexport = 1
        
        if otherOpen :
            doexport = hou.ui.displayMessage("Scene locked by %s?\n Are you sure want to open it?" % fstatDict[ 'otherOpen0' ], buttons=('OK', 'Cancel'))
            if doexport :
                return
        else :
            doexport = 0

        if doexport == 0 :
            print "[ %s ] Start scene %s..." % (datetime.datetime.now().strftime('%H:%M:%S'), scene)
            rem = ['PYTHONHOME', 'HOME', 'PYTHONPATH']
            env = {k:v for k, v in os.environ.items() if not k in rem and not 'HOUDINI' in k}
            cmd = '%s %s' % (bat.replace('/', '\\'), scene)
            maya = subprocess.Popen(cmd, env = env)
        
class flipbook(QWidget) :
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ui_file_path = "{0}/scripts/widgets/flipbook.ui".format(hou.expandString('$ALS'))
        loader = QUiLoader()
        self.widget = loader.load(ui_file_path)

        self.job  = hou.expandString('$JOB')
        self.play = hou.expandString('$PLAY')
        self.seq  = hou.expandString('$SEQ')
        self.sh   = hou.expandString('$SH')
        self.width = 2048
        self.height = 858
        self.replace = 0

        h = QHBoxLayout(self)
        h.setContentsMargins(0,0,0,0)
        h.addWidget(self.widget)
        self.widget.setStyleSheet(hqt.get_h14_style())

        # icon = QIcon()
        # icon.addPixmap(QPixmap("file.png"))
        # self.widget.getDirBtn.setIcon(icon)
        self.widget.getDirBtn.clicked.connect(self._getFlipPath)
        self.widget.flipbookButton.clicked.connect(self._flipWrite)

    def existsCheck(self, path) :
        if os.path.exists(path) and self.replace == 0 :
            question =  hou.ui.displayMessage('%s already exists.\n Do you whant to replace it?' % path, buttons = ('Ok', 'Cancel'))
            if question :
                return False
            self.replace = 1
        pathExp = path.replace('\\', '/')
        if not '$PLAY' in pathExp :
            pathExp = pathExp.replace(self.play, '$PLAY')
        pathExp = pathExp.replace(self.job, '$JOB')
        ext = pathExp.split('/')[-1]
        mode = 'img' if 'jpg' in ext or 'png' in ext else 'mov'
        if mode == 'img' :
            frameExp = re.search('\.\d+\.[a-z]+$', pathExp)
            if frameExp :
                frameGrp = frameExp.group().split(".")[-2]
                padding = len(frameGrp)
                pathExp = pathExp.replace('.%s.' % frameGrp, '.$F%s.' % padding)
        self.widget.pathField.setText(pathExp)
        return True

    def _getFlipPath(self) :
        startDir = hou.expandString(self.widget.pathField.text())
        fname = QFileDialog.getSaveFileName(self, "Save Flipbook", dir=startDir, filter="(*.mov *.mp4 *.jpg *.png)")
        if fname[0] :
            self.existsCheck(fname[0]) 

        
    def viewname(self, viewer) :
        viewname = {
            'desktop' : viewer.pane().desktop().name(),
            'pane' : viewer.name(),
            'type' :'world',
            'viewport': viewer.curViewport().name()
        }
        return '{desktop}.{pane}.{type}.{viewport}'.format(**viewname)

    def viewwrite(self, options='', outpath='ip'):
        current_view = self.viewname(toolutils.sceneViewer())
        pane = current_view.split('.')[1]
        hou.hscript('pane -f 1 %s' % pane)
        go = hou.ui.displayMessage('Viewport ready?')
        if not go :
            hou.hscript('viewwrite {} {} {}'.format(options, current_view, outpath))
            #print 'viewwrite {} {} {}'.format(options, current_view, outpath)
        hou.hscript('pane -f 0 %s' % pane)
        
    def _flipWrite(self) :
        path = self.widget.pathField.text()
        expandPath = hou.expandString(self.widget.pathField.text())
        check = self.existsCheck(expandPath)
        if not check :
            return
        lst = path.split('/')
        dir = hou.expandString('/'.join(lst[:-1]))
        name = lst[-1]

        if not name.split('.')[-1] in ['jpg', 'png', 'mp4', 'mov'] :
            name += '.mov'
        path = dir + '/' + name
            
        ext  =  name.split('.')[-1]
        baseName = name.split('.' + ext)[0]
        print baseName
        qual  = int(float(hou.expandString(self.widget.antialiasSpinBox.text())))
        start = int(float(hou.expandString(self.widget.startField.text())))
        end   = int(float(hou.expandString(self.widget.endField.text())))
        gamma = float(hou.expandString(self.widget.gammaSpinBox.text()))
        start = max(1, start)
        
        if self.widget.dirToggle.checkState() == Qt.CheckState.Checked :
            createPath(dir)
            
        if not ext in [ 'jpg', 'png' ] :
            tmp = dir + '/%s_tmp' % socket.gethostname()
            createPath(tmp)
            ffmpeg = '{0}/ffmpeg/bin/ffmpeg.exe'.format(HOUDINI_GLOB_PATH)
            fps = hou.expandString('$FPS')
            
            self.viewwrite('-q {0} -f {1} {2} -r {4} {5} -g {3} -c'.format(qual, start, end, gamma, self.width, self.height), "%s/'$F4'.jpg"%tmp)
            
            cmd = '{0} -framerate {3} -start_number {1} -i {2} -r {3} -vcodec libx264 {4}'.format(ffmpeg, start, tmp + r'/%04d.jpg', fps, path).replace('/', '\\')
            print cmd
            movie = subprocess.Popen(cmd)
            movie.wait()
            
            for file in os.listdir(tmp) :
                os.remove('%s/%s' % (tmp, file))
            os.rmdir(tmp)
            
        else :
            #pass
            self.viewwrite('-q {0} -f {1} {2} -r {4} {5} -g {3} -c'.format(qual, start, end, gamma, self.width, self.height),\
                           "{}/{}.{}".format(dir, baseName.replace('$F4', "'$F4'"), ext))
        
        cmd = 'explorer /select,{}'.format(path.replace('/', '\\').replace('$F4', ('%s'%start).zfill(4)))
        subprocess.Popen(cmd)
        self.replace = 0


class dataCleaner(QWidget) :
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ui_file_path = "{0}/scripts/widgets/datasync.ui".format(hou.expandString('$ALS'))
        loader = QUiLoader()

        self.widget = loader.load(ui_file_path)
        h = QHBoxLayout(self)
        h.setContentsMargins(0,0,0,0)
        h.addWidget(self.widget)
        self.widget.setStyleSheet(hqt.get_h14_style())

        self.job = hou.expandString('$JOB')

        self.widget.getDirBtn.clicked.connect(self._getScenesPath)
        self.widget.startRepareBtn.clicked.connect(self._runRepare)
        self.widget.startCleanBtn.clicked.connect(self._runCleaner)
        self.widget.syncButton.clicked.connect(self._runButchSync)
        self.widget.syncGuiButton.clicked.connect(self._runGuiSync)

    def _getScenesPath(self) :
        startDir = hou.expandString(self.widget.scenesField.text())
        fname = QFileDialog.getExistingDirectory(dir = startDir)
        if fname :
            self.scenesField.setText(fname.replace('\\', '/').replace(self.job, '$JOB'))

    def _runRepare(self) :
        reload(dataCleaner2)
        dataCleaner2.repare()

    def _runCleaner(self) :
        reload(dataCleaner2)
        scenes = hou.expandString(self.widget.scenesField.text())
        mask   = self.widget.maskField.text()
        dataCleaner2.analize(scenes, mask)

    def _runButchSync(self) :
        subprocess.Popen(('"%s" "%s"' % (SYNC, SYNC_BATCH)).replace('/', '\\'))
        print 'Batch sync process initialized!'

    def _runGuiSync(self) :
        subprocess.Popen(('"%s" "%s"' % (SYNC, SYNC_GUI)).replace('/', '\\'))