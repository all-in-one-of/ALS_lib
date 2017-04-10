try :
    from PySide.QtGui import *
    from PySide.QtCore import *
except :
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    
import hou, os, sys, subprocess, json, re, socket
import datetime
import userfuncs

MAYAPY_PATH = 'mayapy.exe'
P4 = "C:/Program Files/Perforce/p4"
START = "//PROJECTS/Alisa_Film/HoudiniProject/scripts/maya_start.py"
PYTHON = "C:/Python27_64/python.exe"
UPDATEASSETS = "//PROJECTS/Alisa_Film/HoudiniProject/scripts/p4update.py"

def openFileInEditor( file ) :
    if os.path.exists( file ) :
        subl = "C:\\Program Files\\Sublime Text 2\\sublime_text.exe"
        cmd = '"%s" %s' % (subl, file)
        subprocess.Popen( cmd )
    else :
        print "Json file not exists!"

def searchNewVersion( scene ) :
    cmd = "%s sync %s" % ( P4, scene )
    sync = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE ).communicate()
    for string in sync :
        if "updating" in string :
            hou.ui.displayMessage( "Successfully get the new version of %s" % scene )
        if "up-to-date" in string :
            hou.ui.displayMessage( "Not found the new version of %s" % scene )

def rescanLC( mlc, path ) :
    if path :
        exclude = mlc.parm("exclude").eval().split(" ")
        par = None
        for child in mlc.children() :
            if child.name() != "parent" :
                child.destroy()
            else :
                par = child

        y = 0
        for item in os.listdir( path ) :
            ext = item.split(".")[-1]
            name = item.replace( ".%s"%ext, "" )
            if ext == "cam" or ext == "light":
                find = None
                for pattern in exclude :
                    if pattern :
                        regex = re.compile( r"%s"%pattern.replace( "*", ".+" ) )
                        s = regex.match( name )
                        if s and ext != 'cam' :
                            find = True

                if not find :
                    node = mlc.createNode( "maya_%s" % ext, node_name = name )
                    if node.parm('dodof') : node.parm('dodof').setExpression('ch("../dodof")')
                    node.parm( "json" ).set( "$MDATA/%s" % item )
                    node.parm( "update" ).pressButton()
                    node.setPosition( hou.Vector2(0, y) )
                    node.setSelectableInViewport(0)
                    node.setFirstInput( par )
                    for child in node.children() :
                        child.setSelectableInViewport(0)

                    y += 0.5

