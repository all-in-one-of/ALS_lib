import hou
import os
import subprocess

import alsnodeutils
reload(alsnodeutils)
import alsrenderutils
reload(alsrenderutils)
import fileUtils

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
LOCAL = 'Q:/Houdini'
HIP = hou.hipFile.path()
ALS = hou.expandString('$ALS')
RENDER_TYPES = {"ifd"          : "img",
                "my_cache"     : "geo",
                "geometry"     : "geo",
                "rop_geometry" : "geo",
                "write_abc"    : "abc",
                "rop_alembic"  : "abc",}
VER = hou.expandString('$_HIP_SAVEVERSION')
WRAPPER = '{}/scripts/wrapHy.py'.format(ALS)
RENDER_SCRIPT = '{}/scripts/render.py'.format(ALS)
EXPORT = hou.expandString('$_EXPORT')

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
        self.cmd = self._cmd()
        self.alf = self._alfred()

    def _getRange(self):
        f = [int(self.node.parm('f{}'.format(i+1)).eval()) for i in range(3)]
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

    def _writeCmd(self, rop, fr):
        cmdFile = '{}/{}.{}.{}.cmd'.format(EXPORT,
                                           self.node.name(),
                                           self.renderType,
                                           int(fr[0]))
        with open(cmdFile, 'w') as f:
            f.write(r'''
@echo off
setlocal
set WRAPPER={0}
set VERSION={1}
set RENDER={2}
set HIPPATH={3}
set ROPNODE={4}
set F1={5[0]}
set F2={5[1]}
set F3={5[2]}
python %WRAPPER% %VERSION% %RENDER% %HIPPATH% %ROPNODE% %F1% %F2% %F3%
pause
'''.format(WRAPPER.replace('/', '\\'),
           VER,
           RENDER_SCRIPT.replace('/', '\\'),
           HIP.replace('/', '\\'),
           rop,
           fr))
        return cmdFile

    def _cmd(self):
        fileUtils.createDir(EXPORT)
        rop = self.node.path()
        if self.nodeType == 'my_cache':
            name = self.node.parm('name').eval()
            rop += '/{}'.format(name)

        elif self.nodeType == 'write_abc':
            rop += '/output_abc'

        if self.mode == 'single':
            cmd = [self._writeCmd(rop, self.fr)]
        elif self.mode == 'range':
            cmd = []
            _fr = [i for i in self.fr]
            _fr[1] += 1
            for i in range(*_fr):
                frame = i, i, _fr[2]
                cmd.append(self._writeCmd(rop, frame))

        return cmd

    def _alfred(self):
        return None

class deputat():
    def __init__(self):
        node = hou.pwd()
        listNode = alsnodeutils.relToAbsNode(node, node.parm('listnode').eval())
        ropNodes = alsrenderutils.checkTree(listNode)
        self.outputs = []
        # print '\n=================================================\n'
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