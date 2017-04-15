import hou
import os
import subprocess

import alsnodeutils
reload(alsnodeutils)
import alsrenderutils
reload(alsrenderutils)

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
LOCAL = 'Q:/Houdini'
RENDER_TYPES = {"ifd"          : "img",
                "my_cache"     : "geo",
                "geometry"     : "geo",
                "rop_geometry" : "geo",
                "write_abc"    : "abc",
                "rop_alembic"  : "abc",}

class ropTask():
    def __init__(self, parent, index, node, depend=None):
        self.node = node
        self.nodeType = alsnodeutils.shortType(node)
        self.renderType = RENDER_TYPES[self.nodeType]
        self.parent = parent
        self.index = index
        self.depend = depend
        self.fr = self._getRange()
        self.mode = self._getMode()
        self.hycmd = self._hycmd()
        self.alf = self._alfred()

    def _getRange(self):
        f = [self.node.parm('f{}'.format(i+1)).eval() for i in range(3)]
        return f[0], f[1], f[2]

    def _getMode(self):
        mode = 'range'
        if self.nodeType == 'my_cache':
            sim = self.node.parm('simmode').eval()
            single = self.node.parm('single').eval()
            return 'single' if sim or single else 'range'
        elif self.renderType == 'abc':
            return 'single'
        else:
            return 'range'

    def _hycmd(self):
        file = hou.hipFile.path()
        rop = self.node.path()

        if self.nodeType == 'my_cache':
            name = self.node.parm('name').eval()
            rop += '/{}'.format(name)

        elif self.nodeType == 'write_abc':
            rop += '/output_abc'

        code =r'''
hou.hipFile.load('{0}')
rop = hou.node("{1}")
try:
    rop.parm('vm_verbose').set(4)
    rop.parm("vm_vexprofile").set(2)
except(AttributeError):
    pass
rop.render(frame_range = {2}, verbose = True, output_progress = True)
exit()
'''.format(hou.hipFile.path(),
           rop,
           self.fr,)

        print code
        return None

    def _alfred(self):
        return None

class deputat():
    def __init__(self):
        node = hou.pwd()
        listNode = alsnodeutils.relToAbsNode(node, node.parm('listnode').eval())
        ropNodes = alsrenderutils.checkTree(listNode)
        self.outputs = []
        print '\n=================================================\n'
        for i, n, d in ropNodes:
            self.outputs.append(ropTask(listNode, i, n, d))
            # print listNode, i, n, d

        # for out in self.outputs:
            # print out.fr, out.mode

# # print 'ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
# cmd = hou.pwd().parm('cmd').eval()
# alfred = '//PROJECTS/Alisa_Film/HoudiniProject/Jobs/Research/deputat_tests/alf/test.alf'
# print 'unix {0} "{1}"'.format(cmd, alfred)
# # hou.hscript('unix {0} "{1}"\npause'.format(cmd, alfred))
# # subprocess.Popen('{0} "{1}"'.format(cmd, alfred))

dep = deputat()


if __name__ == '__main__':
    print 'Deputat!'