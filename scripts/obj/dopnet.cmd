# Default script run when a dopnetwork object is created
# $arg1 is the name of the object to create

\set noalias = 1
if ( "$arg1" != "" ) then
    opparm $arg1 use_dcolor( 0 ) startframe( $FSTART )
    opcolor -c 0 0.8 1 $arg1
endif

opcf $arg1
opadd output output
opcf ..
