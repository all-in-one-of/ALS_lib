import hou, os, sys, re
import itertools, shutil, subprocess
from pprint import pprint
import codecs
try :
    from PySide.QtGui import *
    from PySide.QtCore import *
except :
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *

SYNC = "C:/Program Files/FreeFileSync/FreeFileSync.exe"
SYNC_BATCH = "//PROJECTS/Alisa_Film/HoudiniProject/data_sinc.ffs_batch"

def myprint( i ) :
    print i

def nameDigits( name ) :
    d = re.search('\d+$', name)
    if d :
        return str(int(d.group()))
    return ''

def createPath( dir ) :
    if not os.path.exists( dir ) :
        lst = dir.replace("//","##").split("/")
        current = []
        for num, part in enumerate( lst ) :
            current.append(part)
            pathString = "/".join(current).replace("##", "//")
            currentPath =  pathString
            if not os.path.exists( currentPath ) :
                try :
                    os.mkdir( currentPath )
                except :
                    pass

class hipParser() :
    def __init__( self, hip, parent = None ) :
        self.hip = hip
        self.text = ''
        self.globVars = {}
        self.opTypes = {}
        self.readHip()
        self.getHipGlobals()
        #pprint( self.globVars )

    def readHip(self) :
        with codecs.open( self.hip, 'r', 'utf-8', errors = 'ignore' ) as f :
            self.text = f.read()

    def getHipGlobals( self ) :
        varExp = re.compile('set\s-g\s[A-Z]*\s=\s[^\n]*')
        varInits = [ match.group() for match in varExp.finditer( self.text ) ]
        for l in varInits :
            parts = l.split(' ')
            key = '$' + parts[2]
            val = parts[-1]
            self.globVars[key] = val.replace("'", '')

    def getOpTypeParms( self, opType, asset=False ) :
        if not self.opTypes.has_key( opType ) :
            op = 'grabovskiy::%s::\d.\d.\d' % opType if asset else opType
            opExp = re.compile('obj[a-zA-Z0-9/_\.]+\.init\x00type\s=\s%s' % op )

            keyExp      = re.compile( '^[a-zA-Z0-9\._^\s]+' )
            valExp      = re.compile( '\(\t(.*)\t\)' )
            blockExp    = re.compile( '\(\t\[[^\)]*\)$' )
            blockGrpExp = re.compile( '\[[^\]]*\]' )
            brackExp    = re.compile( '[\[|\]]' )

            inits = [ match.group() for match in opExp.finditer( self.text ) ]
            self.opTypes[ opType ] = []
            for init in inits :
                parmDict = {}
                path = init.split('.init\x00')[0]
                name = path.split('/')[-1]
                self.globVars['$OS'] = name
                parmExp = re.compile( '%s.parm\x00\{[^\}]*\n\}' % name )
                opdigExp = re.compile( 'opdigits\([^\)]*\)' )
                findParms = parmExp.search( self.text )
                if not findParms :
                    continue
                parmblock = findParms.group().split('\n')[2:-1]
                for l in parmblock :
                    key = keyExp.search( l ).group().strip()
                    findVal = valExp.search( l )
                    if not findVal :
                        continue
                    val = (''.join( findVal.group().split('\t')[1:-1] )).replace('"','').replace('`','')
                    opdigits = opdigExp.search( val )
                    opdPath = ''
                    if opdigits :
                        opPath = re.search( '[\'|\"][^\'^\"]*[\'|\"]', opdigits.group() ).group()
                        opDepth = len( opPath[1:-1].split('/') )
                        opdPath = path.split('/')[ -opDepth ]
                        val = opdigExp.sub( nameDigits( opdPath ), val )
                    block = blockExp.search( l )
                    if block :
                        val = []
                        items = [ match.group() for match in blockGrpExp.finditer( block.group() ) ]
                        for item in items :
                            x = item[2:-2].split('\t')
                            val.append( [ opdigExp.sub( nameDigits( opdPath ), i ).replace('`','').replace( 'opdigits()', nameDigits( name ) ) for i in x ] )

                    for k, v in self.globVars.iteritems() :
                        if isinstance( val, list ) :
                            for n, prm in enumerate( val ) :
                                if k in prm[1] :
                                    val[n][1] = val[n][1].replace( k, v )
                        else :
                            if k in val :
                                val = val.replace( k, v )

                    parmDict[key] = val
                self.opTypes[ opType ].append( ( path, parmDict ) )
            
        return self.opTypes[ opType ]

    def getOpParmVals( self, opType, parmName, asset=False ) :
        opParmDict = {}
        opsParmsList = self.getOpTypeParms( opType, asset=asset )
        for op in opsParmsList :
            path = op[0]
            parms = op[1]
            val = None
            if parms.has_key( parmName ) :
                p = parms[parmName]
                if isinstance( p, list ) :
                    opParmDict[path] = p[0][1]
                else :
                    opParmDict[path] = p
        return opParmDict

    def findFileDependency( self ) :
        rops   = self.getOpParmVals( 'rop_geometry', 'sopoutput' )
        files  = self.getOpParmVals( 'file', 'file' )
        wedges = self.getOpParmVals( 'wedge_load', 'file', asset=True )
        sumDict = {}
        for i in (rops, files, wedges) :
            if i :
                sumDict.update( i )
        result = list( set( [ v for k, v in sumDict.iteritems() ] ) )
        result = [ c.replace( 'Q:/houdini', hou.expandString( '$JOB' ) ) for c in result ]
        for i, c in enumerate( result ) :
            folder = '/'.join(c.split('/')[:-1])
            if not os.path.exists( folder ) :
                del result[i]
        result.sort()
        [ myprint(i) for i in result ]
        return result

