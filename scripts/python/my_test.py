import hou, re, os

def printColor():
	try:
		node = hou.selectedNodes()[0]
		print node.color()
	except(IndexError):
		pass

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
LOCAL = 'Q:/Houdini'

def clean(node):
    for child in node.children():
        if child.type().name() != 'merge':
            child.destroy()

def test():
    node = hou.node('/obj/geo1/rop_list1')
    ropnet = node.node('ropnet')
    number = node.parm('list').eval()
    assPat = re.compile('\:\:(?P<name>[^\:]+)\:\:')
    frPat = re.compile('\.(?P<fexp>\$F\d)\.')
    clean(ropnet)
    for i in range(number):
        rop = 'cachepath{0}'.format(i+1)
        srcNode = hou.node(node.parm(rop).eval())

        try:
            ropType = assPat.search(srcNode.type().name()).group('name')
        except(AttributeError):
            try:
                ropType = srcNode.type().name()
            except(AttributeError):
                ropType = None
                # continue
        if ropType != None :
            collect = ropnet.node('collect')
            if ropType == 'my_cache':
                name = srcNode.parm('name').eval()
                outputNode = srcNode.node(name)
                inputNode = outputNode.inputs()[0]
                try:
                    outExp = outputNode.parm('sopoutput').unexpandedString().replace('$OS', name)
                    fexp = frPat.search(outExp).group('fexp')
                    outfile = hou.expandString(outExp.replace(fexp, '#')).replace('#', fexp)
                except(AttributeError):
                    outfile = outputNode.parm('sopoutput').eval().replace(LOCAL, HOUDINI_GLOB_PATH)

                out = ropnet.createNode('geometry', node_name=name)
                out.parm('soppath').set(inputNode.path())
                out.parm('sopoutput').set(outfile)
                out.parm('trange').set(srcNode.parm('trange').eval())

                for f in range(3):
                    fp = 'f{}'.format(f+1)
                    out.parm(fp).deleteAllKeyframes()
                    if srcNode.parm('single').eval():
                        out.parm(fp).set(1)
                    else:
                        out.parm(fp).set(srcNode.parm(fp).eval())
                collect.setInput(i, out)

            elif ropType == 'rop_geometry':
                name = srcNode.name()
                try:
                    inputNode = srcNode.inputs()[0]
                    try:
                        outExp = srcNode.parm('sopoutput').unexpandedString().replace('$OS', name)
                        fexp = frPat.search(outExp).group('fexp')
                        outfile = hou.expandString(outExp.replace(fexp, '#')).replace('#', fexp)
                    except(AttributeError):
                        outfile = srcNode.parm('sopoutput').eval().replace(LOCAL, HOUDINI_GLOB_PATH)

                    out = ropnet.createNode('geometry', node_name=name)
                    out.parm('soppath').set(inputNode.path())
                    out.parm('sopoutput').set(outfile)
                    out.parm('trange').set(srcNode.parm('trange').eval())

                    for f in range(3):
                        fp = 'f{}'.format(f+1)
                        out.parm(fp).deleteAllKeyframes()
                        out.parm(fp).set(srcNode.parm(fp).eval())
                    collect.setInput(i, out)

                except(IndexError):
                    hou.ui.displayMessage('Not input connection for "{}". Ignore'.format(srcNode.path()))

            ropnet.layoutChildren()


if __name__ == '__main__':
    pass

    # grabovskiy::my_srcNode::1.0.3