# Default script run when a light object is created.
# $arg1 is the name of the object to create

\set noalias = 1
if ( "$arg1" != "" ) then
    opproperty -f -F Render $arg1 mantra default_light

    opcf $arg1

    # Node point_cone_switch
    opadd -n switch point_cone_switch
    oplocate -x -0.594989 -y -6.38178 point_cone_switch
    chadd point_cone_switch input
    chkey -t $TSTART -v 0 -m 0 -a 1 -F 'if (strcmp(propertys("../light_type", 'off'), "on") == 0, 1, 0)' point_cone_switch/input
    opparm point_cone_switch input ( input )
    chlock point_cone_switch -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off point_cone_switch

    # Node final_light
    opadd -n merge final_light
    oplocate -x 3.40277 -y -9.37843 final_light
    opparm final_light
    chlock final_light -*
    opset -d on -r on -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off final_light

    # Node areashape_switch
    opadd -n switch areashape_switch
    oplocate -x 8.37629 -y -5.34795 areashape_switch
    chadd areashape_switch input
    chkey -t $TSTART -v 0 -m 0 -a 1 -F 'if(strcmp(propertys("../areashape", 'point'), "point") == 0, 0, if(strcmp(propertys("../areashape", 'point'), "line") == 0, 1, if(strcmp(propertys("../areashape", 'point'), "grid") == 0, 2, if(strcmp(propertys("../areashape", 'point'), "disk") == 0, 3, if(strcmp(propertys("../areashape", 'point'), "sphere") == 0, 4, if(strcmp(propertys("../areashape", 'point'), "tube") == 0, 5, 0))))))' areashape_switch/input
    opparm areashape_switch input ( input )
    chlock areashape_switch -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off areashape_switch

    # Node null1
    opadd -n null null1
    oplocate -x 7.79277 -y 2.49608 null1
    opparm null1
    chlock null1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off null1

    # Node line1
    opadd -n line line1
    oplocate -x 9.36699 -y 1.64577 line1
    opparm line1 type ( poly ) origin ( -0.5 0 0 ) dir ( 1 0 0 ) dist ( 1 ) points ( 2 ) order ( 4 )
    chlock line1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off line1

    # Node grid1
    opadd -n grid grid1
    oplocate -x 10.3727 -y 0.641406 grid1
    opparm grid1 type ( poly ) surftype ( quads ) orient ( xy ) size ( 1 1 ) t ( 0 0 0 ) rows ( 2 ) cols ( 2 ) orderu ( 4 ) orderv ( 4 ) interpu ( on ) interpv ( on )
    chlock grid1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off grid1

    # Node circle1
    opadd -n circle circle1
    oplocate -x 11.377 -y -0.362946 circle1
    opparm circle1 type ( nurbs ) orient ( xy ) rad ( 0.5 0.5 ) t ( 0 0 0 ) order ( 3 ) divs ( 10 ) arc ( closed ) angle ( 0 360 ) imperfect ( off )
    chlock circle1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off circle1

    # Node sphere1
    opadd -n sphere sphere1
    oplocate -x 12.4013 -y -1.38074 sphere1
    opparm sphere1 type ( nurbs ) surftype ( quads ) rad ( 0.5 0.5 0.5 ) t ( 0 0 0 ) orient ( y ) freq ( 1 ) rows ( 10 ) cols ( 10 ) orderu ( 3 ) orderv ( 3 ) imperfect ( off ) upole ( off ) accurate ( off )
    chlock sphere1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off sphere1

    # Node tube1
    opadd -n tube tube1
    oplocate -x 13.3437 -y -2.38422 tube1
    opparm tube1 stdswitcher ( 1 1 ) type ( nurbs ) surftype ( quads ) orient ( x ) t ( 0 0 0 ) rad ( 0.5 0.5 ) height ( 1 ) imperfect ( off ) rows ( 2 ) cols ( 10 ) orderu ( 3 ) orderv ( 2 ) cap ( off )
    chlock tube1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off tube1

    # Node areasize2
    opadd -n xform areasize2
    oplocate -x 8.36903 -y -7.34429 areasize2
    chadd areasize2 scale
    chkey -t $TSTART -v 1 -m 0 -a 1 -F 'property("../areasize", 1)' areasize2/scale
    opparm areasize2 group ( "" ) grouptype ( guess ) xOrd ( srt ) rOrd ( xyz ) t ( 0 0 0 ) r ( 0 0 0 ) s ( 1 1 1 ) p ( 0 0 0 ) scale ( scale ) grppivot ( off ) updatenmls ( on ) vlength ( on )
    chlock areasize2 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off areasize2

    # Node areasize1
    opadd -n xform areasize1
    oplocate -x -1.60681 -y -0.365115 areasize1
    chadd areasize1 scale
    chkey -t $TSTART -v 1 -m 0 -a 1 -F 'ch("../areasize2/scale")/8' areasize1/scale
    opparm areasize1 group ( "" ) grouptype ( guess ) xOrd ( srt ) rOrd ( xyz ) t ( 0 0 0 ) r ( 0 0 0 ) s ( 1 1 1 ) p ( 0 0 0 ) scale ( scale ) grppivot ( off ) updatenmls ( on ) vlength ( on )
    chlock areasize1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off areasize1

    # Node cone_light
    opadd -n subnet cone_light
    oplocate -x 3.38881 -y -1.38623 cone_light
    opparm cone_light label1 ( 'Sub-Network Input #1' ) label2 ( 'Sub-Network Input #2' ) label3 ( 'Sub-Network Input #3' ) label4 ( 'Sub-Network Input #4' )
    chlock cone_light -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off cone_light
    opcf cone_light

    # Node tube1
    opadd -n tube tube1
    oplocate -x 2.36156 -y 3.62617 tube1
    chadd tube1 tz
    chkey -t $TSTART -v 0 -m 0 -a 1 -F '-ch("height")*.5' tube1/tz
    chadd tube1 rad2
    chkey -t $TSTART -v 0 -m 0 -a 1 -F 'property("../../focus", 10)*sin(property("../../coneangle", 45)/2)' tube1/rad2
    chadd tube1 height
    chkey -t $TSTART -v 0.5 -m 0 -a 1 -F 'property("../../focus", 10) * cos(property("../../coneangle", 45)/2)' tube1/height
    opparm tube1 stdswitcher ( 1 1 ) type ( nurbs ) surftype ( quads ) orient ( z ) t ( 0 0 tz ) rad ( 0 rad2 ) height ( height ) imperfect ( off ) rows ( 2 ) cols ( 10 ) orderu ( 3 ) orderv ( 2 ) cap ( off )
    chlock tube1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off tube1

    # Node grid1
    opadd -n grid grid1
    oplocate -x 1 -y 5 grid1
    chadd grid1 sizey
    chkey -t $TSTART -v 0.5 -m 0 -a 1 -F 'ch("../tube1/rad2")*0.5' grid1/sizey
    chadd grid1 ty
    chkey -t $TSTART -v 0.25 -m 0 -a 1 -F 'ch("../tube1/rad2")*0.25' grid1/ty
    opparm grid1 type ( poly ) surftype ( quads ) orient ( xy ) size ( 0.03 sizey ) t ( 0 ty 0 ) rows ( 2 ) cols ( 2 ) orderu ( 4 ) orderv ( 4 ) interpu ( on ) interpv ( on )
    chlock grid1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off grid1

    # Node merge1
    opadd -n merge merge1
    oplocate -x 1.57597 -y -0.46238 merge1
    opparm merge1
    chlock merge1 -*
    opset -d on -r on -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off merge1

    # Node circle1
    opadd -n circle circle1
    oplocate -x 4.65481 -y 2.9325 circle1
    chadd circle1 radx
    chkey -t $TSTART -v 1 -m 0 -a 1 -F 'property("../../focus", 10)' circle1/radx
    chadd circle1 rady
    chkey -t $TSTART -v 1 -m 0 -a 1 -F 'property("../../focus", 10)' circle1/rady
    chadd circle1 beginangle
    chkey -t $TSTART -v 0 -m 0 -a 1 -F '-property("../../coneangle", 45)/2' circle1/beginangle
    chadd circle1 endangle
    chkey -t $TSTART -v 360 -m 0 -a 1 -F 'property("../../coneangle", 45)/2' circle1/endangle
    opparm circle1 type ( bezier ) orient ( yz ) rad ( radx rady ) t ( 0 0 0 ) order ( 4 ) divs ( 7 ) arc ( openarc ) angle ( beginangle endangle ) imperfect ( on )
    chlock circle1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off circle1

    # Node xform1
    opadd -n xform xform1
    oplocate -x 6.99735 -y 1.74563 xform1
    opparm xform1 group ( "" ) grouptype ( guess ) xOrd ( srt ) rOrd ( xyz ) t ( 0 0 0 ) r ( 0 0 90 ) s ( 1 1 1 ) p ( 0 0 0 ) scale ( 1 ) grppivot ( off ) updatenmls ( on ) vlength ( on )
    chlock xform1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off xform1
    opcf ..

    # Node point_light
    opadd -n file point_light
    oplocate -x -5.61138 -y 3.59963 point_light
    opparm point_light file ( pointlight.bgeo ) reload ( 0 )
    chlock point_light -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off point_light

    # Node switch1
    opadd -n switch switch1
    oplocate -x -2.62131 -y -2.3758 switch1
    chadd switch1 input
    chkey -t $TSTART -v 0 -m 0 -a 1 -F 'if (strcmp(propertys("../areashape", 'point'), 'point') == 0, 0, 1)' switch1/input
    opparm switch1 input ( input )
    chlock switch1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off switch1

    # Node line2
    opadd -n line line2
    oplocate -x 1.37657 -y 7.61234 line2
    opparm line2 type ( poly ) origin ( 0 1.5 0 ) dir ( 0 1 0 ) dist ( 2.5 ) points ( 2 ) order ( 4 )
    chlock line2 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off line2

    # Node duplicate1
    opadd -n duplicate duplicate1
    oplocate -x 1.39951 -y 6.62431 duplicate1
    opparm duplicate1 sourceGrp ( "" ) ncy ( 1 ) xOrd ( srt ) rOrd ( xyz ) t ( 0 0 0 ) r ( 180 0 0 ) s ( 1 1 1 ) p ( 0 0 0 ) scale ( 1 ) grppivot ( off ) cum ( on ) vlength ( on ) newg ( off ) copyg ( 'copyGroup$CY' )
    chlock duplicate1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off duplicate1

    # Node line3
    opadd -n line line3
    oplocate -x 4.35739 -y 7.63465 line3
    opparm line3 type ( poly ) origin ( 1.5 0 0 ) dir ( 1 0 0 ) dist ( 2.5 ) points ( 2 ) order ( 4 )
    chlock line3 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off line3

    # Node duplicate2
    opadd -n duplicate duplicate2
    oplocate -x 4.38029 -y 6.64663 duplicate2
    opparm duplicate2 sourceGrp ( "" ) ncy ( 1 ) xOrd ( srt ) rOrd ( xyz ) t ( 0 0 0 ) r ( 0 180 0 ) s ( 1 1 1 ) p ( 0 0 0 ) scale ( 1 ) grppivot ( off ) cum ( on ) vlength ( on ) newg ( off ) copyg ( 'copyGroup$CY' )
    chlock duplicate2 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off duplicate2

    # Node merge1
    opadd -n merge merge1
    oplocate -x 3.39671 -y 5.63929 merge1
    opparm merge1
    chlock merge1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off merge1

    # Node merge2
    opadd -n merge merge2
    oplocate -x -1.59936 -y 0.593665 merge2
    opparm merge2
    chlock merge2 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off merge2

    # Node null2
    opadd -n null null2
    oplocate -x -0.601918 -y 7.65078 null2
    opparm null2
    chlock null2 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off null2

    # Node switch2
    opadd -n switch switch2
    oplocate -x -0.618242 -y 2.60217 switch2
    chadd switch2 input
    chkey -t $TSTART -v 0 -m 0 -a 1 -F 'if (strcmp(property("../areashape", 'point'), "line") == 0, 0, if(strcmp(propertys("../areashape", 'point'), "tube")==0,2,1))' switch2/input
    opparm switch2 input ( input )
    chlock switch2 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off switch2

    # Node xform1
    opadd -n xform xform1
    oplocate -x 3.37466 -y 3.62929 xform1
    opparm xform1 group ( "" ) grouptype ( guess ) xOrd ( srt ) rOrd ( xyz ) t ( 0 0 0 ) r ( 0 90 0 ) s ( 1 1 1 ) p ( 0 0 0 ) scale ( 1 ) grppivot ( off ) updatenmls ( on ) vlength ( on )
    chlock xform1 -*
    opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -c off -e on -b off xform1
    opcf ..

    opcf $arg1
    opwire -n switch1 -0 point_cone_switch
    opwire -n cone_light -1 point_cone_switch
    opwire -n point_cone_switch -0 final_light
    opwire -n areasize2 -1 final_light
    opwire -n null1 -0 areashape_switch
    opwire -n line1 -1 areashape_switch
    opwire -n grid1 -2 areashape_switch
    opwire -n circle1 -3 areashape_switch
    opwire -n sphere1 -4 areashape_switch
    opwire -n tube1 -5 areashape_switch
    opwire -n areashape_switch -0 areasize2
    opwire -n merge2 -0 areasize1
    opcf cone_light
    opwire -n grid1 -0 merge1
    opwire -n tube1 -1 merge1
    opwire -n circle1 -2 merge1
    opwire -n xform1 -3 merge1
    opwire -n circle1 -0 xform1
    opcf ..
    opwire -n point_light -0 switch1
    opwire -n areasize1 -1 switch1
    opwire -n line2 -0 duplicate1
    opwire -n line3 -0 duplicate2
    opwire -n duplicate1 -0 merge1
    opwire -n duplicate2 -1 merge1
    opwire -n point_light -0 merge2
    opwire -n switch2 -1 merge2
    opwire -n null2 -0 switch2
    opwire -n merge1 -1 switch2
    opwire -n xform1 -2 switch2
    opwire -n merge1 -0 xform1
    opcf ..

    opcolor -c 1 1 0.4 $arg1

endif
