import hou, re

SOPTEMPLATEFILE = hou.expandString("$JOB") + "/scripts/python/sopvextemplates.vfl"
DOPTEMPLATEFILE = hou.expandString("$JOB") + "/scripts/python/dopvextemplates.vfl"

def replaceSimbols() :
    list = [ "$", "Dollar", "^", "Up Arrow", "?", "Question", "#", "Hash",  ]
    return list

def clearSnippet( node ) :
    mode = node.parm("mode").eval()
    snippet = node.parm( "snippet%s" % ( int(mode) + 1 ) )
    snippet.set("")

def _remove_comments(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ' '
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
        )
    return re.sub(pattern, replacer, text)

def createSpareParms( node ):
    mode = node.parm( "mode" ).eval()
    clear = node.parm( "clearchans" ).eval()
    parmname ="snippet%s" % ( int(mode) + 1 )
    code = node.parm(parmname).unexpandedString()

    code = _remove_comments(code)
    chcalls = [ 'ch', 'chf', 'chi', 'chv', 'chp', 'ch3', 'ch4', 'chramp', 'chs' ]

    ch_to_size = {
        'ch':1,
        'chf':1,
        'chi':1,
        'chv':3,
        'chp':4,
        'ch3':9,
        'ch4':16,
        'chramp':1,
        'chs':1 
        }

    chmatches = []
    createdParms = []

    for chcall in chcalls:
        matches = re.findall( chcall + ' *\( *"(\w+)" *[\),]', code )
        matches += re.findall( chcall + " *\( *'(\w+)' *[\),]", code )
        for match in matches :
            chmatches.append(match)
        
        for match in matches:
            if (node.parm(match) is None) and (node.parmTuple(match) is None):
                # No match, add the parameter.
                template = None
                tuplesize = ch_to_size[chcall]
                label = match.title().replace('_', ' ')
                if chcall == 'chramp':
                    # Unfortunately we can't tell colour from scalar ramps here.
                    template = hou.RampParmTemplate(match, label, hou.rampParmType.Float)
                elif chcall == 'chs':
                    template = hou.StringParmTemplate(match, label, tuplesize)
                elif chcall == 'chi':
                    template = hou.IntParmTemplate(match, label, tuplesize)
                else:
                    # Range is less meaningfull for tuples, so set it nicely for scalars.
                    template = hou.FloatParmTemplate(match, label, tuplesize, min = 0, max = 1)
                if not node.parmTemplateGroup().findFolder( "Channels" ) :
                    node.addSpareParmTuple( hou.FolderParmTemplate( "channels", "Channels", folder_type=hou.folderType.Simple ) )
                node.addSpareParmTuple(template, in_folder = ("Channels",))
                if template.name() == "fps" :
                    node.parm("fps").setExpression("$FPS")

    if clear :
        folder = node.parmTemplateGroup().findFolder( "Channels" )
        if folder :
            for parmtemplate in folder.parmTemplates() :
                if not parmtemplate.name() in chmatches :
                    node.removeSpareParmTuple( parmtemplate )
    

    code = node.parm(parmname).unexpandedString()
    node.parm(parmname).set(code)

