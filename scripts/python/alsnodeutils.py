HOUDINI_INSTALL_PATH = 'C:/Houdini16/Houdini_16.0.557'
import os, sys
sys.path.append('{}/houdini/python2.7libs'.format(HOUDINI_INSTALL_PATH))
import hou
import re

HOUDINI_GLOB_PATH = os.environ['HOUDINI_PATH'].split(os.path.pathsep)[0]
LOCAL = 'Q:/Houdini'

def relToAbsPath(node, path):
    '''
    Convert relative node path to absolute
    '''
    link = node.node(path)
    try:
        return link.path()
    except(AttributeError):
        return None

def relToAbsNode(node, path):
    absPath = relToAbsPath(node, path)
    return hou.node(absPath)

def frameExpExpand(path):
    '''
    Expand string, but leave $F expression
    '''
    frPat = re.compile('\.(?P<fexp>\$F\d)\.')
    try:
        fexp = frPat.search(path).group('fexp')
        outpath = hou.expandString(path.replace(fexp, '#')).replace('#', fexp)
    except(AttributeError):
        outpath = hou.expandString(path)

    return outpath.replace(LOCAL, HOUDINI_GLOB_PATH)

def expandExpression(node, exp):
    '''
    Expand expressions with relative path
    '''
    chanPat = re.compile('(?P<ch>chs|ch)(\([\'|\"](?P<parm>[^\']+)[\'|\"]\))')
    d = {}
    res = exp
    for match in chanPat.finditer(exp):
        ch = match.group('ch')
        parm = match.group('parm')
        key = match.group()
        if parm.startswith('.'):
            val = hou.hscriptExpression('{0}("{1}/{2}")'.format(ch, node.path(), parm))
        else:
            val = hou.hscriptExpression('{0}("{1}")'.format(ch, parm))
        d[key] = val

    for k, v in d.iteritems():
        res = res.replace(k, str(v))

    return hou.hscriptExpression(res)


def expandStringExp(node, path):
    '''
    Expand complex string expressions witch use ``
    '''
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
    '''
    Copy parms from src node to target
    '''
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

def shortType(node):
    assPat = re.compile('\:\:(?P<name>[^\:]+)\:\:')
    try:
        return assPat.search(node.type().name()).group('name')
    except(AttributeError):
        try:
            return node.type().name()
        except(AttributeError):
            return None

if __name__ == '__main__':
    pass