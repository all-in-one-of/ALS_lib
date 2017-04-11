try :
    from PySide.QtGui import *
    from PySide.QtCore import *
except :
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

import hou
import toolutils
import subprocess
import os
import socket
import datetime
import subprocess
import re

import dataCleaner2
import fileUtils

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
P4 = "C:/Program Files/Perforce/p4"
PYTHON = "C:/Python27_64/python.exe"
UPDATEASSETS = "//PROJECTS/Alisa_Film/HoudiniProject/scripts/p4update.py"
SYNC = "C:/Program Files/FreeFileSync/FreeFileSync.exe"
SYNC_BATCH = "//PROJECTS/Alisa_Film/HoudiniProject/data_sinc.ffs_batch"
SYNC_GUI = "//PROJECTS/Alisa_Film/HoudiniProject/data_sinc.ffs_gui"
LOCAL = 'Q:/houdini'

def createPath( path ) :
    current = []
    for num, part in enumerate( path.split('/') ) :
        current.append(part)
        pathString = "/".join(current)
        if not os.path.exists( pathString ) :
            try :
                os.mkdir( pathString )
            except :
                pass

class projectBrowser (QWidget) :
    def __init__(self) :
        QWidget.__init__( self )
        
        #============fields==============
        self.projField = QLineEdit()
        self.projField.setText( hou.expandString( '$JOB' ) )
        
        self.mProjField = QLineEdit()
        self.mProjField.setText( hou.expandString( '$MJOB' ) )
        
        self.hdataField = QLineEdit()
        self.hdataField.setText( hou.expandString( '$HDATA' ) )
        
        self.mCacheField = QLineEdit()
        self.mCacheField.setText( hou.expandString( '$MCACHE' ) )
        
        self.mDataField = QLineEdit()
        self.mDataField.setText( hou.expandString( '$MDATA' ) )
        
        self.mScenesField = QLineEdit()
        self.mScenesField.setText( hou.expandString( '$MSCENES' ) )
        
        self.flipField = QLineEdit()
        self.flipField.setText( hou.expandString( '$PLAY' ) )
        
        self.wrangleField = QLineEdit()
        self.wrangleField.setText( hou.expandString( '$WRANGLE' ) )
        
        self.rcpathField = QLineEdit()
        self.rcpathField.setText( hou.expandString( '$RCPATH' ) )
        
        self.referenceField = QLineEdit()
        self.referenceField.setText( hou.expandString( '$REFPATH' ) )
        
        
        #============buttons=============
        pojButton = QToolButton( self )
        pojButton.clicked.connect( self._projDir )
        pojButton.setText("Houdini JOB")
        pojButton.setFixedSize(QSize(120, 25))
        pojButton.setFocusPolicy(Qt.NoFocus)
        
        mProjButton = QToolButton( self )
        mProjButton.clicked.connect( self._mprojDir )
        mProjButton.setText("Maya JOB")
        mProjButton.setFixedSize(QSize(120, 25))
        mProjButton.setFocusPolicy(Qt.NoFocus)
        
        HDataButton = QToolButton( self )
        HDataButton.clicked.connect( self._dataDir )
        HDataButton.setText("Houdini Data")
        HDataButton.setFixedSize(QSize(120, 25))
        HDataButton.setFocusPolicy(Qt.NoFocus)
        
        HDataLocalButton = QToolButton( self )
        HDataLocalButton.clicked.connect( self._dataLocalDir )
        HDataLocalButton.setText("Local")
        HDataLocalButton.setFixedSize(QSize(60, 25))
        HDataLocalButton.setFocusPolicy(Qt.NoFocus)
        
        HDataStorageButton = QToolButton( self )
        HDataStorageButton.clicked.connect( self._dataStorageDir )
        HDataStorageButton.setText("Storage")
        HDataStorageButton.setFixedSize(QSize(80, 25))
        HDataStorageButton.setFocusPolicy(Qt.NoFocus)
        
        MDataButton = QToolButton( self )
        MDataButton.clicked.connect( self._mDataDir )
        MDataButton.setText("Maya Data")
        MDataButton.setFixedSize(QSize(120, 25))
        MDataButton.setFocusPolicy(Qt.NoFocus)
        
        mCacheButton = QToolButton( self )
        mCacheButton.clicked.connect( self._mCacheDir )
        mCacheButton.setText("To Maya Cache")
        mCacheButton.setFixedSize(QSize(120, 25))
        mCacheButton.setFocusPolicy(Qt.NoFocus)
        
        MScenesButton = QToolButton( self )
        MScenesButton.clicked.connect( self._mScenesDir )
        MScenesButton.setText("Maya Scenes")
        MScenesButton.setFixedSize(QSize(120, 25))
        MScenesButton.setFocusPolicy(Qt.NoFocus)
        
        openSneneButton = QToolButton( self )
        openSneneButton.clicked.connect( self._openScene )
        openSneneButton.setText("Open Scene")
        openSneneButton.setFixedSize(QSize(100, 25))
        openSneneButton.setFocusPolicy(Qt.NoFocus)
        
        flipButton = QToolButton( self )
        flipButton.clicked.connect( self._flipDir )
        flipButton.setText("Flipbooks")
        flipButton.setFixedSize(QSize(120, 25))
        flipButton.setFocusPolicy(Qt.NoFocus)
        
        wrangleButton = QToolButton( self )
        wrangleButton.clicked.connect( self._wrangleDir )
        wrangleButton.setText("Saved Wrangles")
        wrangleButton.setFixedSize(QSize(120, 25))
        wrangleButton.setFocusPolicy(Qt.NoFocus)
        
        rcpathButton = QToolButton( self )
        rcpathButton.clicked.connect( self._rcpathDir )
        rcpathButton.setText("Render Compose")
        rcpathButton.setFixedSize(QSize(120, 25))
        rcpathButton.setFocusPolicy(Qt.NoFocus)
        
        referenceButton = QToolButton( self )
        referenceButton.clicked.connect( self._referenceDir )
        referenceButton.setText("References")
        referenceButton.setFixedSize(QSize(120, 25))
        referenceButton.setFocusPolicy(Qt.NoFocus)
        
        #============layouts=============
        projLayout = QHBoxLayout()
        projLayout.addWidget( pojButton )
        projLayout.addWidget( self.projField )
        
        mProjLayout = QHBoxLayout()
        mProjLayout.addWidget( mProjButton )
        mProjLayout.addWidget( self.mProjField )
        
        hDataLayout = QHBoxLayout()
        hDataLayout.addWidget( HDataButton )
        hDataLayout.addWidget( self.hdataField )
        hDataLayout.addWidget( HDataLocalButton )
        hDataLayout.addWidget( HDataStorageButton )
        
        mDataLayout = QHBoxLayout()
        mDataLayout.addWidget( MDataButton )
        mDataLayout.addWidget( self.mDataField )
        
        mCacheLayout = QHBoxLayout()
        mCacheLayout.addWidget( mCacheButton )
        mCacheLayout.addWidget( self.mCacheField )
        
        MScenesLayout = QHBoxLayout()
        MScenesLayout.addWidget( MScenesButton )
        MScenesLayout.addWidget( self.mScenesField )
        MScenesLayout.addWidget( openSneneButton )
        
        flipLayout = QHBoxLayout()
        flipLayout.addWidget( flipButton )
        flipLayout.addWidget( self.flipField )
        
        wrangleLayout = QHBoxLayout()
        wrangleLayout.addWidget( wrangleButton )
        wrangleLayout.addWidget( self.wrangleField )
        
        rcpathLayout = QHBoxLayout()
        rcpathLayout.addWidget( rcpathButton )
        rcpathLayout.addWidget( self.rcpathField )
        
        referenceLayout = QHBoxLayout()
        referenceLayout.addWidget( referenceButton )
        referenceLayout.addWidget( self.referenceField )
        
        
        #============Master Layout=============
        MasterLayout = QVBoxLayout()
        MasterLayout.addLayout(projLayout)
        MasterLayout.addLayout(mProjLayout)
        MasterLayout.addLayout(hDataLayout)
        MasterLayout.addLayout(mDataLayout)
        MasterLayout.addLayout(mCacheLayout)
        MasterLayout.addLayout(MScenesLayout)
        MasterLayout.addLayout(flipLayout)
        MasterLayout.addLayout(wrangleLayout)
        MasterLayout.addLayout(rcpathLayout)
        MasterLayout.addLayout(referenceLayout)
        MasterLayout.addStretch(1)

        self.setLayout(MasterLayout)
        self.setProperty("houdiniStyle", True)

    def openPath(self, field, var, create_dir=False):
        field.setText( hou.expandString( var ) )
        path = field.text().replace( '/', '\\' )
        if create_dir:
            fileUtils.createDir(path)
        os.startfile( path )
        
    def _projDir( self ) :
        self.openPath(self.projField, '$JOB', create_dir=False)
        
    def _mprojDir( self ) :
        self.openPath(self.mProjField, '$MJOB', create_dir=False)
        
    def _dataDir( self ) :
        self.openPath(self.hdataField, '$HDATA', create_dir=True)
        
    def _mDataDir( self ) :
        self.openPath(self.mDataField, '$MDATA', create_dir=True)
        
    def _mCacheDir( self ) :
        self.openPath(self.mCacheField, '$MCACHE', create_dir=True)
        
    def _mScenesDir( self ) :
        self.openPath(self.mScenesField, '$MSCENES', create_dir=False)
        
    def _flipDir( self ) :
        self.openPath(self.flipField, '$PLAY', create_dir=True)
        
    def _wrangleDir( self ) :
        self.openPath(self.wrangleField, '$WRANGLE', create_dir=True)
        
    def _rcpathDir( self ) :
        self.openPath(self.rcpathField, '$RCPATH', create_dir=True)
        
    def _referenceDir( self ) :
        self.openPath(self.referenceField, '$REFPATH', create_dir=True)

    # non standart functions
        
    def _dataLocalDir( self ) :
        self.hdataField.setText( hou.expandString( '$HDATA' ) )
        path = self.hdataField.text().replace( self.projField.text(), LOCAL ).replace( '/', '\\' )
        os.startfile( path )
        
    def _dataStorageDir( self ) :
        self.hdataField.setText( hou.expandString( '$HDATA' ) )
        path = self.hdataField.text().replace( LOCAL, self.projField.text() ).replace( 'data', 'data_store' ).replace( '/', '\\' )
        os.startfile( path )
        
    def _openScene( self ) :
        bat = hou.expandString( '$ALS' ) + '/scripts/maya2016-x64_open_scene.cmd'
        scene = hou.expandString( '$PERFORCE' )
        path = hou.hipFile.path()
        curSeq = '%s_%s' % ( hou.hscriptExpression( '$SEQ' ), hou.hscriptExpression( '$SH' ) )
        if not curSeq in path or curSeq == '_' :
            hou.ui.displayMessage( 'Environment does not match to scene path!\nTry agayn when reload be completed.' )
            userfuncs.reloadScene()
            return
        print "[ %s ] Synchronize assets in perforce..." % datetime.datetime.now().strftime('%H:%M:%S')
        assetsCmd = "%s %s" % ( PYTHON, UPDATEASSETS )
        assets = subprocess.Popen( [ 'p4', 'sync', '-q', 'Q:/Film/Assets/...' ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        assets.wait()
        sync = assets.communicate()
        print sync[0]

        print "[ %s ] Synchronize scene in perforce..." % datetime.datetime.now().strftime('%H:%M:%S')        
        p4sync = subprocess.Popen( [ 'p4', 'sync', '-q', scene ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        p4sync.wait()
        sync = p4sync.communicate()
        print sync[0]
        
        p4stat = subprocess.Popen( [ 'p4', 'fstat', '-q', scene ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        p4stat.wait()
        fstat = p4stat.communicate()
        print fstat[0]
        fstatArray = [ i.replace('... ', '').replace('\r', '') for i in fstat[0].split('\n') ]
        fstatDict = dict( (i.split(' ')[0], i.split(' ')[-1]) for i in fstatArray )
        otherOpen = fstatDict.has_key('otherOpen')
        
        doexport = 1
        
        if otherOpen :
            doexport = hou.ui.displayMessage( "Scene locked by %s?\n Are you sure want to open it?" % fstatDict[ 'otherOpen0' ], buttons=('OK', 'Cancel') )
            if doexport :
                return
        else :
            doexport = 0

        if doexport == 0 :
            print "[ %s ] Start scene %s..." % ( datetime.datetime.now().strftime('%H:%M:%S'), scene )
            rem = ['PYTHONHOME', 'HOME', 'PYTHONPATH']
            env = {k:v for k, v in os.environ.items() if not k in rem and not 'HOUDINI' in k}
            cmd = '%s %s' % ( bat.replace('/', '\\'), scene )
            maya = subprocess.Popen( cmd, env = env )
        
class flipbook( QWidget ) :
    def __init__(self) :
        QWidget.__init__( self )

        self.job  = hou.expandString( '$JOB' )
        self.play = hou.expandString( '$PLAY' )
        self.seq  = hou.expandString( '$SEQ' )
        self.sh   = hou.expandString( '$SH' )
        self.replace = 0
        
        pathLabel = QLabel( 'Path ' )
        self.pathField = QLineEdit( '$PLAY/001.mov' )
        self.getDirBtn = QToolButton( self )
        # icon = QIcon()
        # icon.addPixmap(QPixmap("file.png"))
        # self.getDirBtn.setIcon(icon)
        self.getDirBtn.clicked.connect( self._getFlipPath )
        self.dirToggle = QCheckBox( 'Create Intermediate Directories' )
        self.dirToggle.setChecked( 1 )
        
        startLabel      = QLabel( 'Start' )
        self.startField = QLineEdit( '$RFSTART' )
        endLabel        = QLabel( 'End' )
        self.endField   = QLineEdit( '$RFEND' )
        gammaLabel        = QLabel( '    Gamma' )
        self.gammaField   = QLineEdit( '2.2' )
        self.gammaField.setFixedSize(QSize(40, 20))
        antialiasLabel        = QLabel( '    Anialiasing' )
        self.antialiasField   = QLineEdit( '4' )
        self.antialiasField.setFixedSize(QSize(40, 20))
        
        flipbookButton = QToolButton( self )
        flipbookButton.clicked.connect( self._flipWrite )
        flipbookButton.setText("Write Flipbook")
        flipbookButton.setFixedSize(QSize(120, 25))
        flipbookButton.setFocusPolicy(Qt.NoFocus)
        
        #============Element Layouts=============
        pathLayout = QHBoxLayout()
        pathLayout.addWidget( pathLabel )
        pathLayout.addWidget( self.pathField )
        pathLayout.addWidget( self.getDirBtn )
        pathLayout.addWidget( self.dirToggle )
        
        rangeLayout = QHBoxLayout()
        rangeLayout.addWidget( startLabel )
        rangeLayout.addWidget( self.startField )
        rangeLayout.addWidget( endLabel )
        rangeLayout.addWidget( self.endField )
        rangeLayout.addWidget( gammaLabel )
        rangeLayout.addWidget( self.gammaField )
        rangeLayout.addWidget( antialiasLabel )
        rangeLayout.addWidget( self.antialiasField )
        
        runLayout = QHBoxLayout()
        runLayout.addWidget( flipbookButton )
        
        #============Master Layout=============
        MasterLayout = QVBoxLayout()
        MasterLayout.addLayout(pathLayout)
        MasterLayout.addLayout(rangeLayout)
        MasterLayout.addLayout(runLayout)
        
        MasterLayout.addStretch(1)
        self.setLayout(MasterLayout)
        self.setProperty("houdiniStyle", True)

    def existsCheck( self, path ) :
        if os.path.exists( path ) and self.replace == 0 :
            question =  hou.ui.displayMessage( '%s already exists.\n Do you whant to replace it?' % path, buttons = ( 'Ok', 'Cancel' ) )
            if question :
                return False
            self.replace = 1
        pathExp = path.replace('\\', '/')
        if not '$PLAY' in pathExp :
            pathExp = pathExp.replace( self.play, '$PLAY' )
        pathExp = pathExp.replace( self.job, '$JOB' )
        ext = pathExp.split('/')[-1]
        mode = 'img' if 'jpg' in ext or 'png' in ext else 'mov'
        if mode == 'img' :
            frameExp = re.search( '\.\d+\.[a-z]+$', pathExp )
            if frameExp :
                frameGrp = frameExp.group().split(".")[-2]
                padding = len(frameGrp)
                pathExp = pathExp.replace( '.%s.' % frameGrp, '.$F%s.' % padding )
        self.pathField.setText( pathExp )
        return True

    def _getFlipPath( self ) :
        startDir = hou.expandString( self.pathField.text() )
        fname = QFileDialog.getSaveFileName(self, "Save Flipbook", dir=startDir, filter="(*.mov *.mp4 *.jpg *.png)")
        if fname[0] :
            self.existsCheck( fname[0] ) 

        
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
        hou.hscript( 'pane -f 1 %s' % pane )
        go = hou.ui.displayMessage( 'Viewport ready?')
        if not go :
            hou.hscript('viewwrite {} {} {}'.format(options, current_view, outpath))
            #print 'viewwrite {} {} {}'.format(options, current_view, outpath)
        hou.hscript( 'pane -f 0 %s' % pane )                
        
        
    def _flipWrite( self ) :
        path = self.pathField.text()
        expandPath = hou.expandString( self.pathField.text() )
        check = self.existsCheck( expandPath )
        if not check :
            return
        lst = path.split('/')
        dir = hou.expandString( '/'.join( lst[:-1] ) )
        name = lst[-1]
        '''
        if os.path.exists( path ) :
            fileList = os.listdir( '/'.join( path.split( '/' )[:-1] ) )
            listString = ''
            i = 0
            for file in fileList :
                listString += file + '\n'
                i += 1
                if i > 20 :
                    listString += '...\n'
                    break
            new = hou.ui.readInput( 'Flip book file is exists! Please enter a new name.\nList of files:\n%s' % listString )
            name = new[1]
            if not name : 
                return
        '''
        if not name.split('.')[-1] in ['jpg', 'png', 'mp4', 'mov'] :
            name += '.mov'
        path = dir + '/' + name
            
        ext  =  name.split('.')[-1]
        baseName = name.split( '.' + ext )[0]
        print baseName
        qual  = int( float( hou.expandString( self.antialiasField.text() ) ) )
        start = int( float( hou.expandString( self.startField.text() ) ) )
        end   = int( float( hou.expandString( self.endField.text() ) ) )
        gamma = float( hou.expandString( self.gammaField.text() ) )
        start = max( 1, start )
        
        if self.dirToggle.checkState() == Qt.CheckState.Checked :
            createPath( dir )
            
        if not ext in [ 'jpg', 'png' ] :
            tmp = dir + '/%s_tmp' % socket.gethostname()
            createPath( tmp )
            ffmpeg = '{0}/ffmpeg/bin/ffmpeg.exe'.format(HOUDINI_GLOB_PATH)
            fps = hou.expandString( '$FPS' )
            
            self.viewwrite( '-q {0} -f {1} {2} -r 2048 858 -g {3} -c'.format( qual, start, end, gamma ), "%s/'$F4'.jpg" % tmp )
            
            cmd = '{0} -framerate {3} -start_number {1} -i {2} -r {3} -vcodec libx264 {4}'.format( ffmpeg, start, tmp + r'/%04d.jpg', fps, path ).replace('/', '\\')
            print cmd
            movie = subprocess.Popen( cmd )
            movie.wait()
            
            for file in os.listdir( tmp ) :
                os.remove( '%s/%s' % ( tmp, file ) )
            os.rmdir( tmp )
            
        else :
            #pass
            self.viewwrite( '-q {0} -f {1} {2} -r 2048 858 -g {3} -c'.format( qual, start, end, gamma ), "%s/%s.%s" % ( dir, baseName.replace( '$F4', "'$F4'" ), ext ) )
        
        cmd = 'explorer /select,%s' % path.replace('/', '\\').replace('$F4', ('%s' % start).zfill(4) )
        subprocess.Popen( cmd )
        self.replace = 0


class dataCleaner( QWidget ) :
    def __init__(self) :
        QWidget.__init__( self )
        self.job = hou.expandString( '$JOB' )

        cleanBox = QGroupBox( 'Data Cleaner' )
        syncBox  = QGroupBox( 'Data Sync' )
        
        scenesLabel = QLabel( 'Scenes dir for clean ' )
        self.scenesField = QLineEdit( '$JOB/scenes' )
        self.getDirBtn = QToolButton( self )
        # icon = QIcon()
        # icon.addPixmap(QPixmap("file.png"))
        # self.getDirBtn.setIcon(icon)
        self.getDirBtn.clicked.connect( self._getScenesPath )

        maskLabel = QLabel( 'Mask Dirs RegExp    ' )
        self.maskField = QLineEdit( '(.*)seq000(.*)' )

        self.startRepareBtn = QToolButton( self )
        self.startRepareBtn.setText( 'REPARE CACHES' )
        self.startRepareBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.startRepareBtn.font().setPointSize(500)
        self.startRepareBtn.clicked.connect( self._runRepare )

        self.startCleanBtn = QToolButton( self )
        self.startCleanBtn.setText( 'CLEAN' )
        self.startCleanBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.startCleanBtn.font().setPointSize(500)
        self.startCleanBtn.clicked.connect( self._runCleaner )

        self.syncButton = QToolButton( self )
        self.syncButton.setText( 'SYNC NOW' )
        self.syncButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.syncButton.clicked.connect( self._runButchSync )

        self.syncGuiButton = QToolButton( self )
        self.syncGuiButton.setText( 'OPEN SYNC GUI' )
        self.syncGuiButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.syncGuiButton.clicked.connect( self._runGuiSync )

         #============Element Layouts=============
        scenesPathLayout = QHBoxLayout()
        scenesPathLayout.addWidget( scenesLabel )
        scenesPathLayout.addWidget( self.scenesField )
        scenesPathLayout.addWidget( self.getDirBtn )

        maskExpresLayout = QHBoxLayout()
        maskExpresLayout.addWidget( maskLabel )
        maskExpresLayout.addWidget( self.maskField )        

        ctartCleanLayout = QHBoxLayout()
        ctartCleanLayout.addWidget( self.startRepareBtn )
        ctartCleanLayout.addWidget( self.startCleanBtn )


        #=============Group Box Layouts===========
        cleanGroupLayout = QVBoxLayout()
        cleanGroupLayout.setContentsMargins(20,20,20,20)
        cleanGroupLayout.addLayout(scenesPathLayout)
        cleanGroupLayout.addLayout(maskExpresLayout)
        cleanGroupLayout.addLayout(ctartCleanLayout)
        cleanBox.setLayout( cleanGroupLayout )

        symcGroupLayout  = QHBoxLayout()
        symcGroupLayout.setContentsMargins(20,20,20,20)
        symcGroupLayout.addWidget( self.syncButton )
        symcGroupLayout.addWidget( self.syncGuiButton )
        syncBox.setLayout( symcGroupLayout )

        
        #============Master Layout=============
        MasterLayout = QVBoxLayout()
        MasterLayout.addWidget(cleanBox)
        MasterLayout.addWidget(syncBox)
        
        #MasterLayout.addStretch(1)
        self.setLayout(MasterLayout)
        self.setProperty("houdiniStyle", True)

    def _getScenesPath( self ) :
        startDir = hou.expandString( self.scenesField.text() )
        fname = QFileDialog.getExistingDirectory( dir = startDir )
        if fname :
            self.scenesField.setText( fname.replace('\\', '/').replace( self.job, '$JOB' ) )

    def _runRepare( self ) :
        reload( dataCleaner2 )
        dataCleaner2.repare()

    def _runCleaner( self ) :
        reload( dataCleaner2 )
        scenes = hou.expandString( self.scenesField.text() )
        mask   = self.maskField.text()
        dataCleaner2.analize( scenes, mask )

    def _runButchSync( self ) :
        subprocess.Popen( ('"%s" "%s"' % (SYNC, SYNC_BATCH) ).replace('/', '\\') )
        print 'Batch sync process initialized!'

    def _runGuiSync( self ) :
        subprocess.Popen( ('"%s" "%s"' % (SYNC, SYNC_GUI) ).replace('/', '\\') )