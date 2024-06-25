import make_facade_joint as MFJ
import rhinoscriptsyntax as rs
reload(MFJ)
import sys
sys.path.append("..\lib")

import EnneadTab


@EnneadTab.ERROR_HANDLE.try_catch_error
def make_facade_joints():
    base_srfs = rs.GetObjects(message = "pick many base surfaces", custom_filter = rs.filter.surface)
    joint_block = rs.GetObject(message = "pick joint block", custom_filter = rs.filter.instance)
    at_corner = True if "skip" not in rs.ListBox(["use corner", "skip corner"], "should it mark at corner?") else False
    spacing_along_edge = (rs.RealBox("max spacing mark at each edge? -1 means no placement at edge", -1)) 
    
    rs.EnableRedraw(False)
    time_mark = EnneadTab.TIME.mark_time()

    joints = []
    for i, srf in enumerate(base_srfs):
        if i % 50 == 0:
            EnneadTab.NOTIFICATION.toast(main_text = "{} of {} processed".format(i, len(base_srfs)))
        joints.append(MFJ.make_joint(joint_block, srf, at_corner, spacing_along_edge))
    #joints = [MB.make_beam(joint_block, x,  use_rs = False) for x in base_srfs]

    if isinstance(joints[0], list):
        flatten_joints = []
        for item in joints:
            flatten_joints.extend(item)
        rs.AddObjectsToGroup(flatten_joints, rs.AddGroup())
    else:
        rs.AddObjectsToGroup(joints, rs.AddGroup())

    time_used = EnneadTab.TIME.time_span(time_mark)
    EnneadTab.NOTIFICATION.toast(main_text = "All joints made!!", message = "Used {} seconds".format(time_used))
    if len(base_srfs) > 500:
        EnneadTab.RHINO.RHINO_CLEANUP.save_small()
    rs.MessageBox("All joints made!!\nUsed {} seconds = {} mins".format(time_used, time_used/60))
#####
if __name__ == "__main__":
    make_facade_joints()
