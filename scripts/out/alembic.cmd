# Default script run when a geometry object is created
# $arg1 is the name of the object to create

\set noalias = 1
if ( "$arg1" != "" ) then
    # Add render scripts
    opproperty -F "Scripts" $arg1 events prerender
    opproperty -F "Scripts" $arg1 events preframe
    opproperty -F "Scripts" $arg1 events postframe
    opproperty -F "Scripts" $arg1 events postrender
    # Set custom parms
    opparm $arg1 filename "\$MCACHE/\$OS.abc"
endif