class wrangle() :
    def __init__( self, parent = None ) :
        self.node = hou.pwd()
        self.mode = self.node.parm("mode").eval()
        self.code = self.node.parm( "snippet%s" % ( int(self.mode) + 1 ) ).eval()
        self.replace = self.node.parm("replace").eval()
        self.menutype = self.node.parm("menutype").eval()
        self.snippets = {}

    def arraysInit( self ) :
        self.snippets[ "Append Item To Array" ] = \
        'append( array, value );'

        self.snippets[ "Insert Item into An Array" ] = \
        'insert( array, idx, value );'

        self.snippets[ "Sort Array" ] = \
        'int sorted = sort( array );'

        self.snippets[ "Push Item in Array" ] = \
        'push( array, item );'

        self.snippets[ "Remove Index" ] = \
        'removeindex( array, idx );'

        self.snippets[ "Is Valid Index" ] = \
        'isvalidindex( array, idx );'

        self.snippets[ "Reorder Array" ] = \
        'reorder( array, newidxorder );//newidxorder is int array'

        self.snippets[ "Slice Array (Or String)" ] = \
        'slice( array, start, end );'

        self.snippets[ "Remove And Return Last Element" ] = \
        'pop( array );'

    def attributesInit( self ) :
        self.snippets[ "Attribute Point" ] = \
        'point(1, "attr", ptnum);'

        self.snippets[ "Attribute Primitive" ] = \
        'prim(1, "attr", primnum);'

        self.snippets[ "Attribute Vertex" ] = \
        'vertex(1, "attr", vtxnum);'

        self.snippets[ "Attribute Detail" ] = \
        'detail(1, "attr", 0);'
        
        self.snippets[ "Find By Point Attribute" ] = \
        'findattribval( 0, "point", "id", i@id );'
        
        self.snippets[ "Find By Primitive Attribute" ] = \
        'findattribval( 0, "primitive", "name", s@name );'
        
        self.snippets[ "Has Point Attribute" ] = \
        'haspointattrib( 0, "Cd" );'
        
        self.snippets[ "Has Pprimitive Attribute" ] = \
        'hasprimattrib( 0, "Cd" );'
        
        self.snippets[ "Has Vertex Attribute" ] = \
        'hasvertexattrib( 0, "N" );'
        
        self.snippets[ "Has Detail Attribute" ] = \
        'hasdetailattrib( 0, "attr" );'
        
        self.snippets[ "Id To Point Number" ] = \
        'idtopoint( 1, @id );'
        
        self.snippets[ "Name To Point Number" ] = \
        'nametopoint( 1, s@name );'
        
        self.snippets[ "Set Point Attribute" ] = \
        'setpointattrib( 0, "Cd", color );'
        
        self.snippets[ "Set Primitive Attribute" ] = \
        'setprimattrib( 0, "Cd", @ptnum, color );'
        
        self.snippets[ "Set Vertex Attribute" ] = \
        'setvertexattrib( 0, "N", @vtxnum, normal );'
        
        self.snippets[ "Set Detail Attribute" ] = \
        'setdetailattrib( 0, "attr", value );'
        
        self.snippets[ "Set Point Attribute" ] = \
        'setpointattrib( 0, "Cd", @primnum, color );'
        
        self.snippets[ "Unique Value from an Attribute (int, string)" ] = \
        'uniqueval( 0, "point", "name", wich);//Which one of the unique values to return. Use nuniqueval to determine how many matched'

    def conversionInit( self ) :
        self.snippets[ "String to Float" ] = \
        'atof( string );'

        self.snippets[ "String to Integer" ] = \
        'atoi( string );'

        self.snippets[ "Radians to degrees" ] = \
        'degrees( angle );'

        self.snippets[ "Euler Angle to Quaternion" ] = \
        'eulertoquaternion( rotvector, order ); //Specify the rotation order with the order integer. Use the constants defined in $HH/vex/include/math.h (for example, XFORM_XYZ)'

        self.snippets[ "HSV to RGB" ] = \
        'hsvtorgb( color );'

        self.snippets[ "RGB to HSV" ] = \
        'rgbtohsv( color );'

        self.snippets[ "Quaternion to Matrix3" ] = \
        'qconvert( opient );'

        self.snippets[ "RGB to XYZ" ] = \
        'rgbtoxyz( color );'

        self.snippets[ "XYZ to RGB" ] = \
        'xyztorgb( @P );'

    def geometryInit( self ) :
        self.snippets[ "Add Point" ] = \
        'addpoint( 0, position );'

        self.snippets[ "Add Primitive" ] = \
        'addprim( 0, "polyline" );'

        self.snippets[ "Add Vertex" ] = \
        'addvertex( 0, primnum, ptnum );'

        self.snippets[ "Remove Point" ] = \
        'removepoint( 0, @ptnum );'
        
        self.snippets[ "Remove Primitive" ] = \
        'removeprim( 0, @primnum, 1 );'
        
        self.snippets[ "Get BBox" ] = \
        'vector min, max;\ngetbbox( 0, min, max );'
        
        self.snippets[ "Get Relative BBox" ] = \
        'relbbox( 0, @P );'
        
        self.snippets[ "Half-edge From Given Point" ] = \
        'pointhedge( 0, @ptnum );'
        
        self.snippets[ "Half-edge From Two Points" ] = \
        'pointhedge( 0, srcpoint, dstpoint );'
        
        self.snippets[ "Half-edge From Given Primitive" ] = \
        'primhedge( 0, @primnum );'
        
        self.snippets[ "Half-edge Equivalent Count" ] = \
        'hedge_equivcount( 0, hedgenum );'
        
        self.snippets[ "Half-edge next Equivalent" ] = \
        'hedge_nextequiv( 0, hedgenum );'
        
        self.snippets[ "Half-edge to Primitive" ] = \
        'hedge_prim( 0, hedgenum );'
        
        self.snippets[ "Half-edge Source Point" ] = \
        'hedge_srcpoint( 0, hedgenum );'
        
        self.snippets[ "Half-edge Destination Point" ] = \
        'hedge_dstpoint( 0, hedgenum );'
        
        self.snippets[ "Half-edge Previous in Polygon" ] = \
        'hedge_prev( 0, hedgenum );'
        
        self.snippets[ "Half-edge Next in Polygon" ] = \
        'hedge_next( 0, hedgenum );'
        
        self.snippets[ "Intersect" ] = \
        'vector pp, uv;\nint inter = intersect( 0, @P + dir * ch("bias"), dir, pp, uv );'
        
        self.snippets[ "Intersect All" ] = \
        'int prim[];\nvector pp[], uvw[];\nint inter = intersect_all( 0, @P + dir * ch("bias"), dir, pp, prim, uvw );'
        
        self.snippets[ "Near Position (Closest Point Vector)" ] = \
        'minpos( 1, @P ); //may use maxdist'
        
        self.snippets[ "Near Point (Closest Point Number)" ] = \
        'nearpoint( 1, @P ); //may use maxdist'
        
        self.snippets[ "Neighbour Count" ] = \
        'neighbourcount( 0, @ptnum );'
        
        self.snippets[ "Neighbour Point" ] = \
        'neighbour( 0, @ptnum, num );'
        
        self.snippets[ "Primitives From Point Number" ] = \
        'pointprims( 0, @ptnum ); //Array'
        
        self.snippets[ "Linear Vertex From Point Number" ] = \
        'pointvertex( 0, @ptnum );'
        
        self.snippets[ "Point From Primitive Number" ] = \
        'primpoint( 0, @primnum, vertex );'
        
        self.snippets[ "Set Primitive Vertex (Rewires in a Different Point)" ] = \
        'setprimvertex( 0, @primnum, vtxnum, ptnum );'
        
        self.snippets[ "Vertex Previous" ] = \
        'vertexprev( 0, @vtxnum );'
        
        self.snippets[ "Vertex Next" ] = \
        'vertexnext( 0, @vtxnum );'
        
        self.snippets[ "Vertex Index in Primitive" ] = \
        'vertexprimindex( 0, @vtxnum );'
        
        self.snippets[ "Linear Vertex from Primitive/Vertex" ] = \
        'vertexindex( 0, @primnum, vtxnum );'
        
        self.snippets[ "Primitive from Vertex" ] = \
        'vertexprim( 0, @vtxnum );'
        
        self.snippets[ "XYZ Distance" ] = \
        'int prim;\nvector uv;\nfloat dist = xyzdist( 1, @P, prim, uv );'
        
        self.snippets[ "Prim Normal" ] = \
        'vector nn = prim_normal( 1, prim, uv[0], uv[1] );'
        
        self.snippets[ "Prim UV" ] = \
        'primuv( 1, "attr", prim, uv );'

    def groupsInit( self ) :
        
        self.snippets[ "Expand Point Group" ] = \
        'expandpointgroup( 0, "groupname" ); //return array'
        
        self.snippets[ "Expand Point Group" ] = \
        'expandprimgroup( 0, "groupname" ); //return array'
        
        self.snippets[ "In Point Group" ] = \
        'inpointgroup(0, "groupname", @ptnum);'
        
        self.snippets[ "In Primitive Group" ] = \
        'inprimgroup(0, "groupname", @primnum);'
        
        self.snippets[ "Number of Points in Group" ] = \
        'npointsgroup( 0, "groupname" );'
        
        self.snippets[ "Number of Primitives in Group" ] = \
        'nprimitivesgroup( 0, "groupname" );'
        
        self.snippets[ "Set Point Group" ] = \
        'setpointgroup( 0, "groupname", @ptnum, 1 );//mode = set, add, min, max, mult, toggle'
        
        self.snippets[ "Set Primitive Group" ] = \
        'setprimgroup( 0, "groupname", @primnum, 1 );//mode = set, add, min, max, mult, toggle'


    def includesInit( self ) :    
        self.snippets[ "My general functions" ] = \
        '#include <grabovskiy_general_funcs.h>'


    def intrinsicsInit( self ) :
        self.snippets[ "Packed Full Transform" ] = \
        'primintrinsic( 0, "packedfulltransform", @primnum );'

        self.snippets[ "Packed Transform" ] = \
        'primintrinsic( 0, "transform", @primnum );'

        self.snippets[ "Packed Pivot" ] = \
        'primintrinsic( 0, "pivot", @primnum );'

        self.snippets[ "Set Primitive Intrinsic" ] = \
        'setprimintrinsic( 0, "transform", @primnum, matrix3 );'

        self.snippets[ "Detail Intrinsic" ] = \
        'detailintrinsic( 0, "detailattributes" );'

    def loopsInit( self ) :
        self.snippets[ "For Loop" ] = \
        'for( int i = 0; i < condition; i++ ){\n    \n\n}'

        self.snippets[ "While Loop" ] = \
        'int iteration = 0;\nwhile( iteration < 10 ){\n    \n    iteration++;\n}'

        self.snippets[ "Do While Loop" ] = \
        'int iteration = 0;\ndo{\n    iteration++;\n\n}while( iteration < 10 );'

        self.snippets[ "Foreach Loop" ] = \
        'string names[] = { "name0", "name1", "name2" };\nforeach( int pr; string name; names )'
        self.snippets[ "Foreach Loop" ] += '{\n    printf( "%d - %s\\n", pr, name );\n\n}'

    def mathInit( self ) :
        self.snippets[ "Blackbody Color From Temperature" ] = \
        'blackbody( temperature, luminance );'

        self.snippets[ "Crack Transform" ] = \
        'cracktransform( trs, xyz, c, @P, xform );'

        self.snippets[ "Rotate Vector A onto the Vector B" ] = \
        'dihedral( A, B ); //matrix3 or quaternion'

        self.snippets[ "Fresnel" ] = \
        'float kr, kt;\nfresnel( ray, v@N, eta, kr, kt );'

        self.snippets[ "Instance Transform Matrix" ] = \
        'instance( @P, @N, vscale, protate, porient, vpivot );//Have more simple versions'

        self.snippets[ "Lookat Transform Matrix" ] = \
        'lookat( vfrom, vto, vu );//Have more simple versions'

        self.snippets[ "Make Basis From One Vector" ] = \
        'vector xaxis, yaxis;\nmakebasis( xaxis, yaxis, zaxis );'

        self.snippets[ "Make Transformation Matrix" ] = \
        'maketransform( trs, xyz, t, r, s );'

        self.snippets[ "Closest Distance to the Finite line" ] = \
        'ptlined( P0, P1, @P );'

        self.snippets[ "Angle Between Two Quaternions" ] = \
        'qdistance( q1, q2 );'

        self.snippets[ "Rotate Vector By Quaternion" ] = \
        'qrotate( orient, v@N );'

        self.snippets[ "Make Quaternion" ] = \
        'quaternion(angle, axis); //Have other versions for matrix3'

        self.snippets[ "Blend Two Quaternions" ] = \
        'slerp( q1, q2, bias );'

        self.snippets[ "Translation Matrix" ] = \
        'matrix trans = ident();\ntranslate( trans, dir * ch("translate") );'

        self.snippets[ "Operator Transform Matrix" ] = \
        'optransform(pathToObject);'

    def noiseInit( self ) :
        self.snippets[ "ANoise" ] = \
        'anoise( @P * ch("frecuency") + chv("offset"), chi("turbulence"), ch("rough"), ch("atten") ) * ch("amplitude");'

        self.snippets[ "Curl Noise" ] = \
        'curlnoise( @P * ch("frecuency") + chv("offset") ) * ch("amplitude");'

        self.snippets[ "Flow Noise" ] = \
        'flownoise( @P * ch("frecuency") + chv("offset"), ch("flow") ) * ch("amplitude");'

        self.snippets[ "Perlin Noise" ] = \
        'noise( @P * ch("frecuency") + chv("offset") ) * ch("amplitude");'

        self.snippets[ "Simplex Noise" ] = \
        'xnoise( @P * ch("frecuency") + chv("offset") ) * ch("amplitude");'

        self.snippets[ "ONoise" ] = \
        'onoise( @P * ch("frecuency") + chv("offset"), chi("turbulence"), ch("rough"), ch("atten") ) * ch("amplitude");'

        self.snippets[ "SNoise" ] = \
        'snoise( @P * ch("frecuency") + chv("offset"), chi("turbulence"), ch("rough"), ch("atten") ) * ch("amplitude");'

        self.snippets[ "Voronoy Noise" ] = \
        'int seed;\nfloat f1, f2;\nvector pos1, pos2;\nvnoise( @P * ch("frecuency") + chv("offset"), ch("jitter"), seed, f1, f2, pos1, pos2 );'

        self.snippets[ "Worley Noise" ] = \
        'int seed;\nfloat f1, f2, f3, f4;\nwnoise( @P * ch("frecuency") + chv("offset"), seed, f1, f2, f3, f4 );'


    def pcInit( self ) :
        self.snippets[ "PC Open" ] = \
        'int handle = pcopen( 0, "P", @P, ch("rad"), chi("npoints") );'

        self.snippets[ "PC Filter" ] = \
        'pcfilter( handle, "" );\n'

        self.snippets[ "PC Iterate (While Loop)" ] = \
        'while( pciterate( handle ) ){\n    \n\n}'

        self.snippets[ "PC Num Found (If Condition)" ] = \
        'if( pcnumfound( handle ) > 0 ){\n    \n\n}'

        self.snippets[ "PC Import" ] = \
        'pcimport( handle, "", variable );'

        self.snippets[ "PC Import (Number)" ] = \
        'pcimport( handle, "point.number", num );'

        self.snippets[ "PC Import (Distance)" ] = \
        'pcimport( handle, "point.distance", dist );'

        self.snippets[ "PC Fathest (Distance)" ] = \
        'pcfathest( handle );'

        self.snippets[ "PC Find (Array of points)" ] = \
        'pcfind( 0, "P", @P, ch("rad"), chi("npoints") );'

        self.snippets[ "PC Find Radius (Array of points)" ] = \
        'pcfind_radius( 0, "P", "pscale", ch("find_pscale"), @P, ch("rad"), chi("npoints") );'

        self.snippets[ "PC Generate" ] = \
        'pcgenerate( "filename", npoints );'

        self.snippets[ "PC Export" ] = \
        'pcgenerate( "filename", "attr", value );'

        self.snippets[ "PC Write Data to File" ] = \
        'pcwrite( "filename", "P", pos );//Can write more then one attribute'

        self.snippets[ "PG Find (Array of points)" ] = \
        'pgfind( 0, "P", @P, ch("rad"), chi("npoints"), ch("divsize") );'

    def samplingInit( self ) :
        self.snippets[ "Sample Simple Arc (vec2)" ] = \
        'sample_circle_arc( center, ch("maxangle"), fu );'

        self.snippets[ "Sample Circle Edge Uniform (vec2)" ] = \
        'sample_circle_edge_uniform( fu );'

        self.snippets[ "Sample Circle Uniform (vec2)" ] = \
        'sample_circle_uniform( v2u );'

        self.snippets[ "Sample Direction Cone (vec3)" ] = \
        'sample_direction_cone( center, ch("maxangle"), v2u );'

        self.snippets[ "Sample Direction Uniform (vec3)" ] = \
        'sample_direction_uniform( v2u );'

        self.snippets[ "Sample Hemisphere (vec3)" ] = \
        'sample_hemisphere( v2u );'

        self.snippets[ "Sample Hipersphere Cone (vec4)" ] = \
        'sample_hypersphere_cone( v4center, ch("maxangle"), v4u );'

        self.snippets[ "Sample Orientation Cone (vec4)" ] = \
        'sample_orientation_cone( v4center, ch("maxangle"), v3u );'

        self.snippets[ "Sample Orientation Uniform (vec4)" ] = \
        'sample_orientation_uniform( v4u );'

        self.snippets[ "Sample Sphere Cone (vec3)" ] = \
        'sample_sphere_cone( v3center, ch("maxangle"), v3u );'

        self.snippets[ "Sample Sphere Uniform (vec3)" ] = \
        'sample_sphere_uniform( v3u );'

        self.snippets[ "Sample Disk (void vec2)" ] = \
        'float x, y;\nsampledisk( x, y, sx, sy );'

    def stringsInit( self ) :
        self.snippets[ "String Ends With" ] = \
        'endswith( "string", "end" );'

        self.snippets[ "Find String in Array" ] = \
        'find( array, "search" );'

        self.snippets[ "Is Alpha" ] = \
        'isalpha( "string" );'

        self.snippets[ "Is Digit" ] = \
        'isdigit( "string" );'

        self.snippets[ "Join" ] = \
        'join( str_array, "_" );'

        self.snippets[ "Strip" ] = \
        'lstrip( "string" );//can specified space simbol'

        self.snippets[ "Match" ] = \
        'match( "pattern", "string" );'

        self.snippets[ "Last Sequence of Digits" ] = \
        'opdigits( "string1" );'

        self.snippets[ "Last Sequence of Digits" ] = \
        'opdigits( "string1" );'

        self.snippets[ "Regular Find" ] = \
        're_find( "regex", "string" );//More variant in help'

        self.snippets[ "Regular Find All" ] = \
        're_findall( "regex", "string" );//More variant in help'

        self.snippets[ "Regular Match" ] = \
        're_match( "regex", "string" );'

        self.snippets[ "Regular Replace" ] = \
        're_replace( "find", "replace", "string" );'

        self.snippets[ "Regular Split" ] = \
        're_split( "regex", "string" );'

        self.snippets[ "Relative Path From Two Full" ] = \
        'relativepath( src, dest );'

        self.snippets[ "Split" ] = \
        'split( "regex", "string" );'

        self.snippets[ "Split Path to Dir and Name" ] = \
        'string dir, name;\nsplitpath( "fullpath", dir, name );'

        self.snippets[ "Format String" ] = \
        'sprintf( "%d", 123 );'

        self.snippets[ "String Starts With" ] = \
        'startswith( "string", "start" );'

        self.snippets[ "String Length" ] = \
        'strlen( "string" );'

        self.snippets[ "Title Case" ] = \
        'titlecase( "string" );'

        self.snippets[ "To Upper" ] = \
        'toupper( "string" );'

        self.snippets[ "To Lower" ] = \
        'tolower( "string" );'

    def utilitiesInit( self ) :
        self.snippets[ "Custom Error" ] = \
        'error( "string format" );'

        self.snippets[ "Custom Warning" ] = \
        'warning( "string format" );'

        self.snippets[ "Print Once" ] = \
        'print_once( "Message" );'

    def templatesInit( self, sourcefile ) :
        start = "#START"
        end   = "#END"
        templateFile = open( sourcefile, "r" )
        templates = templateFile.read().strip().split( start )
        for template in templates :
            if template :
                code = template.split( end )[0]
                lines = code.split("\n")
                itemName = ""
                for line in lines :
                    if line : 
                        itemName = line.replace("/","")
                        break
                code = code.split("\n")
                self.snippets[itemName] = "\n".join( code[2:] )

    def volumesInit( self ) :
        self.snippets[ "Volume Gradient" ] = \
        'volumegradient( 0, "density", @P);'

        self.snippets[ "Volume Index (Value of a specific voxel)" ] = \
        'volumeindex(0, "density", voxel); //voxel is a vector from voxel numbers in third dimensions'

        self.snippets[ "Volume Index Vector (Value of a specific voxel)" ] = \
        'volumeindexv(0, "density", voxel); //voxel is a vector from voxel numbers in third dimensions'

        self.snippets[ "Volume Index Position" ] = \
        'volumeindexpos(0, "density", voxel); //voxel is a vector from voxel numbers in third dimensions'

        self.snippets[ "Volume Position to Index" ] = \
        'volumepostoindex(0, "density", @P);'

        self.snippets[ "Volume Resolution" ] = \
        'volumeres(0, "density");'

        self.snippets[ "Volume Sample (Float)" ] = \
        'volumesample( 1, "surface", @P );'

        self.snippets[ "Volume Sample (Vector)" ] = \
        'volumesamplev( 1, "vel", @P );'


