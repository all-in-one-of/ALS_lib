newNode = kwargs["node"]
newNode.parm("filename").set("$MCACHE/$OS.abc")
newNode.parm( 'build_from_path' ).set(1)