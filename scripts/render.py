import hou, sys
try:
    hip =  sys.argv[1]
    node = sys.argv[2]
    f = (int(sys.argv[3]),
         int(sys.argv[4]),
         int(sys.argv[5]))

    hou.hipFile.load(hip)
    hippath = '/'.join(hip.split('\\')[:-1])
    hipname = hip.split('\\')[-1].replace('.hip', '')
    hou.hscript('set -g HIP={}'.format(hippath))
    hou.hscript('set -g HIPNAME={}'.format(hipname))
    hou.hscript('set -g HIPFILE={}/{}.hip'.format(hip, hipname))
    rop = hou.node(node)
    try:
        rop.parm('vm_verbose').set(4)
        rop.parm("vm_vexprofile").set(1)
        rop.parm("vm_alfprogress").set(1)

    except(AttributeError):
        try:
            rop.parm("alfprogress").set(1)
        except(AttributeError):
            pass
    rop.render(frame_range = f, verbose = True, output_progress = True)
    exit()

except(IndexError):
    print 'Bad args:'
    for arg in sys.argv:
        print arg