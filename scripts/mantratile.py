import sys,mantra, datetime
'''
tile:ncomplete – The number of tiles which have been completed.
tile:ntiles – The total number of tiles in the image.
tile:laptime – The number of seconds taken to render the last tile.
tile:totaltime – The total number of seconds to render since the render began. This does not include time to load the scene, but rather is defined as the time since the first tile began rendering.
tile:coords – The tile bounding box (in pixels).
tile:memory – The amount of RAM in use by mantra.
tile = mantra.property("tile:ncomplete")[0]
'''

def formatTime( s ) :
    H = int( s / 3600 )
    M = int( (s % 3600) / 60 )
    S = round( (s % 3600) % 60, 0 )
    return "%0*d:%0*d:%0*d" % ( 2,H, 2,M, 2,S )

time   = datetime.datetime.now().strftime("%H:%M:%S")
rop    = mantra.property("renderer:name")[0]
ver    = mantra.property("renderer:version")
tile   = mantra.property("tile:ncomplete")[0]
ntiles = mantra.property("tile:ntiles")[0]
lap    = mantra.property("tile:laptime")[0]
total  = mantra.property("tile:totaltime")[0]
mem    = mantra.property("tile:memory")[0] * 0.000001
padzero = len( str( ntiles ) )
prog = float( tile ) / float( ntiles ) * 100.0
sep = "\n==============================================================================\n"
insep = "--------"

if tile == 1 : print "%s[%s] Rendered by %s %s.%s.%s" % ( sep, time, rop, ver[0], ver[1], ver[2] )

print "[%s] %s Tile %0*d / %d %s Tile rendered %s / %s %s memory %.2f Mb %s progress %0*d %%" %\
      ( time, insep, padzero, tile, ntiles, insep, formatTime( lap ), formatTime( total ), insep, mem, insep, 3, prog )

if tile == ntiles : print "%s" % sep