class treeViewWindow(QWidget) :
    def __init__( self, sceneName, node, parent = None ) :
        super(treeViewWindow, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize( 400, 800 )
        self.setWindowTitle('Maya Scene Tree')
        icon = QIcon( hou.expandString("$JOB") + "/icons/maya.png" )
        self.setWindowIcon(icon)

        self.name = sceneName
        self.jsonFile = hou.expandString("$MDATA") + "/sceneDump.json"
        self.node = node
        self.pattern = ""
        self.sep = "|"
        self.objlist = None

        self.treeView = QTreeView()
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openMenu)
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        lights, cameras, meshes = self.getJsonData()
        self.model = QStandardItemModel()
        self.addItems(self.model, lights, "# lights")
        self.addItems(self.model, cameras, "# cameras")
        self.addItems(self.model, meshes, "# meshes")
        self.treeView.setModel(self.model)
        #self.connect(self.treeView.selectionModel(), SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.foo)

        select = QPushButton("OK")
        reset  = QPushButton("Reset") 
        cancel = QPushButton("Cancel") 
        self.connect(select, SIGNAL('clicked()'), self.setSelection)
        self.connect(reset,  SIGNAL('clicked()'), self.selectPattern)
        self.connect(cancel, SIGNAL('clicked()'), self.close)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(select)
        hbox.addWidget(reset)
        hbox.addWidget(cancel)


        self.model.setHorizontalHeaderLabels([self.tr(self.name)])

        layout = QVBoxLayout()
        layout.addWidget(self.treeView)
        layout.addLayout(hbox)
        self.setLayout(layout)

        self.createObjList()
        self.selectionModel = self.treeView.selectionModel()
        self.selectPattern()

        self.setStyleSheet("""
        QWidget {
            color : rgb(180,180,180);
            background-color: rgb(58,58,58);
            border-left: 1px solid rgb(40,40,40);
        }

         QTreeView::item {
            background-color: rgb(58,58,58);
            border-left: 1px solid rgb(40,40,40);
        }

        QTreeView::item::selected {
            background-color: rgb(103,95,92);
            color: rgb(255,255,255);
        }

         QTreeView QHeaderView:section {
            background-color: rgb(58,58,58);
            color: rgb(170,170,170);
        }

        QPushButton{
            background-color: rgb(80,80,80);
            color: rgb(250,250,250);
        }

    """)

    def getJsonData(self) :
        if os.path.exists( self.jsonFile ) :
            jsonData = open(self.jsonFile, "r")
            exportData = json.load(jsonData)
            lights = exportData['lights']
            cameras = exportData['cameras']
            meshes = exportData['meshes']
            return lights, cameras, meshes
        else :
            return "", "", ""

    def createObjList( self ) :
        mode = self.node.parm("mode").eval()
        if mode == "json" :
            jsonObjs = self.node.parm("abcfile").eval().replace(".abc", ".json")
            if os.path.exists( jsonObjs ) and jsonObjs != hou.expandString("$MDATA") :
                jsonData = open(jsonObjs, "r")
                objData = json.load(jsonData)
                self.objlist = objData[ "objects" ]
        else :
            self.objlist  = self.node.parm("selstr").eval().replace(" ", "").split(",")

    def selectPattern(self) :
        self.treeView.clearSelection()
        if self.objlist :
            for obj in self.objlist :
                for i in range( self.model.rowCount() ) :
                    item = self.model.item(i)
                    if item.text() == "# meshes" :
                        self.treeView.expand(item.index())
                    lst = obj.split( self.sep )
                    for j, name in enumerate( lst ) :
                            for k in range(item.rowCount()) :
                                if item.child(k) :
                                    if item.child(k).text() == name :
                                        index = item.child(k).index()
                                        if j == len( lst ) - 1 :
                                            self.selectionModel.select(index, self.selectionModel.Select)
                                        else :
                                            self.treeView.expand(index)
                                            item = item.child(k)

    def setSelection( self ) :
        indexes = self.treeView.selectedIndexes()
        roots = ["# meshes","# lights","# cameras"]
        pattern = []
        for index in indexes :
            item = self.model.itemFromIndex(index)
            basename = item.text()
            fullname = basename
            while item.text() not in roots :
                item = item.parent()
                fullname = "%s|%s" % ( item.text(), fullname )
            for root in roots :
                fullname = fullname.replace( root, "" )

            pattern.append(fullname)
        result = ", ".join(pattern)
        self.node.parm("selstr").set( result )
        self.node.parm("mode").set( "custom" )
        self.close()

    def addChilds( self, parent, name ) :
        item = QStandardItem(name)
        parent.appendRow(item)
        return item

    def findChilds( self, parent, name ) :
        idx = -1
        for i in range( parent.rowCount() ) :
            if parent.child(i).text() == name :
                idx = i
        if idx >= 0 :
            parent = parent.child(idx)
            return parent
        else :
            return None

    def branch( self, node, name ) :
        child = self.findChilds( node, name )
        parent = child if child else self.addChilds( node, name )
        return parent


    def addItems(self, parent, data, rootName):
        root = self.addChilds( parent, rootName )
        for item in data :
            lst = item.split( self.sep )
            del lst[0]
            for i, name in enumerate( lst ):
                parent = self.branch( root, name ) if i == 0 else self.branch( parent, name )

        return None
    
    def openMenu(self, position):
        #print position
    
        indexes = self.treeView.selectedIndexes()
        '''if len(indexes) > 0:
        
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1'''
        
        menu = QMenu()
        menu.addAction(self.tr("Some action"))
        
        menu.exec_(self.treeView.viewport().mapToGlobal(position))


