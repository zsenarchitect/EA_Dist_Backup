import make_beam as MB
import rhinoscriptsyntax as rs
reload(MB)
import sys
sys.path.append("..\lib")

import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error
def make_beams():
    base_crvs = rs.GetObjects(message = "pick many base curves", custom_filter = rs.filter.curve)
    profile = rs.GetObject(message = "pick profile curves in block", custom_filter = rs.filter.instance)
    rs.EnableRedraw(False)
    time_mark = EnneadTab.TIME.mark_time()

    beams = []
    for i, crv in enumerate(base_crvs):
        if i % 20 == 0:
            EnneadTab.NOTIFICATION.toast(main_text = "{} of {} processed".format(i, len(base_crvs)))
        beams.append(MB.make_beam(profile, crv,  use_rs = False))
    #beams = [MB.make_beam(profile, x,  use_rs = False) for x in base_crvs]

    if isinstance(beams[0], list):
        flatten_beams = []
        for item in beams:
            flatten_beams.extend(item)
        rs.AddObjectsToGroup(flatten_beams, rs.AddGroup())
    else:
        rs.AddObjectsToGroup(beams, rs.AddGroup())

    time_used = EnneadTab.TIME.time_span(time_mark)
    EnneadTab.NOTIFICATION.toast(main_text = "All beams made!!", message = "Used {} seconds".format(time_used))
    if len(base_crvs) > 150:
        EnneadTab.RHINO.RHINO_CLEANUP.save_small()
    rs.MessageBox("All beams made!!\nUsed {} seconds = {} mins".format(time_used, time_used/60))
#####
if __name__ == "__main__":
    make_beams()
