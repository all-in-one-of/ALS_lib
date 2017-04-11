import hou, toolutils
import colors
import os
import tempfile
import re
reload( colors )

def checkSelection( ) :
    node = None
    try :
        node = hou.selectedNodes()[0]
    except :
        print "Nothing selected!"
    
    return node

def readRopFile() :
    root = hou.node("/obj")
    node = checkSelection()
    
    if node and node.type() == hou.nodeType(hou.sopNodeTypeCategory(), "rop_geometry"):
        name = node.name()
        path = node.parm("sopoutput").unexpandedString()
        geo = root.createNode("geo", node_name = name)
        file = geo.node("file1")
        file.setName(name)
        file.parm("file").set(path)
        file.setSelected(1)
        
def newHipFileVersion() :
    confirm = hou.ui.displayMessage( "New version of hip file  will be create. Are you sure?", buttons=('OK', 'Cancel') )
    if confirm == 0 :
        hou.hipFile.saveAndIncrementFileName()
        import workCal
        workCal.writeVisit( scenes = 1 )

def createMerge() :
    node = checkSelection()
        
    if node :
        name = node.name()
        parent = node.parent()
        pos = node.position()
        merge = parent.createNode("object_merge", node_name = "merge_%s"%name)
        #merge.parm("objpath1").set("../%s"%name)
        merge.parm("objpath1").set(node.path())
        merge.setPosition(pos + hou.Vector2(1.5, 0) )
        node.setSelected(0)
        merge.setSelected(1)
        clr = hou.Color( colors.merge )
        merge.setColor( clr )
        
def createNullOutput() :
    node = checkSelection()
    
    if node :
        parent = node.parent()
        pos = node.position()
        out = parent.createNode("null", node_name = "OUT")
        out.setPosition( pos + hou.Vector2(0, -1) )
        out.setInput( 0, node )
        out.setDisplayFlag(1)
        try :
            out.setRenderFlag(1)
        except :
            pass
        node.setSelected(0)
        out.setSelected(1)
        clr = hou.Color( colors.null )
        out.setColor( clr )
        
def createOutput() :
    node = checkSelection()
    
    if node :
        parent = node.parent()
        pos = node.position()
        out = parent.createNode("output", node_name = "OUT")
        out.setPosition( pos + hou.Vector2(0, -1) )
        out.setInput( 0, node )
        out.setDisplayFlag(1)
        try :
            out.setRenderFlag(1)
        except :
            pass
        node.setSelected(0)
        out.setSelected(1)
        clr = hou.Color( colors.output )
        out.setColor( clr )
        
def reloadScene() :
    if not "untitled.hip" in hou.hipFile.basename() :
        scene = hou.hipFile
        path = scene.path()
        scene.save()
        hou.hipFile.load(path)
        
    
def setSelectedGroup() :
    node = hou.selectedNodes()[0]
    if node :
        geo = node.geometry()
        selection = node.geometry().selection()
        type = selection.selectionType()
        pattern = ""
        typeStr = ""
        
        if type == hou.geometryType.Points :
            typeStr = "point" if node.parm("entity") else "points"
            for p in selection.points(geo) :
                pattern += "%d " % p.number()
        if type == hou.geometryType.Primitives :
            typeStr = "primitive" if node.parm("pattern") else "prims"
            for p in selection.prims(geo) :
                pattern += "%d " % p.number()
                
        try :
            node.parm("entity").set(typeStr)
            node.parm("pattern").set(pattern)
            
        except :
            try :
                node.parm("grouptype").set(typeStr)
                node.parm("group").set(pattern)
            except :
                try :
                    node.parm("group").set(pattern)
                except :
                    pass

def displaySelectPattern() :
    node = hou.selectedNodes()[0]
    if node :
        geo = node.geometry()
        selType = hou.geometryType.Primitives
        result = ""
        elements = []

        entyty    = node.parm("entity")
        grouptype = node.parm("grouptype")
        pattern   = node.parm("pattern")
        group     = node.parm("group")

        if entyty :
            if entyty.eval() == 1 : selType = hou.geometryType.Points
            if pattern : result = pattern.eval()

        else :
            if grouptype : 
                if grouptype.eval() == 1 : selType = hou.geometryType.Points
            if group : result = group.eval()


        if selType == hou.geometryType.Points :
            for point in geo.points() :
                if str( point.number() ) in result : elements.append( point )

        if selType == hou.geometryType.Primitives :
            for prim in geo.prims() :
                if str( prim.number() ) in result : elements.append( prim )

        #print ( elements )
        hou.Selection( elements )


