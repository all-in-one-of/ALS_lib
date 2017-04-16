HOUDINI_INSTALL_PATH = 'C:/Houdini16/Houdini_16.0.557'
import os, sys
sys.path.append('{}/houdini/python2.7libs'.format(HOUDINI_INSTALL_PATH))
import hou
import re

import alsnodeutils
reload(alsnodeutils)

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
LOCAL = 'Q:/Houdini'
# LOCAL = 'C:/Users/a.grabovski'

#=========================================== Rop List Fuctions ===================================

def checkTree(node):
    validTypes = ['my_cache',
                  'rop_geometry',
                  'geometry',
                  'write_abc',
                  'rop_alembic',
                  'alembic',
                  'ifd',]
    number = node.parm('list').eval()
    result = []
    for i in range(number):
        if node.parm('use{}'.format(i+1)).eval():
            rop = 'cachepath{0}'.format(i+1)
            ropPathParm = node.parm(rop).eval()
            srcNode = alsnodeutils.relToAbsNode( node, ropPathParm )
            ropType = alsnodeutils.shortType(srcNode)

            if ropType != None:
                if not ropType in validTypes :
                    hou.ui.displayMessage("Invalid rop type '{}' in path {}".format(ropType, i+1))
                else:
                    depend = node.parm('depend{}'.format(i+1)).eval()
                    depend = 0 if depend == '' else depend
                    result.append((i+1, srcNode, int(depend)))
    return result

def createRopNode(*args):
    network = args[0]
    nodeType = args[1]
    nodeName = args[2]
    outNode = args[3]
    inputNumber = args[4]
    out =  network.createNode(nodeType, node_name=nodeName)
    alsnodeutils.copyParms(outNode, out)
    return out

def createTree():
    typeDict = {'my_cache' : 'geometry',
                'rop_geometry' : 'geometry',
                'geometry' : 'geometry',
                'write_abc' : 'alembic',
                'rop_alembic' : 'alembic',
                'alembic' : 'alembic',
                'ifd' : 'ifd',}

    node = hou.pwd()
    ropnet = node.node('ropnet')
    number = node.parm('list').eval()
    assPat = re.compile('\:\:(?P<name>[^\:]+)\:\:')
    for i in range(number):
        if node.parm('use{}'.format(i+1)).eval():
            rop = 'cachepath{0}'.format(i+1)
            ropPathParm = node.parm(rop).eval()
            ropPathParm = alsnodeutils.relToAbsPath( node, ropPathParm )
            srcNode = hou.node(ropPathParm)

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

                elif ropType == 'write_abc' :
                    name = '{0}{1}.{2:02d}'.format(srcNode.parm('name').eval(),
                                                   srcNode.parm('post').eval(),
                                                   srcNode.parm('ver').eval())
                    outputNode = srcNode.node('output_abc')
                else:
                    name = srcNode.name()
                    outputNode = srcNode
                try:
                    out = createRopNode(ropnet, typeDict[ropType], name, outputNode, i)
                    node.parm('ropnode{}'.format(i+1)).set(out.path())
                    if ropType == 'rop_alembic':
                        try:
                            inputNode =  srcNode.inputs()[0]
                            out.parm('use_sop_path').deleteAllKeyframes()
                            out.parm('use_sop_path').set(1)
                            out.parm('sop_path').set(srcNode.path())

                        except(IndexError):
                            pass

                    ropnet.layoutChildren()
                except(KeyError):
                    hou.ui.displayMessage("Invalid rop type '{}' in path {}".format(ropType, i+1))


if __name__ == '__main__':
    pass