class thread_search(QThread):

    update = Signal()
    
    def __init__(self, files, parent = None):
        super(thread_search, self).__init__(parent)
        self.files = files
        self.caches = []
        
    def run(self):
        print ''.join( [ '=' for i in range( 100 ) ] )
        print '\nFind files dependencies in all scened from all selected subfolders:\n'
        for i, f in enumerate( self.files ) :
            c = hipParser(f).findFileDependency()
            self.caches += c
            self.update.emit()
        self.caches = list( set( self.caches ) )
        self.caches.sort()
        #pprint(self.caches)


class thread_delete(QThread):

    update = Signal()
    
    def __init__(self, scenesDir, mask, parent = None):
        super(thread_delete, self).__init__(parent)
        self.dataDir = scenesDir.replace( 'scenes', 'data' )
        self.mask = re.compile( mask )
        self.file_list = []
        self.dir_list  = []

        
    def setSaveList(self, lst):
        self.file_list = lst
        self.dir_list = [ '/'.join(i.split('/')[:-1]) for i in lst ]
        
    def run(self):
        print ''.join( [ '=' for i in range( 100 ) ] )
        print '\nRemove unused caches from all selected subfolders:\n' 
        Fd = re.compile( '\.f\d+\.' )
        for d, dirs, files in os.walk( self.dataDir ) :
            if not dirs :
                cd = d.replace('\\', '/')
                if cd in self.dir_list :
                    self.update.emit()
                    if 'WEDGE' in cd  and not self.mask.search( cd ) :
                        wmask = re.compile('\.w\d+\.f')
                        fileMasks = []
                        wlist = []
                        for fl in  self.file_list :
                            if wmask.search( fl ) :
                                wlist.append( fl )

                        for file in files :
                            wfind = wmask.search( file )
                            if not wfind :
                                continue
                            if not wfind.group() in ' '.join( wlist ) :
                                curr = re.search( '^(.)+\.w\d+', file ).group()
                                storePath = d.replace( 'data', 'data_store' ).replace('\\', '/')
                                createPath( storePath )
                                shutil.move( '%s/%s' % ( cd, file ), '%s/%s' % ( storePath, file ) )
                                if not curr in fileMasks :
                                    fileMasks.append( curr )
                                    print 'remove: %s/%s' % (d.replace('\\', '/'), Fd.sub('.f$F4.', file))

                    print '-'.join( ['' for i in range(8)] ) + ' ' + cd
                elif not self.mask.search( cd ) :
                    end = d.replace('\\', '/').split('/')[-1]
                    if  not re.match( '_EXPORT', end )\
                        and not re.match( 'hycmd', end )\
                        and not re.match('seq\d+_sh\d+', end)\
                        and not re.match('seq\d+[a-z]_sh\d+', end) :
                            self.update.emit()
                            print 'remove: ' + cd
                            storePath = d.replace( 'data', 'data_store' ).replace('\\', '/')
                            createPath( storePath )
                            for file in files :
                                shutil.move( '%s/%s' % ( cd, file ), '%s/%s' % ( storePath, file ) )
                            os.rmdir( cd )
            
