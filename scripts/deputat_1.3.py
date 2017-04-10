'''
Render manager module for Sidefx houdini and Cinesoft Deputat. Writen by Anton Grabovskiy. 2016.
version 1.0
'''
import hou, os, datetime, subprocess, itertools, re

v = re.compile( '^(\d+)\.(\d+)\.(\d+)' )
x = hou.expandString('$_HIP_SAVEVERSION') 
ver = v.search( x ).groups()

S = 'hy_film16' if ver[0] == '16' else 'hy_film'
STARTER = "//PROJECTS/Alisa_Film/HoudiniProject/scripts/{}.py".format( S ) 
LOCAL = 'Q:/houdini'

#functions 
def searchDriverNode( node ) :    
    tree = []
    drivers = []
    #recurtion function for ssearch nodes
    def nodesTree( node ) :
        tree.append( node )
        for input in node.inputs() :
            nodesTree( input )
    #buid nodes tree
    if node.type().category().name() == "Driver" :
        nodesTree( node )
    else :
        if node.type().name() == "rop_geometry" or node.type().name() == "rop_alembic":
            drivers.append( driverNode( node ) )
    #get drivers from tree
    for n in tree :
        typeName = n.type().name()
        if typeName == "ifd" or typeName == "geometry" :
            drivers.append( driverNode(n) )
            
    return drivers

#ropnode class
class driverNode() :
    def __init__ (self, node) :
        self.node = node
        self.name = node.name()
        self.path = node.path()
        self.job  = hou.expandString( '$JOB' )
        
        self.renderTypes = {"ifd"          : "img",
                            "geometry"     : "geo",
                            "rop_geometry" : "geo",
                            "rop_alembic"  : "abc",}
        
        self.fileParms   = {"ifd"          : "vm_picture",
                            "geometry"     : "sopoutput",
                            "rop_geometry" : "sopoutput",
                            "rop_alembic"  : "filename",}
                            
        self.alfredParms = {"ifd"          : "vm_alfprogress",
                            "geometry"     : "alfprogress",
                            "rop_geometry" : "alfprogress",
                            "rop_alembic"  : "",}
       
        
    def fileParm( self ) : return self.node.parm( self.fileParms[ self.node.type().name() ] )
    def alfredParm( self ) : return self.node.parm( self.alfredParms[ self.node.type().name() ] )
    def start( self ) : return self.node.parm( "f1" ).eval()
    def end( self )   : return self.node.parm( "f2" ).eval()
    
    def filePath( self ) : return self.fileParm().eval().replace( LOCAL, self.job )
    def ext( self ) : 
        ext = self.filePath().split(".")[-1]
        result = "bgeo.sc" if ext == "sc" else ext
        return result
    def basename( self ) : return self.filePath().split("/")[-1].split(".%s"%self.ext())[0]
    def fileDir( self )  : return self.filePath().split( self.basename() )[0]
    
    def type( self ) : return self.renderTypes[ self.node.type().name() ]
    def res( self ) :
        if self.type() == "img" :
            try :
                cam = hou.node( self.node.parm( "camera" ).eval() )
                resx = cam.parm("resx").eval()
                resy = cam.parm("resy").eval()
                return resx, resy
            except :
                hou.ui.displayMessage('No camera selected in %s node!' % self.name)
    
    def postframe( self )  : return self.node.parm("postframe")
    def postrender( self ) : return self.node.parm("postrender")
    
    def padzero( self ) :
        return len( str( max( int(self.start()), int(self.end()) ) ) ) + 1
        
