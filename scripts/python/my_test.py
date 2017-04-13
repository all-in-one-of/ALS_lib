import hou
import re, os

def printColor():
	try:
		node = hou.selectedNodes()[0]
		print node.color()
	except(IndexError):
		pass

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
LOCAL = 'Q:/Houdini'
LOCAL = 'C:/Users/a.grabovski'

def clean(node):
    for child in node.children():
        if child.type().name() != 'merge'\
        and child.type().name() != 'null'\
        and not 'deputat' in child.type().name():
            # print child.name()
            child.destroy()

def relToAbsPath(node, path):
    link = node.node(path)
    try:
        return link.path()
    except(AttributeError):
        return None

def frameExpExpand(path):
    frPat = re.compile('\.(?P<fexp>\$F\d)\.')
    try:
        fexp = frPat.search(path).group('fexp')
        outpath = hou.expandString(path.replace(fexp, '#')).replace('#', fexp)
    except(AttributeError):
        outpath = hou.expandString(path)

    return outpath.replace(LOCAL, HOUDINI_GLOB_PATH)

def expandExpression(node, exp):
    chanPat = re.compile('(?P<ch>chs|ch)(\([\'|\"](?P<parm>[^\']+)[\'|\"]\))')
    d = {}
    res = exp
    for match in chanPat.finditer(exp):
        ch = match.group('ch')
        parm = match.group('parm')
        key = match.group()
        val = hou.hscriptExpression('{0}("{1}/{2}")'.format(ch, node.path(), parm))
        d[key] = val

    for k, v in d.iteritems():
        res = res.replace(k, str(v))

    return hou.hscriptExpression(res)


def expandStringExp(node, path):
    expPat = re.compile('\`([^\`]+)\`')
    groups = expPat.findall(path)
    splitted = expPat.split(path)
    res = []
    for part in splitted:
        if part in groups:
            res.append(expandExpression(node, part))
        else:
            # print part
            res.append(part)

    return ''.join(res)


def copyParms(src, target):
    for p in src.parms():
        tepmplate = p.parmTemplate()
        name = tepmplate.name()
        label = tepmplate.label()
        ptype = tepmplate.type()
        if ptype != hou.parmTemplateType.Button:
            try:
                if ptype == hou.parmTemplateType.String:
                    tags = tepmplate.tags()
                    value = p.unexpandedString()
                    if 'opfilter' in tags:
                        target.parm(name).set(relToAbsPath(src, value))
                    else:
                        value = value.replace('$OS', src.name())
                        value = value.replace('pwd()', 'node("{}")'.format(src.path()))
                        value = expandStringExp(src, value)
                        target.parm(name).set(frameExpExpand(value))

                else:
                    expression = 'ch("{}")'.format(p.path())
                    target.parm(p.name()).setExpression(expression)
            except(AttributeError):
                pass

def createRopNode(*args):
    network = args[0]
    nodeType = args[1]
    nodeName = args[2]
    outNode = args[3]
    collectNode = args[4]
    inputNumber = args[5]
    out =  network.createNode(nodeType, node_name=nodeName)
    copyParms(outNode, out)
    # print collectNode
    collectNode.setInput(inputNumber, out)

def createTree():
    node = hou.node('/obj/geo1/rop_list1')
    ropnet = node.node('ropnet')
    number = node.parm('list').eval()
    assPat = re.compile('\:\:(?P<name>[^\:]+)\:\:')
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
                createRopNode(ropnet, 'geometry', name, outputNode, collect, i)

            elif ropType == 'rop_geometry':
                name = srcNode.name()
                outputNode = srcNode
                createRopNode(ropnet, 'geometry', name, outputNode, collect, i)

            elif ropType == 'write_abc' :
                name = '{0}{1}.{2:02d}'.format(srcNode.parm('name').eval(),
                                        srcNode.parm('post').eval(),
                                        srcNode.parm('ver').eval())
                outputNode = srcNode.node('output_abc')
                createRopNode(ropnet, 'alembic', name, outputNode, collect, i)

            elif ropType == 'rop_alembic':
                name = srcNode.name()
                outputNode = srcNode
                createRopNode(ropnet, 'alembic', name, outputNode, collect, i)

            elif ropType == 'ifd':
                name = srcNode.name()
                outputNode = srcNode
                createRopNode(ropnet, 'ifd', name, outputNode, collect, i)




            ropnet.layoutChildren()


def test():
    createTree()
    # node = hou.node('/obj/geo1/write_abc1/output_abc')
    # exp = "$MCACHE/`chs('../name') + chs('../post')`.v`padzero(2,ch('../ver'))`.abc"
    # print expandStringExp( node, exp )
    # print expandExpression( node, "chs('../name') + chs('../post')" )

if __name__ == '__main__':
    pass

    # grabovskiy::my_srcNode::1.0.3