class searchProgress( QProgressBar ) :
    def __init__( self, root, files, mask, parent = None ) :
        super(searchProgress, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize( 400, 50 )
        self.setMaximum(len(files) - 1)
        self.caches = []
        
        self.thread_search = thread_search( files )
        self.thread_search.update.connect(self.plus_one)
        self.thread_search.finished.connect(self.finish_search)
        
        self.thread_delete = thread_delete( root, mask )
        self.thread_delete.update.connect(self.plus_one)
        self.thread_delete.finished.connect(self.finish_delete)
        
    def plus_one( self, ) :
        self.setValue( self.value() + 1 )
    
    def finish_search(self):
        self.caches = self.thread_search.caches
        self.run_delete()
    
    def finish_delete(self):
        print '\nClean process complete!'
        subprocess.Popen( ('"%s" "%s"' % (SYNC, SYNC_BATCH) ).replace('/', '\\') )
        self.close()
    
    def setTitle( self, title ) :
        self.setWindowTitle( title )
        
    def run_search(self):
        self.setWindowTitle('Search actual caches...')
        self.thread_search.start()
    
    def run_delete(self):
        self.setMaximum( len(self.caches) - 1 )
        self.setWindowTitle('Clear cache directory...')
        self.setValue(0)
        self.thread_delete.setSaveList( self.caches )
        self.thread_delete.start()

class thread_repare(QThread) :

    update = Signal()
    
    def __init__(self, dirs, wedges, parent = None):
        super(thread_repare, self).__init__(parent)
        self.dirs = dirs
        self.wedges = wedges
        
    def run(self):
        print ''.join( [ '=' for i in range( 100 ) ] )
        print '\nMove all losted files back to data filder:\n'
        for d in self.dirs :
            cd = d.replace( '\\', '/' )
            store = hou.expandString('$DATA_STORE')
            data = hou.expandString('$HDATA_GLOB')
            dataPath = cd.replace( store, data )
            print dataPath
            createPath( dataPath )
            for f in os.listdir( cd ) :
                self.update.emit()
                print 'repare: %s/%s' % ( dataPath, f )
                shutil.move( '%s/%s' % ( cd, f ), '%s/%s' % ( dataPath, f ) )
            os.rmdir( cd )

        wdirs = []
        for w in self.wedges :
            self.update.emit()
            d = '/'.join( w.split('/')[:-1] )
            name = w.split('/')[-1]
            dataPath = d.replace( 'data_store', 'data' )
            if not d in wdirs :
                createPath( d )
            print 'repare: %s/%s' % ( dataPath, name )
            shutil.move( '%s/%s' % ( d, name ), '%s/%s' % ( dataPath, name ) )
        for d in wdirs :
            if len( os.listdir( d ) ) == 0 :
                print 'clean: %d' % d
                os.rmdir( d )


class repareProgress( QProgressBar ) :
    def __init__( self, rep_dict, parent = None ) :
        super(repareProgress, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize( 400, 50 )
        self.setMaximum( rep_dict['count'] - 1 )

        self.thread_repare = thread_repare( rep_dict['lost_dirs'], rep_dict['lost_wedges'] )
        self.thread_repare.update.connect(self.plus_one)
        self.thread_repare.finished.connect(self.finish_repare)

    def plus_one( self ) :
        self.setValue( self.value() + 1 )
        
    def run_repare(self):
        self.setWindowTitle('Repare losted caches...')
        self.thread_repare.start()
    
    def finish_repare(self):
        print '\nAll caches was repared!'
        subprocess.Popen( ('"%s" "%s"' % (SYNC, SYNC_BATCH) ).replace('/', '\\') )
        self.close()



def lastModScenes( root ) :
    last_files = []
    for d, dirs, files in os.walk( root ) :
        if not 'backup' in d and not 'otls' in d :
            mask_dct = {}
            for f in files :
                if f.split('.')[-1] == 'hip' :
                    mask = d + '/' + f.split('.')[0]
                    mask = re.split( '_[v|V]\d+', mask )[0]
                    
                    mtime = os.path.getmtime(d + '/' + f)
                    if not mask_dct.has_key(mask):
                        mask_dct[mask] = (mtime, f)
                    else:
                        if mask_dct[mask][0] < mtime:
                            mask_dct[mask] = (mtime, f)
            lf = ['%s/%s' % (d, j) for i,j in mask_dct.itervalues()]
            if lf :
                last_files += lf
            #pprint(last_files)
    result = [ i.replace('\\', '/') for i in list( set( last_files ) )]
    result.sort()
    return result

def analize( dir, mask ) :
    question = hou.ui.displayMessage( '%s directory will be scanned and cleaned.\n Are you sure?' % dir, buttons = ( 'Ok', 'Cancel' ) )
    if not question :
        files = lastModScenes( dir )
        #pprint( files )
        hou.session.prog = searchProgress( dir, files, mask )
        hou.session.prog.show()
        hou.session.prog.run_search()

def searchLostCaches( ) :
    lost_dir = []
    lost_wedges = []
    filecount = 0
    weExp = re.compile( '\.w\d+\.f' )
    for n in hou.node('/obj').allSubChildren() :
        if n.type().name() == 'file' :
            file = n.parm('file').eval()
            path = '/'.join( file.split('/')[:-1] )
            hdata = hou.expandString( '$HDATA_GLOB' )
            data_store = hou.expandString( '$DATA_STORE' )
            store_path = path
            if hdata in path : 
                store_path = path.replace( hdata, data_store )
            else :
                store_path = path.replace( 'data', 'data_store' )
                
            if not os.path.exists( path ) and os.path.exists( store_path ) :
                lost_dir.append( store_path )
                filecount += len( [i for i in os.listdir( store_path ) ] )
                    
            if 'WEDGE' in path :
                pattern = weExp.search( file ).group()
                try:
                    fileList = os.listdir( store_path )
                except(WindowsError):
                    fileList = []
                for f in fileList :
                    if pattern in f :
                        lost_wedges.append( store_path + '/' + f )
                        filecount += 1
    return( { 'lost_dirs' : lost_dir, 'lost_wedges' : lost_wedges, 'count' : filecount } )

def repare() :
    question = hou.ui.displayMessage( 'All losted files will be moved back from storage.\n Are you sure?', buttons = ( 'Ok', 'Cancel' ) )
    if not question :
        lost = searchLostCaches()
        hou.session.repr = repareProgress( lost )
        hou.session.repr.show()
        hou.session.repr.run_repare()

if __name__ == '__main__':
    scenes = 'D:/HoudiniProjects/scenes'

    '''
    import hou
    from pprint import pprint
    import dataCleaner2
    reload( dataCleaner2 )

    scenes = '%s/scenes/seq006c/seq006c_sh011' % hou.expandString( '$JOB' )
    dataCleaner2.analize( scenes )
    '''