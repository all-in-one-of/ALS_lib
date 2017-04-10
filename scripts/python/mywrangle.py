import hou, os, subprocess

EDITOR = "C:/Program Files/Sublime Text 2/sublime_text.exe"
HISTORY = 10
PADDING = 3

def wrangleType() :
    node = hou.pwd()
    mode = node.parm( "mode" ).eval()
    wtype = node.parm( "type" )
    context = node.type().category().name()
    if context == "Sop" :
        if mode == 0 :
            iterclass = node.parm("class").eval()
            if iterclass == 0 : wtype.set( "sop.detail" )
            if iterclass == 1 : wtype.set( "sop.prim" )
            if iterclass == 2 : wtype.set( "sop.point" )
            if iterclass == 3 : wtype.set( "sop.vertex" )
            if iterclass == 4 : wtype.set( "sop.number" )
        if mode == 1 : wtype.set( "sop.volume" )
        if mode == 2 : wtype.set( "sop.deform" )

    if context == "Dop" :
        if mode == 0 : wtype.set( "dop.field" )
        if mode == 1 :
            iterclass = node.parm("bindclass").eval()
            if iterclass == 0 : wtype.set( "dop.geo.detail" )
            if iterclass == 1 : wtype.set( "dop.geo.prim" )
            if iterclass == 2 : wtype.set( "dop.geo.point" )
            if iterclass == 3 : wtype.set( "dop.geo.vertex" )
            if iterclass == 4 : wtype.set( "dop.geo.number" )
        if mode == 2 : wtype.set( "dop.pop" )

class wrangle() :
    def __init__( self, parent = None ) :
        self.node = hou.pwd()
        self.mode = self.node.parm("mode").eval()
        self.file = self.node.parm("file").eval()
        self.name = self.file.split("/")[-1]
        self.dir  = self.file.replace( self.name, "" )
        self.snippet = self.node.parm( "snippet%s" % ( int(self.mode) + 1 ) )
        self.path = self.node.path()

    def backup( self ) :
        back = "%sbackup" % self.dir
        if not os.path.exists( back ) :
            os.mkdir( back )
        files = os.listdir( back )
        current = filter(lambda x: x.startswith(self.name), files)
        if len( current ) < HISTORY  :
            pass
        else :
            os.remove( "%s/%s" % ( back, current[-1] ) )
            del(current[-1])
        idx = len(current) - 1
        if idx >= 0 :
            for n in range( len(current) ) :
                file = current[idx]
                num = int( file.split(".")[-2] ) + 1
                newFile = "%s/" % back + ".".join(file.split(".")[:-2]) + ".%0*d.back" % ( PADDING, num )
                os.rename( "%s/%s" % ( back, file ), newFile )
                idx -= 1

        name = "%s/%s.%0*d.back" % ( back, self.name, PADDING, 1 )
        b = open( name, "w" )
        b.write( self.snippet.eval() )
        b.close()

    def updateName( self ) :
        self.file = self.node.parm("file").eval()
        self.name = self.file.split("/")[-1]
        self.dir  = self.file.replace( self.name, "" )

    def save( self ) :
        wrangleType()
        self.updateName()
        if os.path.exists( self.dir ) :
            if self.snippet.eval() :
                self.backup()
            vfl = open( self.file, "w" )
            path = "//PATH = %s" % self.path
            snippet = self.snippet.eval().split("\n")
            if( "//PATH = " in snippet[0] ) :
                snippet = "\n".join( [path] + snippet[1:] )
            else :
                snippet = "\n".join( [path] + snippet )
            vfl.write( snippet )
            vfl.close()

    def load( self ) :
        wrangleType()
        self.updateName()
        if os.path.exists( self.file ) :
            vfl = open( self.file, "r" )
            self.snippet.set( vfl.read() )


    def edit( self ) :
        self.save()
        cmd = "%s %s" % ( EDITOR, self.file )
        subprocess.Popen( cmd )

    def browse( self ) :
        self.save()
        cmd = "explorer /select,%s" % ( self.file.replace("/", "\\") )
        subprocess.Popen( cmd )