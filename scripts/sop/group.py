import colors
reload( colors )
newNode = kwargs["node"]
clr = hou.Color( colors.group )
newNode.setColor( clr )
newNode.parm( "crname" ).set("$OS")