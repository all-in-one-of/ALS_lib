import hou
import os
import re
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
    def __init__(self, node, index, depend):
        self.node = node
        self.rop = node
        self.index = index
        self.depend = depend
        self.nodeType = alsnodeutils.shortType(node)
        self.renderType = RENDER_TYPES[self.nodeType]
        self.taskName = self._taskName()
        self.fr = self._getRange()
        self.mode = self._getMode()
        self.cmd = self._cmd()
        self.preview = self._getFileName()
        # self.alf = self._alfred()
        # print self.alf

    def _getRange(self):
        f = [int(self.node.parm('f{}'.format(i+1)).eval()) for i in range(3)]
        return f[0], f[1], f[2]

    def _getMode(self):
        mode = 'range'
        if self.nodeType == 'my_cache':
            sim = self.node.parm('simmode').eval()
            single = self.node.parm('single').eval()
            if single :
                self.fr = 1,1,1
            return 'single' if sim or single else 'range'
        elif self.renderType == 'abc':
            return 'single'
        else:
            return 'range'

    def _taskName(self):
        return '{}.{}'.format(self.node.name(),
                              self.renderType)

    def _cmdName(self, num):
        if self.mode == 'single':
            return self.taskName

        return '{}.{}.{}'.format(self.node.name(),
                                 self.renderType,
                                 num)

    def _writeCmd(self, rop, fr):
        cmdFile = '{}/{}.cmd'.format(EXPORT, self._cmdName(fr[0]))
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
            self.rop = hou.node(rop)

        elif self.nodeType == 'write_abc':
            rop += '/output_abc'
            self.rop = hou.node(rop)

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

    def _getFileName(self):
        try:
            fileParm = self.rop.parm('vm_picture').unexpandedString()
        except(AttributeError):
            try:
                fileParm = self.rop.parm('sopoutput').unexpandedString()
            except(AttributeError):
                fileParm = self.rop.parm('filename').unexpandedString()

        fileParm = fileParm.replace('$OS', self.rop.name())
        file = alsnodeutils.expandStringExp(self.rop, fileParm)
        file = alsnodeutils.frameExpExpand(file)
        fexp = re.compile('\$F(?P<pad>\d)')
        try:
            pad = int(fexp.search(file).group('pad'))
        except(AttributeError):
            pad = 4
        if self.mode == 'single':
            frame = '%0*d'%(pad, int(self.fr[0]))
            return fexp.sub(frame, file)
        elif self.mode == 'range':
            res = []
            _fr = [i for i in self.fr]
            _fr[1] += 1
            for i in range(*_fr):
                frame = '%0*d'%(pad, i)
                res.append(fexp.sub(frame, file))
            return res
                

    def _setLevel(self, code, level):
        indent = ''.join(['    ' for i in range(level)])
        res = []
        for ln in code.split('\n'):
            if ln != '':
                res.append('{}{}'.format(indent,ln))
            else:
                res.append('')
        return '\n'.join(res)

    def alfred(self, level=1, instance=None):
        kwargs = {'task' : self.taskName,
                  'preview' : 'mplay.exe' if self.renderType == 'img' else 'gplay.exe',
                  'file' : self.preview,
                  'instance' : instance}
        # ---------------------------------- Multiframe task ------------------------------
        if len(self.cmd) > 1: 
            code = r'''

Task {{ {task} }} -subtasks {{'''.format(**kwargs)
            kwargs['subtask'] = kwargs['task'].split('.')[0]
            for i, cmd in enumerate(self.cmd):
                kwargs['cmd'] = cmd
                kwargs['frame'] = i + self.fr[0]
                kwargs['file'] = self.preview[i]
                kwargs['num'] = i

                # ----------------------------- Default free task --------------------------
                if instance == None:
                    code += r'''

    Task {{ {subtask}.frame.{frame} }} -cmds {{
            RemoteCmd {{ {cmd} }}
        }} -preview {{
            {preview} "{file}"
        }}'''.format(**kwargs)
                # ----------------------------- Dependent task --------------------------
                else :
                    code += r'''

    Task {{ {subtask}.frame.{frame} }} -subtasks {{
            Instance {{ {instance} }}
        }} -cmds {{
            RemoteCmd {{ {cmd} }}
        }} -preview {{
            {preview} "{file}"
        }} -cleanup {{
            Cmd {{ Alfred }} -msg {{ File delete "{cmd}" }}
        }}'''.format(**kwargs)

            # ----------------------------- Default free task cleanup --------------------------
            if instance == None:
                code += '\n\n    } -cleanup {\n'
                for i, cmd in enumerate(self.cmd):
                    kwargs['cmd'] = cmd
                    code += '''
        Cmd {{ Alfred }} -msg {{ File delete "{cmd}" }}'''.format(**kwargs)
            code += '\n\n    }'

        else:
            kwargs['cmd'] = self.cmd[0]
            code = r'''

Task {{ {task} }} -cmds {{
        RemoteCmd {{ {cmd} }}
    }} -preview {{
        {preview} "{file}"
    }}'''.format(**kwargs)
            code += ''' -cleanup {{
        Cmd {{ Alfred }} -msg {{ File delete "{cmd}" }}
    }}'''.format(**kwargs)

        return self._setLevel(code, level)

class deputat():
    def __init__(self):
        node = hou.pwd()
        listNode = alsnodeutils.relToAbsNode(node, node.parm('listnode').eval())
        ropNodes = alsrenderutils.checkTree(listNode)
        self.comment = listNode.parm('comment').eval()
        self.save = listNode.parm('save_scene').eval()
        self.submit = listNode.parm('submit').eval()

        self.outputs = []
        for i, n, d in ropNodes:
            self.outputs.append(ropTask(n, i, d))
        self.jobName = self._getJob(listNode)
        self.alf = self._alfred()
        self.cmd = 'unix {} "{}"'.format(listNode.parm('cmd').eval(), self.alf)

    def _getJob(self, listNode):
        basename = hou.hipFile.path().split('/')[-1].replace('.hip', '')
        seq = hou.expandString('$SEQ')
        sh = hou.expandString('$SH')
        seq_sh = '{}_{}'.format(seq, sh) if seq != '' else ''
        base = '{}.{}'.format(seq_sh, basename) if seq_sh != '' else basename
        return '{}.{}'.format(base, listNode)

    def findOutput(self, index):
        for out in self.outputs:
            if out.index == index:
                return out.taskName
        return None

    def _alfred(self):
        kwargs = {'job' : self.jobName,
                  'comment' : self.comment}
        code = r'''##AlfredToDo 3.0
Job -title {{ {job} }} -comment {{ {comment} }} -subtasks {{'''.format(**kwargs)
        for out in self.outputs:
            dep = self.findOutput(out.depend)
            code += out.alfred(instance=dep)
        code += '\n\n    }'

        alfFile = '{}/{}.alf'.format(EXPORT, self.jobName)
        with open(alfFile, 'w') as f:
            f.write(code)
        return alfFile

    def start(self):
        if self.save == 1:
            print 'Save scene'
            hou.hipFile.save()
        print self.cmd
        hou.hscript(self.cmd)


dep = deputat()
dep.start()


if __name__ == '__main__':
    print 'Deputat!'