def checkSnippet() :
    selection = hou.selectedNodes()
    if selection :
        node = selection[0]
        if node :
            snippet = None
            try :
                snippet = node.parm("snippet")
            except :
                hou.ui.displayMessage( "Nothing wrangle was selected!" )

            if snippet :
                return snippet
    else :
        hou.ui.displayMessage( "Nothing selected!" )
        return None

def deleteByName() :
    node = hou.selectedNodes()[0]
    if node :
        geo = node.geometry()
        selection = node.geometry().selection()
        type = selection.selectionType()
        elements = selection.points( geo ) if type == hou.geometryType.Points else selection.prims( geo )
        grouptype = "point" if type == hou.geometryType.Points else "prims"
        selNames = []
        for p in elements :
            name = p.attribValue("name")
            selNames.append( "@name=%s"%name )
            
        selString = ' '.join( list( set (selNames) ) )
            
        parent = node.parent()
        pos = node.position()
        
        blast = parent.createNode("blast")
        blast.setPosition( pos + hou.Vector2(0, -1) )
        blast.setInput( 0, node )
        blast.parm( "group" ).set( selString )
        blast.parm( "negate" ).set( 1 )
        blast.setDisplayFlag(1)
        blast.setRenderFlag(1)
        node.setSelected(0)
        blast.setSelected(1)

def deleteByName16() :
    node = hou.selectedNodes()[0]
    if node :
        selNames = []
        geo = node.geometry()
        viewer = toolutils.sceneViewer()
        viewportSel =  viewer.selectGeometry()
        for selection in viewportSel.selections() :
            type = selection.selectionType()
            elements = selection.points( geo ) if type == hou.geometryType.Points else selection.prims( geo )
            grouptype = "point" if type == hou.geometryType.Points else "prims"
            for p in elements :
                name = p.attribValue("name")
                selNames.append( "@name=%s"%name )
            
        selString = ' '.join( list( set (selNames) ) )
            
        parent = node.parent()
        pos = node.position()
        
        blast = parent.createNode("blast")
        blast.setPosition( pos + hou.Vector2(0, -1) )
        blast.setInput( 0, node )
        blast.parm( "group" ).set( selString )
        blast.parm( "negate" ).set( 1 )
        blast.setDisplayFlag(1)
        blast.setRenderFlag(1)
        node.setSelected(0)
        blast.setSelected(1)

def changeCase( mode ) :
    nodes = hou.selectedNodes()
    if nodes :
        for node in nodes :
            name = node.name()
            newName = name.upper() if mode == "upper" else name.lower()
            node.setName( newName )


def opinputPath() :
    instertPoint =  "#"
    exp = '`opinputpath( ".", 0 )`'
    node = checkSelection()
    if node :
        for parm in node.parms() :
            parm_template = parm.parmTemplate()
            if isinstance(parm_template, hou.StringParmTemplate):
                if instertPoint in parm.eval() :
                    parm.set( parm.eval().replace( instertPoint, exp ) )


def nameByFile() :
    nodes = hou.selectedNodes()
    if nodes :
        for node in nodes :
            filename = node.parm( "fileName" ) if node.type().name() == "alembic" else node.parm( "file" )
            if filename :
                name = filename.eval().split("/")[-1].split(".")[:-1]
                name = "_".join(name)
                try :
                    node.setName( name )
                except :
                    hou.ui.displayMessage( 'Can not rename node "%s"'% node.path() )

def cachePrefix() :
    prefix = hou.ui.readInput( "Enter prefix:", buttons = ("OK", "Cancel") )
    #print prefix
    if prefix[0] == 0 and prefix[1] :
        for child in hou.node("/obj").allSubChildren() :
            if child.type().name() == "grabovskiy::my_cache::1.0.0" :
                current = child.parm("name").eval()
                newName = "%s_%s" % (current, prefix[1] )
                child.parm("name").set( newName )
                child.hdaModule().rename( child )


def cacheReplacePrefix() :
    sel = hou.selectedNodes()
    if sel :
        print sel[0]
        root = sel[0].parent()
        prefix = hou.ui.readMultiInput( "Replace prefix in cache files:", ("Old prefix:", "New prefix"), buttons = ("OK", "Cancel") )
        #print prefix
        if prefix[0] == 0 and prefix[1] :
            for child in root.allSubChildren() :
                if child.type().name() == "grabovskiy::my_cache::1.0.0" :
                    current = child.parm("name").eval()
                    newName = current.replace( prefix[1][0], prefix[1][1] )
                    child.parm("name").set( newName )
                    child.hdaModule().rename( child )