def buildmenu() :
    node = wrangle()

    if node.menutype == "arrays" :
        node.arraysInit()

    if node.menutype == "attributes" :
        node.attributesInit()

    if node.menutype == "convert" :
        node.conversionInit()

    if node.menutype == "geometry" :
        node.geometryInit()

    if node.menutype == "groups" :
        node.groupsInit()

    if node.menutype == "includes" :
        node.includesInit()

    if node.menutype == "intrinsics" :
        node.intrinsicsInit()

    if node.menutype == "loops" :
        node.loopsInit()

    if node.menutype == "math" :
        node.mathInit()

    if node.menutype == "noise" :
        node.noiseInit()

    if node.menutype == "pcfuncs" :
        node.pcInit()

    if node.menutype == "sampling" :
        node.samplingInit()

    if node.menutype == "strings" :
        node.stringsInit()

    if node.menutype == "soptemplates" :
        node.templatesInit( SOPTEMPLATEFILE )

    if node.menutype == "doptemplates" :
        node.templatesInit( DOPTEMPLATEFILE )

    if node.menutype == "utilities" :
        node.utilitiesInit()

    if node.menutype == "volumes" :
        node.volumesInit()

    menu = []
    names = list( node.snippets.keys() )
    names.sort()

    for name in names :
        val = node.snippets[name]
        code = node.code
        if node.replace in code :
            code = code.replace( node.replace, val )
        else :
            code += val
        menu += [code] + [name]

    return menu