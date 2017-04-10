from datetime import datetime, date
from calendar import monthrange
import os, sys, hou, json

job = '//PROJECTS/Alisa_Film/HoudiniProject'
user = os.path.expandvars("%userprofile%").split('\\')[-1]
users = [ 'a.grabovski', 'a.krylevsky' ]

def writeVisit( scenes = 0, cache = '' ) :
    if user in users :
        now = datetime.now()
        year  = int( datetime.strftime( now, '%Y' ) )
        month = int( datetime.strftime( now, '%m' ) )
        day =   int( datetime.strftime( now, '%d' ) )
        time = datetime.strftime( now, '%H:%M' )
        weekday = datetime.weekday( now )
        monthRange = monthrange( year, month )
        file = job + "/cal/%s.%s.json" % ( month, year )
        if not os.path.exists( file ) :
            dayList = []
            for d in range( monthRange[1] ) :
                dd = date( year, month, d + 1 )
                dayList.append( { 'day'         : d + 1,
                                  'weekday'     : dd.weekday(),
                                  '%s'%users[0] : 0,
                                  '%s'%users[1] : 0,
                                  '%s_scenes'%users[0] : [],
                                  '%s_scenes'%users[1] : [], } )
            with open( file, 'w') as outfile:
                    json.dump( { 'dayList' : dayList }, outfile, indent=4)
        else :
            jsonData = open(file, "r")
            cal = json.load(jsonData)
            cal[ 'dayList' ][ day - 1 ][ user ] = 1
            if( scenes ) :
                s = cal[ 'dayList' ][ day - 1 ][ '%s_scenes'%user ]
                post = '  cache( %s )' % cache if cache else ''
                s.append( '%s - '%time + '/'.join( hou.hipFile.path().split('/')[-2:] ) + post )
                sout = list( set( s ) )
                sout.sort()
                cal[ 'dayList' ][ day - 1 ][ '%s_scenes'%user ] = sout
            with open( file, 'w') as outfile:
                    json.dump( cal, outfile, indent=4)
                
def printMonth( ) :
    now = datetime.now()
    year  = int( datetime.strftime( now, '%Y' ) )
    month = int( datetime.strftime( now, '%m' ) )
    day =   int( datetime.strftime( now, '%d' ) )
    user = os.path.expandvars("%userprofile%").split('\\')[-1]
    request = hou.ui.readMultiInput( 'Please enter data:', ['name', 'year', 'month', 'day'],
                                 initial_contents = ( user, str(year), str(month), str(day) ),
                                 buttons=('OK', 'CANCEL') )
    
    button = request[0]
    if not button :
        user  = request[1][0].strip()
        year  = request[1][1].strip()
        month = request[1][2].strip()
        day   = request[1][3].strip()

        file = job + "/cal/%s.%s.json" % ( month, year )
        jsonData = open(file, "r")
        cal = json.load(jsonData)
        for i,d in enumerate( cal[ 'dayList' ] ) :
            if not day and d['weekday'] < 5 :
                sc = '\n    '.join( d['%s_scenes'%user] ) if d['%s_scenes'%user] else '------------------------------------'
                print '%02d.%s.%s : %s\n    %s\n' % ( i+1, month, year, d[user], sc )
            if day == str( d['day'] ) :
                sc = '\n    '.join( d['%s_scenes'%user] ) if d['%s_scenes'%user] else '------------------------------------'
                print '%02d.%s.%s : %s\n    %s\n' % ( i+1, month, year, d[user], sc )