#deputat node class
class deputat() :
    def __init__ ( self, node ) :
        self.node    = node
        self.rop     = hou.node( node.parm("ropnode").eval() )
        self.job     = node.parm('job').eval()
        self.rcpath  = node.parm('rcpath').eval()
        self.seq     = node.parm('seq').eval()
        self.sh      = node.parm('sh').eval()
        self.hdata   = '{0}/data/{1}/{1}_{2}'.format( self.job, self.seq, self.sh) #node.parm('hdata').eval()

        self.simmode = node.parm('simmode').eval()
        self.distribute = node.parm('distribute').eval()
        self.distributemode  = node.parm('distribmode').eval()
        self.distributeparts = node.parm('distribparts').eval()

        self.save    = node.parm('save_scene').eval()
        self.new_ver = node.parm('increment').eval()
        self.submit  = node.parm('submit').eval()
        self.wedge   = node.parm('wedge').eval()        
        self.cmd     = node.parm('cmd').eval()
        self.comment = node.parm('comment').eval()
        self.tilescript = node.parm('tilescript').eval()
        self.seq_sh  = "%s_%s"%(self.seq, self.sh)
        self.hstart  = '%s/scripts'%self.job
        
        self.hipName = hou.hipFile.name()
        self.hipBasename = hou.hipFile.basename().split(".hip")[0]
        self.taskName = "%s.%s" % ( self.seq_sh, self.hipBasename )

        self.prerender = self.node.parm('dopreren').eval()

    def runPrerender( self ) :
        code = self.node.parm('prerenscript').eval()
        exec( code )
    
    def drivers( self ) :
        result = searchDriverNode( self.rop ) if self.rop else None
        if not result : hou.ui.displayMessage( "Render Node must be a mantra, geometry or rop_geometry node!" )
        return result
        
    def driversString( self ) :
        result = ""
        for idx, d in enumerate( self.drivers() ) :
            result += "%s" % d.name
            if idx < len( self.drivers() )-1 : result += ","
        return result

    def totalFrames( self ) :
        total = 0
        mode = self.mode()
        for driver in self.drivers() :
            if "wedge" in mode :
                total += self.wIters() * abs( int( driver.start() ) - int( driver.end() ) ) if "sim" in mode else self.wIters()
            else :
                total += abs( int( driver.start() ) - int( driver.end() ) ) + 1

        return total
        
    def mode( self ) :
        if self.simmode and self.distribute : return "distribute_sim"
        if self.simmode and self.wedge : return "wedge_sim"
        if self.simmode : return "sim"
        if self.wedge : return "wedge"
        else : return "default"
        
    def wedgeGen( self ) :
        wedgeDict = {}
        wedgeDict["prefix"] = self.node.parm('task').eval()
        wedgeDict["frame"]  = self.node.parm('frame').eval()
        size = self.node.parm("size").eval()
        wedgeDict["size"] = size
        
        x = [range(self.node.parm("steps%d"%(i+1)).eval()) for i in range(size)]
        steps = list(itertools.product(*x))
        
        name = []
        chan = []
        minV = []
        maxV = []
        maxStep = []
        stepSize = []
        
        for i in range( size ) :    
            name.append( self.node.parm("name%d"%(i+1)).eval() )
            chan.append( self.node.parm("chan%d"%(i+1)).eval() )
            minV.append( self.node.parm("range%dx"%(i+1)).eval() )
            maxV.append( self.node.parm("range%dy"%(i+1)).eval() )
            maxStep.append( self.node.parm("steps%d"%(i+1)).eval() )
            stepSize.append( (maxV[i] - minV[i]) / (maxStep[i] - 1) )
            
        wedgeDict["names"] = name
        wedgeDict["chans"] = chan
            
        wedgeDict["parms"] = []
        for element in steps :
            parmSet = []
            for num in range(size) :
                result = [ i * stepSize[num] + minV[num] for i in range( maxStep[num] )][element[num]]           
                parmSet.append( result )
                
            wedgeDict["parms"].append(parmSet)
            
        return wedgeDict
        
    def wPrefix( self ) : return self.wedgeGen()["prefix"]
    def wFrame ( self ) : return self.wedgeGen()["frame"]
    def wSize  ( self ) : return self.wedgeGen()["size"]
    def wNames ( self ) : return self.wedgeGen()["names"]
    def wChans ( self ) : return self.wedgeGen()["chans"]
    def wParms ( self ) : return self.wedgeGen()["parms"]
    
    def wIters   ( self ) : return len( self.wedgeGen()["parms"] )
    def wPadzero ( self ) : return len( str ( self.wIters() ) ) + 1
    
    def wFont      ( self ) : return self.node.parm("font").unexpandedString()
    def wFontSize  ( self ) : return self.node.parm("fontsize").eval()
    def wFontColor ( self ) : 
        R = int( round( self.node.parm("fontclrr").eval() * 255 ) )
        G = int( round( self.node.parm("fontclrg").eval() * 255 ) )
        B = int( round( self.node.parm("fontclrb").eval() * 255 ) )
        return R,G,B
    def wFontPos ( self )   : return self.node.parm("fontpos").eval()
    def wPadding ( self ) :
        x = self.node.parm("paddingx").eval()
        y = self.node.parm("paddingy").eval()
        return x,y
        
    def wWatermark ( self, driver, num, file  ) :
        x = self.wPadding()[0]
        y = self.wPadding()[1]
        if self.wFontPos() == "top" :
            y = driver.res()[1] - y - self.wFontSize()
        pos = x, y
        cmd = 'unix hwatermark -x %d %d -c %d %d %d -m "' % tuple(itertools.chain( pos, self.wFontColor() ) )
        for i in range( self.wSize() ) :
            cmd += '%s\ =\ %s\;\ ' % ( self.wNames()[i], self.wParms()[num][i] )
        cmd += '" "%s" "%s" %s %d' % ( file, file, self.wFont(), self.wFontSize() )
        return cmd
        
    def dirs( self, type ) :
        outpath = None
        if type == "img" : outpath = self.rcpath
        if type == "geo" : outpath = self.hdata
        if type == "abc" : outpath = self.hdata
        export = outpath + "/_EXPORT"
        vfx    = export + "/VFX" if type == "img" else export
        hycmd  = vfx + "/hycmd"
        for dir in ( export, vfx, hycmd ) :
            if not os.path.exists(dir) :
                os.mkdir(dir)
                
        return { "VFX" : vfx, "hycmd" : hycmd }
        
    def getTaskName( self, driver, num ) :
        taskName = self.taskName
        if "wedge" in self.mode() :
            taskName += ".%s.%s" % ( driver.name, self.wPrefix() )
        if ("default" or "sim") and not "wedge" in self.mode() :
            taskName += ".%s" % driver.name

        return taskName

    def getWedgeTaskName( self, driver, num ) :
        taskName = "%s_" % self.wPrefix()
        for idx in range( self.wSize() ) :
            val = "%d" % self.wParms()[num][idx] if "wedge_sim" in self.mode() else ""
            taskName += self.wNames()[idx] + val
            if idx < self.wSize() - 1 :
                taskName += "_"

        return taskName

    def wedgeNamesString( self, num ) :
        result = ""
        for i in range( self.wSize() ) :
            result += "%s=%s, " % ( self.wNames()[i], self.wParms()[num][i] )
        return result

    def getCurOutPath( self, driver, num, distrib ) :
        dtype = driver.type()
        outpath = ""
        if dtype != "abc" :
            pattern = re.compile("\$F\d")
            pathParm = driver.fileParm().unexpandedString()
            frameExp = pattern.search( pathParm ).group()
            padzero = int( frameExp.split("$F")[1] )
            splitName = driver.fileParm().unexpandedString().split( frameExp )
            number = "%0*d"%(padzero, num)
            splitName = [ s.replace( '$CLUSTER', str(distrib) ) for s in splitName ]
            splitName = [ s.replace( '$SLICE',   str(distrib) ) for s in splitName ]
            outpath = hou.expandString( splitName[0].replace( "$OS", driver.name ) ) + number + hou.expandString( splitName[1].replace( "$OS", driver.name ) )
        else :
            outpath = driver.fileParm().eval()
        #print( 'Distrib = %s      path = %s' % ( distrib, outpath ) )
        return outpath.replace( LOCAL, self.job )

        
    def hycmd( self, driver, num, fmode = "r", distrib = 0 ) :
        start = num
        end = num
        mode = self.mode()
        taskName = "%s.%s" % ( self.getTaskName( driver, num ), mode )
        filename = self.dirs( driver.type() )["hycmd"]
        outpath = self.getCurOutPath( driver, num, distrib )
        fileDir = driver.fileDir()
        
        code = 'hou.hipFile.load("%s")\n' % ( hou.hipFile.path() )
        code += 'rop = hou.node("%s")\n' % driver.path

        if driver.alfredParm() :
            code += 'rop.parm("%s").set(1)\n' % driver.alfredParm().name()
        if driver.type() == "img" : 
            code += 'rop.parm("vm_image_comment").set("%s")\n' % self.comment
            code += 'rop.parm("vm_verbose").set(4)\n'
            code += 'rop.parm("vm_vexprofile").set(2)\n'
            code += 'rop.parm("vm_tilecallback").set("%s")\n' % self.tilescript
            
        if "wedge" in self.mode() :
            for p in range( self.wSize() ) :
                code += 'hou.parm("%s").set("%s")\n' % ( self.wChans()[p], self.wParms()[num][p] )

            wPadzero = self.wPadzero()
            wedgeTaskName = taskName.replace( "%s." % self.seq_sh, "" )
            dirList = fileDir.split("/")
            dirList = dirList[:-2] + [ "WEDGE" ] + dirList[-2:]
            fileDir = "/".join( dirList )
            outpath = "%s%s.w%0*d" % ( fileDir, wedgeTaskName, wPadzero, num )
            filename += "/%s.w%0*d" % ( wedgeTaskName, wPadzero, num )
            
            if "wedge_sim" in mode :
                filename = self.dirs( driver.type() )["hycmd"] + "/%s.w%0*d" % ( wedgeTaskName, wPadzero, num )
                outpath += ".f$F%d" % driver.padzero()
            outpath += ".%s" % driver.ext()
            filename += ".hycmd"
            filename = filename.replace( "%s." % self.seq_sh, "" )
            code += 'rop.parm("%s").set("%s")\n' % ( driver.fileParm().name(), outpath )
            
            if driver.type() == "img" :
                comment = ""
                for i in range( self.wSize() ) :
                    comment += '%s= %s;' % ( self.wNames()[i], self.wParms()[num][i] )
                side = 0 if "bottom" in self.wFontPos() else 1
                code += 'rop.parm("vm_image_comment").set("%s (%s)")\n' % (self.comment, (comment) )
                code += 'rop.parm("postframe").set(\'%s\')\n' % self.wWatermark( driver, num, outpath )
                code += 'alpha = hou.node("/obj").createNode("wedge_message_alpha")\n'
                code += 'alpha.parm("resy").set(%d)\n' % driver.res()[1]
                code += 'alpha.parm("fontsize").set(%d)\n' % self.wFontSize()
                code += 'alpha.parm("padding").set(%d)\n' % self.wPadding()[1]
                code += 'alpha.parm("side").set(%d)\n' % side
                
        if "sim" in mode :
            start = driver.start()
            end = driver.end()
            if driver.type() != "abc" :
                code += 'rop.parm("lpostframe").set("python")\n'
                postframe  = "import datetime\\n"
                postframe += "now = datetime.datetime.now().strftime('%H:%M:%S')\\n"
                postframe += "print ( \'[%s] Frame finished ( %s )\' % ( now, hou.expandString(\'$F\') ) )"
                code += 'rop.parm("postframe").set("%s")\n' % postframe
            if not "wedge" in mode : filename = "%s/%s.hycmd" % ( self.dirs( driver.type() )["hycmd"], taskName )
        if mode == "wedge" :
            start = self.wFrame()
            end = start

        if mode == "distribute_sim" :
            outpath = self.getCurOutPath( driver, num, distrib )
            distribVar = "CLUSTER" if self.distributemode == 0 else "SLICE"
            distribType = "cluster" if self.distributemode == 0 else "slice"
            code += "hou.hscript('set -g %s=%s')\n" % ( distribVar, num )
            filename = "%s/%s.%s.%d.hycmd" % ( self.dirs( driver.type() )["hycmd"], taskName, distribType, num )


        code += 'rop.render( frame_range = ( %d, %d ), output_progress = True )\n' % ( start, end )
        code += 'exit()\n'


        if "default" in mode :
            filename += "/%s.f%0*d.hycmd" % ( taskName, driver.padzero(), num )
        
        if fmode == "w" :
            hycmdFile = open(filename, "w")
            hycmdFile.write(code)
            hycmdFile.close()

        return { "code" : code, "name" : filename, "outpath" : outpath }

    def AlfredClean( self, driver, alfName ) :
        code  = "-cleanup {\n"
        cmd = "        Cmd {Alfred} -msg {File delete \"?\"}\n"
        mode = self.mode()

        if mode == "sim" :
            code += cmd.replace("?", self.hycmd(driver, 0)["name"] )

        if "wedge" in mode :
            for w in range( self.wIters() ) :
                code += cmd.replace("?", self.hycmd(driver, w)["name"] )

        if mode == "distribute_sim" :
            for p in range( self.distributeparts ) :
                code += cmd.replace("?", self.hycmd(driver, p)["name"] )

        if "default" in mode :
            for f in range( int( driver.start() ), int( driver.end() ) + 1 ) :
                code += cmd.replace("?", self.hycmd(driver, f)["name"] )

        code += cmd.replace("?", alfName )
        code += "    }\n"

        return code

        
    def alf( self ) :
        driversString = self.driversString()
        drivers = self.drivers()
        minFrame = ""
        maxFrame = ""
        mode = self.mode()
        rname = "dep" if self.node.name() == "deputat1" else self.node.name()
        mainTaskName = "%s-r(%s)-d(%s)-tf(%d)-m(%s)" % ( self.taskName, rname, driversString, self.totalFrames(), mode )
        fileNameBase = mainTaskName.replace("-", ".").replace("(", "-").replace(")", "").replace(",", ".")
        alfName = "%s/%s.alf" % ( self.dirs("img")["VFX"], fileNameBase )
        #starter = "//PROJECTS/Alisa_Film/HoudiniProject/scripts/hy_chess.py"
        starter = STARTER
        
        
        now_time = datetime.datetime.now()
        code  = "##AlfredToDo 3.0 header %s" % now_time.strftime("%d/%m/%Y %H:%M:%S\n")
        code += "# spooled as: %s\n" % alfName
        code += "# last estimated time remaining: +0:01:10\n\n"
        code += "Job -title {%s}\\\n" % ( mainTaskName )
        code += "    -comment {%s}\\\n" % self.comment
        #code += "}\n"
        code += "    -subtasks {\n"
        
        if mode == "sim" :
            for idx, driver in enumerate( drivers ) :
                cmdName = driver.name
                cmdFile = self.hycmd( driver, 0, "w" )["name"]
                driverPadzero = driver.padzero()
                start = int( driver.start() )
                end = int( driver.end() )
                drType = driver.type()
                if len( drivers ) == 1 :
                    code += "    Task {%s -t(%s) -fr(%d-%d)} -cmds {\n" % ( cmdName, drType, start, end )
                    code += "        RemoteCmd {python.exe \\\"%s\\\" \\\"%s\\\"} -service {mantra} -tags {mantra}\n        }" % ( starter, cmdFile )
                    code += "%s" % ( (" -preview {\n            mplay.exe \"%s\"\n        }" % self.hycmd(driver, start)["outpath"] ) if driver.type() == "img"\
                                else (" -preview {\n            gplay.exe \"%s\"\n        }"  % self.hycmd(driver, start)["outpath"] ) )
                    if idx == len( drivers ) - 1 : code += " %s" % ( self.AlfredClean( driver, alfName ) )
                else : 
                    if idx == 0 : code += "    Task {(%s) -m(%s)} -subtasks {\n" % ( driversString, mode )
                    code += "        Task {%s -t(%s) -fr(%d-%d)} -cmds {\n" % ( cmdName, drType, start, end )
                    code += "            RemoteCmd {python.exe \\\"%s\\\" \\\"%s\\\"} -service {mantra} -tags {mantra}\n        }" % ( starter, cmdFile )
                    code += "%s" % ( (" -preview {\n            mplay.exe \"%s\"\n        }\n" % self.hycmd(driver, start)["outpath"] ) if driver.type() == "img"\
                                else (" -preview {\n            gplay.exe \"%s\"\n        }\n"  % self.hycmd(driver, start)["outpath"] ) )
                    if idx == len( drivers ) - 1 : code += "   } %s" % ( self.AlfredClean( driver, alfName ) )
                    
        if "wedge" in mode :
            size = self.wSize()
            iters = self.wIters()
            padzero = self.wPadzero()
            for idx, driver in enumerate( drivers ) :
                driverPadzero = driver.padzero()
                start = int( driver.start() )
                end = int( driver.end() )
                subTaskName = "%s -t(%s)" % ( driver.name, driver.type() )
                code += "    Task {%s -wr(%d-%d)} -subtasks {\n" % ( subTaskName, 0, iters - 1 )
                for thread in range( iters ) :
                    cmdName = "%s -p(%s) -w(%0*d)" % ( self.wPrefix(), self.wedgeNamesString(thread), padzero, thread )
                    cmdFile = cmdFile = self.hycmd( driver, thread, "w" )["name"]
                    code += "        Task {%s} -cmds {\n" % ( cmdName )
                    code += "            RemoteCmd {python.exe \\\"%s\\\" \\\"%s\\\"} -service {mantra} -tags {mantra}\n        }" % ( starter, cmdFile )
                    previewFile = self.hycmd(driver, thread)["outpath"].replace( "$F%d" % driverPadzero, "%0*d" % ( driverPadzero, start ) ) if "sim" in mode else self.hycmd(driver, thread)["outpath"]
                    code += "%s" % ( (" -preview {\n            mplay.exe \"%s\"\n        }\n" % previewFile ) if driver.type() == "img"\
                                else (" -preview {\n            gplay.exe \"%s\"\n        }\n"  % previewFile ) )
                    if thread == iters - 1 : code += "   } %s" % ( self.AlfredClean( driver, alfName ) )

        if mode == "distribute_sim" :
            for idx, driver in enumerate( drivers ) :
                driverPadzero = driver.padzero()
                start = int( driver.start() )
                end = int( driver.end() )
                drType = driver.type()
                for thread in range( self.distributeparts ) :
                    distribType = "cluster" if self.distributemode == 0 else "slice"
                    cmdName = "%s -%s(%s)" % ( driver.name, distribType, thread )
                    cmdFile = self.hycmd( driver, thread, "w" )["name"]
                    if thread == 0 :code += "    Task {(%s) -m(%s)} -subtasks {\n" % ( driversString, mode )
                    code += "        Task {%s -t(%s) -fr(%d-%d)} -cmds {\n" % ( cmdName, drType, start, end )
                    code += "            RemoteCmd {python.exe \\\"%s\\\" \\\"%s\\\"} -service {mantra} -tags {mantra}\n        }" % ( starter, cmdFile )
                    code += "%s" % ( (" -preview {\n            mplay.exe \"%s\"\n        }\n" % self.hycmd(driver, start, 'r', thread)["outpath"] ) if driver.type() == "img"\
                                else (" -preview {\n            gplay.exe \"%s\"\n        }\n"  % self.hycmd(driver, start, 'r', thread)["outpath"] ) )
                    if thread == len( range( self.distributeparts ) ) - 1 : code += "   } %s" % ( self.AlfredClean( driver, alfName ) )

        if "default" in mode :
            for idx, driver in enumerate( drivers ) :
                cmdName = driver.name
                driverPadzero = driver.padzero()
                start = int( driver.start() )
                end = int( driver.end() )
                subTaskName = "%s -t(%s)" % ( driver.name, driver.type() )
                code += "    Task {%s -fr(%d-%d)}  -subtasks {\n" % ( subTaskName, start, end )
                for thread in range( start, end + 1 ) :
                    cmdFile = self.hycmd( driver, thread, "w" )["name"]
                    code += "        Task {%s -f(%0*d)} -cmds {\n" % ( cmdName, driverPadzero, thread )
                    code += "            RemoteCmd {python.exe \\\"%s\\\" \\\"%s\\\"} -service {mantra} -tags {mantra}\n        }" % ( starter, cmdFile )
                    code += "%s" % ( (" -preview {\n            mplay.exe \"%s\"\n        }\n" % self.hycmd(driver, thread)["outpath"] ) if driver.type() == "img"\
                                else (" -preview {\n            gplay.exe \"%s\"\n        }\n"  % self.hycmd(driver, thread)["outpath"] ) )
                    if thread == end : code += "   } %s" % ( self.AlfredClean( driver, alfName ) )

        code += "}" if "sim" or "default" in mode else "     }\n}"
        code += "\n## --- End of Job '%s-j(houdini)'" % mainTaskName

        alfFile = open( alfName, "w" )
        alfFile.write( code )
        alfFile.close()

        return alfName

    def saveHipFile(  self ) :
        if self.new_ver :
            hou.hipFile.saveAndIncrementFileName()
        else :
            hou.hipFile.save()

    def render( self ) :
        must_vars = [self.rcpath, self.hdata, self.seq, self.sh]
        empty = ""
        for var in must_vars :
            if not var :
                ready = False
                empty += " %s," % var
        if empty : hou.ui.displayMessage("Empty variables:%s!" % empty )
        else : 
            alfred = self.alf()
            if self.submit :
                #submit_job = os.system( "%s %s" % ( self.cmd, alfred ) )
                hou.hscript('unix %s "%s"' % (self.cmd, alfred ) )
                #print "%s %s" % ( self.cmd, alfred.replace( "/", "\\" ) )
                #subprocess.Popen( "%s %s" % ( self.cmd, alfred.replace( "/", "\\" ) ) )
   


#================================================ send tasks =============================================================
dep = deputat(hou.pwd())
if dep.prerender :
    dep.runPrerender()
if dep.save :
    dep.saveHipFile()
dep.render()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        