def HDA_IncrementVersion( threshold, dirPath, namePrefix, major, minor, work, idx=0 ) :
    res = ""
    new_work  = work
    new_minor = minor
    new_major = major

    if( work + 1 ) >= threshold :
        new_work = 0
        if( minor + 1 ) >= threshold :
            new_minor = 0
            new_major = major + 1
        else :
            new_minor = minor + 1
    else :
        new_work = work + 1

    filePath = "%s/%s_%d.%d.%d.hda" % ( dirPath, namePrefix, new_major, new_minor, new_work )
    checkFile = os.path.exists( filePath )
    prevVer = "%s/%s_%d.%d.%d.hda" % ( dirPath, namePrefix, major, minor, work )
    if not checkFile : return (True, filePath, [new_major, new_minor, new_work], prevVer, idx)
    else :
        idx += 1
        find = None
        lastFile = filePath
        while not find :
            res = HDA_IncrementVersion( threshold, dirPath, namePrefix, new_major, new_minor, new_work, idx )
            find = res[0]

        return res

def HDA_isUnlockedAsset( node ):
    return not node.isLocked() and node.type().definition() is not None


def HDA_AddVersion( threshold = 10 ) :
    selected_nodes = hou.selectedNodes()
    tempHdaPath = ''
    tempPath = ''
    if selected_nodes :
        for node in selected_nodes :
            hdaDef = node.type().definition()
            if hdaDef :
                libPath = hdaDef.libraryFilePath()
                dirPath = "/".join( libPath.split("/")[:-1] )
                fileName = libPath.split("/")[-1].replace(".hda", "")
                hdaVersion = fileName.split("_")[-1].split(".")
                namePrefix = "_".join( fileName.split("_")[:-1] )
                major = int( hdaVersion[0] )
                minor = int( hdaVersion[1] )
                work  = int( hdaVersion[2] )

                new_version = HDA_IncrementVersion( threshold, dirPath, namePrefix, major, minor, work )
                if new_version[-1] > 0 :
                    hou.ui.displayMessage( 'Not last version of "%s" selected!\nLast version is: %s\nAbort operation!' % ( namePrefix, new_version[-2] ) )

                else :
                    versioDialog = hou.ui.displayMessage( 'New verion of "%s" will be created. Are you sure?' % namePrefix, ("Ok", "Cancel") )
                    if versioDialog == 1 :
                        break

                    old_type_name  = hdaDef.nodeTypeName()
                    type_name = old_type_name.split("::")[:-1]
                    type_version =  ".".join( [ str( num ) for num in new_version[2] ] )
                    type_name.append( type_version )
                    new_type_name = "::".join( type_name )
                    new_file_path = new_version[1]

                    checkLock = None
                    if HDA_isUnlockedAsset( node ) :
                        tempPath = tempfile.mktemp().replace("\\", "/")
                        tempHdaPath = "%s_%s.hda"%( tempPath, fileName )
                        hdaDef.save( str(tempHdaPath), node )
                        hou.hda.installFile( str(tempHdaPath), None, False, True )
                        hdaDef = node.type().definition()
                        hdaDef.setIsPreferred(False)
                        checkLock=True
                    
                    hdaDef.copyToHDAFile( new_file_path, new_name=new_type_name )
                    hou.hda.installFile( str(new_file_path), None, False, True )
                    node = node.changeNodeType( new_type_name )
                    hdaDef = node.type().definition()
                    hdaDef.setIsPreferred(False)
                    if checkLock :
                        hou.hda.uninstallFile( str(tempHdaPath) )
                        os.remove( tempHdaPath )
                    else :
                        node.allowEditingOfContents()

                    hou.ui.displayMessage( 'Hda "%s" successfully written!' % new_type_name )

def createNewShot() :
    import platform
    system = platform.system()
    seq_sh = hou.ui.readMultiInput( "Enter sequence and shot numbers:", ("Sequence:", "Shot"), buttons = ("OK", "Cancel") )
    if seq_sh[0] == 0 :
        job = hou.expandString( "$JOB" )
        seq = seq_sh[1][0]
        sh  = seq_sh[1][1]
        path = "{0}/scenes/seq{1}/seq{1}_sh{2}".format( job, seq, sh )
        confirm = hou.ui.displayMessage( '"%s" path will be created. Are you sure?' % path, ("Ok", "Cancel") )
        if confirm == 0 :
            lst = path.replace("//","##").split("/")
            current = []
            for num, part in enumerate( lst ) :
                current.append(part)
                pathString = "/".join(current).replace("##", "//")
                currentPath =  pathString if system == "Windows" else "/" + pathString
                if not os.path.exists( currentPath ) :
                    try :
                        os.mkdir( currentPath )
                    except :
                        pass