class maya_scene(QObject) :
    def __init__(self, fromnode = True, parent = None) :
        super(maya_scene, self).__init__(parent)
        self.process_maya = None
        self.fromnode = fromnode

        self.node = None
        self.maya_env()

        self.scene = hou.expandString( "$PERFORCE" )
        try :
            self.scene = hou.pwd().parm("scene").eval()
        except:
            pass
            
        self.exportPath = hou.expandString( "$MDATA" )
        self.abc = "0"
        self.light = "1"
        self.cam = "1"
        self.start =  hou.expandString( "$RFSTART" )
        self.end   =  hou.expandString( "$RFEND" )

        self.mode    = "empty"
        self.abcFile = "empty"
        self.selstr  = "empty"
        self.smooth  = "empty"
        self.smoothIter = "empty"
        self.checkMblur = "empty"
        self.step = "empty"
        if fromnode :
            self.initNode()

    def initNode(self) :
        self.node = hou.pwd()
        self.maya_env()
        self.scene = hou.pwd().parm("scene").eval()
        self.exportPath = hou.expandString( "$MDATA" )
        self.abc = str( hou.pwd().parm("doabc").eval() )
        self.light = str( hou.pwd().parm("dolight").eval() )
        self.cam = str( hou.pwd().parm("docam").eval() )

        self.start = str( hou.pwd().parm("f1").eval() )
        self.end   = str( hou.pwd().parm("f2").eval() )
        if 'MLC' in self.node.type().name() :
            if self.node.parm('lslight').eval() :
                self.light = "0"

    def maya_env(self) :
        NETSOFT_PATH = os.environ["NETSOFT_PATH"]
        MAYA_VERSION = "2016"
        MAYA_ARCH = "-x64"
        MAYA_LOCATION = "C:/Autodesk/Maya%s%s" % ( MAYA_VERSION, MAYA_ARCH )
        MR_VERSION = "3131"
        MAYA_CGRU_LOCATION = "//%s/TOOLS/cgru" % NETSOFT_PATH
        MENTALRAY_LOCATION = "C:/Autodesk/mentalrayForMaya%s" % MAYA_VERSION

        MAYA_SCRIPT_PATH = None #os.environ["MAYA_SCRIPT_PATH"]
        os.environ["MAYA_SCRIPT_PATH"] = ( "//%s/TOOLS/MAYA/scripts;\
                                          //%s/TOOLS/MAYA/AETemplates;\
                                          %s/mel/AETemplates;\
                                          %s/mel/override/%s;\
                                          //%s/TOOLS/MAYA/scripts/z;\
                                          //%s/TOOLS/MAYA/selector2011;&" % ( NETSOFT_PATH, NETSOFT_PATH, MAYA_CGRU_LOCATION, MAYA_CGRU_LOCATION, MAYA_VERSION, NETSOFT_PATH, NETSOFT_PATH ) ).replace( " ", "" )

        os.environ["PYTHONPATH"] = ("//%s/TOOLS/MAYA/scripts;\
                                    //%sTOOLS/MAYA/scripts/MA;\
                                    //%s/TOOLS/MAYA/pythonModules%s;\
                                    //%s/TOOLS/CGRU/afanasy/python;\
                                    //%s/TOOLS/CGRU/lib/python;&" % ( NETSOFT_PATH, NETSOFT_PATH, NETSOFT_PATH, MAYA_VERSION, NETSOFT_PATH, NETSOFT_PATH ) ).replace(" ", "")

        os.environ["MAYA_PLUG_IN_PATH"] = "%s/mll/%s%s;//%s/TOOLS/MAYA/plug-ins%s;&" % ( MAYA_CGRU_LOCATION, MAYA_VERSION, MAYA_ARCH, NETSOFT_PATH, MAYA_VERSION,  )
        os.environ["MAYA_MODULE_PATH"] = "//%s/TOOLS/MAYA/modules/%s%s;&" % ( NETSOFT_PATH, MAYA_VERSION, MAYA_ARCH,  )
        os.environ["MENTALRAY_SHADERS_LOCATION"] = "//%s/TOOLS/MR%s/lib_maya;//%s/TOOLS/MR%s/lib;" % ( NETSOFT_PATH, MR_VERSION, NETSOFT_PATH, MR_VERSION )
        os.environ["MAYA_MR_STARTUP_DIR"] = "//%s/TOOLS/MR%s" % ( NETSOFT_PATH, MR_VERSION )
        os.environ["MI_CUSTOM_SHADER_PATH"] = "//%s/TOOLS/MR%s/include;//%s/TOOLS/MR%s/lib_maya;//%s/TOOLS/MR_TOOLS%s/lib;" % ( NETSOFT_PATH, MR_VERSION, NETSOFT_PATH, MR_VERSION, NETSOFT_PATH, MR_VERSION, )
        os.environ["MENTALRAY_INCLUDE_LOCATION"] = "//%s/TOOLS/MR%s/include" % ( NETSOFT_PATH, MR_VERSION )
        os.environ["MENTALRAY_BIN_LOCATION"] = "%s/bin" % ( MENTALRAY_LOCATION )
        os.environ["IMF_PLUG_IN_PATH"] = "%s/bin/image;&" % ( MENTALRAY_LOCATION  )
        os.environ["MAYA_RENDER_DESC_PATH"] = "%s/rendererDesc;&" % ( MENTALRAY_LOCATION )

        os.environ["ALISA_REF"] = "\\Projects\Alisa"
        os.environ["ALISA_SER"] = "Q:/"
        os.environ["ALISA_FILM"] = "Q:/Film"
        '''
        os.environ["PATH"] = "%s/bin;%s/bin;&" % ( MAYA_LOCATION, MENTALRAY_LOCATION  )
		'''
        print "[ %s ] Successfully setup maya environment..." % datetime.datetime.now().strftime('%H:%M:%S')

    def open( self ) :
        path = hou.hipFile.path()
        curSeq = '%s_%s' % ( hou.hscriptExpression( '$SEQ' ), hou.hscriptExpression( '$SH' ) )
        if not curSeq in path or curSeq == '_' :
            hou.ui.displayMessage( 'Environment does not match to scene path!\nTry agayn when reload be completed.' )
            userfuncs.reloadScene()
            return
        print "[ %s ] Synchronize assets in perforce..." % datetime.datetime.now().strftime('%H:%M:%S')
        assetsCmd = "%s %s" % ( PYTHON, UPDATEASSETS )
        assets = subprocess.Popen( [ 'p4', 'sync', '-q', 'Q:/Film/Assets/...' ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        #assets = subprocess.Popen( [ 'p4', 'sync', '-q', 'Q:/Film/Assets/...' ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        #assets = subprocess.Popen( ['p4', 'sync', '-q', 'Q:/Film/Assets/...'] )
        assets.wait()
        sync = assets.communicate()
        print sync[0]

        print "[ %s ] Synchronize scene in perforce..." % datetime.datetime.now().strftime('%H:%M:%S')
        camScene = self.scene.replace(".ma", "Cam.ma")
        
        p4sync = subprocess.Popen( [ 'p4', 'sync', '-q', self.scene ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        p4sync.wait()
        sync = p4sync.communicate()
        print sync[0]
        
        p4stat = subprocess.Popen( [ 'p4', 'fstat', '-q', self.scene ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        p4stat.wait()
        fstat = p4stat.communicate()
        print fstat[0]
        fstatArray = [ i.replace('... ', '').replace('\r', '') for i in fstat[0].split('\n') ]
        fstatDict = dict( (i.split(' ')[0], i.split(' ')[-1]) for i in fstatArray )
        otherOpen = fstatDict.has_key('otherOpen')
        
        doexport = 1
        
        if otherOpen :
            doexport = hou.ui.displayMessage( "Scene locked by %s?\n Are you sure want to export it?" % fstatDict[ 'otherOpen0' ], buttons=('OK', 'Cancel') )
            if doexport :
                return
        else :
            doexport = hou.ui.displayMessage( "Are uou sure want to update cache?", buttons=('OK', 'Cancel') )

        if doexport == 0 :
            print "[ %s ] Export path = %s" % (datetime.datetime.now().strftime('%H:%M:%S'), self.exportPath )
            print "[ %s ] Create maya process...\nStart scene %s..." % ( datetime.datetime.now().strftime('%H:%M:%S'), self.scene )


            self.process_maya = QProcess(self)
            self.process_maya.setProcessChannelMode(QProcess.MergedChannels)
            self.process_maya.readyRead.connect(self.process_output)
            
            self.process_maya.start( MAYAPY_PATH, [START, 
                                                  self.scene,
                                                  self.start,
                                                  self.end,
                                                  self.abc, 
                                                  self.light, 
                                                  self.cam, 
                                                  self.exportPath, 
                                                  self.abcFile, 
                                                  self.mode,
                                                  "\"" + self.selstr + "\"",
                                                  self.smooth,
                                                  self.smoothIter,
                                                  self.checkMblur,
                                                  self.step, ] )
        
    def process_output(self):
        output = self.process_maya.readAll()
        output = str(output).strip()      
        if output :
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            line = output.replace( "\n", "" )
            line = output.replace( "$$", "\n" )
            cleanLine = line.replace(".", "").replace(" ", "")
            if cleanLine.isdigit() :
                try :
                    curFrame = float( line )
                    frameRange = float(self.end) - float(self.start) + 1
                    percentage = int((( curFrame - float( self.start ) + 1 ) / frameRange) * 100)
                    print "[ %s ] Frame    %.02f -- ( %d%% )" % ( timestamp, curFrame, percentage )
                except :
                    pass

            else :
                print "[ %s ] %s" % ( timestamp, line )

            if "Successfully completed operation!" in output :
                print "[ %s ] Close maya process..." % timestamp
            	self.process_maya.close()
                self.process_maya = None
                if self.fromnode :
                    self.node.parm( "reload" ).pressButton()

    def abcWrite(self) :
        self.mode    = hou.pwd().parm("mode").eval()
        self.abcFile = hou.pwd().parm("abcfile").eval()
        self.selstr  = hou.pwd().parm("selstr").eval()
        self.smooth  = str(hou.pwd().parm("dosmooth").eval())
        self.smoothIter = str(hou.pwd().parm("smoothiter").eval())
        self.checkMblur = str( hou.pwd().parm("checkmblur").eval() )
        self.step = str( hou.pwd().parm("stepsize").eval() )

        basename = self.abcFile.split("/")[-1]
        abcFolder = self.abcFile.replace("/%s" % basename, "" )
        self.exportPath = abcFolder
        self.abcFile = basename
        
        if not os.path.exists(self.abcFile.replace(".abc", ".json")) and  self.mode == "json" :
            print "Json file not exists! AbcExport canceled..."

        else :
            self.open()
            
    def lsexport( self ) :
        if hou.pwd().parm('lslight').eval() :
            for file in os.listdir( self.exportPath ) :
                ext = file.split( '.' )[-1]
                if ext == 'light' :
                    oldlight =  '%s/%s' % (self.exportPath, file)
                    os.remove( oldlight )
            
            
            self.abc = "0"
            self.light = "1"
            self.cam = "0"
            self.scene = hou.pwd().parm('lsfile').eval()
            self.open()