# Automatically generated script: Wednesday May 24, 15:00
\set noalias = 1
#
#  Creation script for clean operator
#

if ( "$arg1" == "" ) then
    echo This script is intended as a creation script
    exit
endif

opparm $arg1 objname1 ( "*" )
opparm $arg1 startframe( $FSTART )
opcolor -c 0 0.8 1 $arg1

opcf $arg1
opadd output output
opcf ..