def mergeToGeo() :
    selected_nodes = hou.selectedNodes()
    if selected_nodes :
        root = hou.node("/obj")
        for node in selected_nodes :
            name = node.name().lower()
            geo = root.createNode("geo", node_name = name)
            geo.node( "file1" ).destroy()
            merge = geo.createNode("object_merge", node_name = "merge_%s"%node.name() )
            #merge.parm("objpath1").set("../%s"%name)
            merge.parm("objpath1").set(node.path())
            clr = hou.Color( colors.merge )
            merge.setColor( clr )

def splitAbc() :
    selected_nodes = hou.selectedNodes()
    if selected_nodes :
        node = selected_nodes[0]
        parent = node.parent()
        geo = node.geometry()
        for num, prim in enumerate( geo.prims() ) :
            name = prim.attribValue("name")
            selString = "@name=%s " % name
            pos = node.position()
            startOffset = hou.Vector2(num * 4 - ( len( geo.points() ) - 1 ) * 2, -2)
            
            #blast node
            blast = parent.createNode("blast", node_name = name )
            blast.setPosition( pos + startOffset )
            blast.setInput( 0, node )
            blast.parm( "group" ).set( selString )
            blast.parm( "negate" ).set( 1 )

def extractTrans( ) :
    s = hou.selectedNodes()
    if s :
        node = None
        out = None
        if s[0].type().category().name() == 'Object' :
            node = s[0]
            out = hou.node('%s/__display_sop__' % node.path() )
        if s[0].type().category().name() == 'Sop' :
            out = s[0]
            node = out.parent()
        if node and out :
            pos = out.position()
            shift = node.createNode('timeshift')
            shift.setPosition( pos + hou.Vector2(-1, -1) )
            shift.setInput( 0, out )
            shift.parm('frame').deleteAllKeyframes()
            shift.parm('frame').set(1)
            
            black = hou.Color( (0,0,0) )
            
            static = node.createNode( 'null', 'STATIC' )
            static.setPosition( pos + hou.Vector2( -1, -2 ) )
            static.setInput( 0, shift )
            static.setColor( black )
            
            animated = node.createNode( 'null', 'ANIMATED' )
            animated.setPosition( pos + hou.Vector2( 1, -2 ) )
            animated.setInput( 0, out )
            animated.setColor( black )
            
            transform = node.parent().createNode( 'extractgeo', '%s_transform' % node.name() )
            transform.setPosition( node.position() + hou.Vector2( 2, 0 ) )
            transform.parm('srcpath').set( static.path() )
            transform.parm('dstpath').set( animated.path() )
            node.setSelected(0)
            transform.setSelected(1)
    return None

def createSubnet() :
    node = checkSelection()
    
    if node :
        parent = node.parent()
        pos = node.position()
        sub = parent.createNode("subnet")
        sub.setPosition( pos + hou.Vector2(0, -1) )
        sub.setInput( 0, node )
        sub.setDisplayFlag(1)
        sub.setRenderFlag(1)
        sparms = sub.parms()
        for p in sparms :
            p.hide(1)

        innull = sub.createNode( 'null', node_name='IN' )
        innull.setInput( 0, sub.indirectInputs()[0] )
        innull.setPosition( hou.Vector2(0, 5) )
        out = sub.createNode( 'output', node_name='output0' )
        out.setInput( 0, innull )
        sub.setColor( hou.Color( colors.subnet ) )
        out.setColor( hou.Color( colors.output ) )
        node.setSelected(0)
        sub.setSelected(1)




'''
def deleteByName() :
    node = hou.selectedNodes()[0]
    if node :
        geo = node.geometry()
        selection = node.geometry().selection()
        type = selection.selectionType()
        elements = selection.points( geo ) if type == hou.geometryType.Points else selection.prims( geo )
        grouptype = "point" if type == hou.geometryType.Points else "prims"
        selString = ""
        for p in elements :
            name = p.attribValue("name")
            selString += "@name=%s "%name
            
        parent = node.parent()
        pos = node.position()
        
        blast = parent.createNode("blast")
        blast.setPosition( pos + hou.Vector2(0, -1) )
        blast.setInput( 0, node )
        blast.parm( "group" ).set( selString )
        blast.parm( "negate" ).set( 1 )
        blast.setDisplayFlag(1)
        blast.setRenderFlag(1)
        node.setSelected(0)
        blast.setSelected(1)
'''