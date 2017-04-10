# Default script run when a geometry object is created
# $arg1 is the name of the object to create

\set noalias = 1
if ( "$arg1" != "" ) then
    opparm $arg1 use_dcolor( 0 )
    opproperty -f -F Render $arg1 mantra default_geometry
#   Lock the scales if you want to play it more safely:
#   chlock $arg1 +s?

    opcf $arg1
    opadd -n file file1
    opparm file1 file default.bgeo
    oplocate -x 0 -y 0 file1
    opset -d on -r on -t off -l off -s off -u off file1
    opcf ..
    opcolor -c 0 0.4 0 $arg1
endif
