import rhinoscriptsyntax as rs
from scriptcontext import doc
import Rhino # pyright: ignore
import sys
sys.path.append("..\lib")
import EnneadTab
import make_beam as MB
reload(MB)

@EnneadTab.ERROR_HANDLE.try_catch_error
def make_truss():
    base_crv = rs.GetObject(message = "pick base curve", custom_filter = rs.filter.curve)
    profile = rs.GetObject(message = "pick profile curves in block", custom_filter = rs.filter.instance)
    depth = float(rs.StringBox(message = "Enter diagramatic truss web depth in file unit", default_value = str(900)))
    sample_interval = depth
    division = int(rs.CurveLength(base_crv)/sample_interval)
    rs.EnableRedraw(False)


    lower_chord = rs.CopyObject(base_crv, [0,0,-depth])
    top_pts = rs.DivideCurve(base_crv, 2 * division)
    bm_pts = rs.DivideCurve(lower_chord, 2 * division)
    beam_lines = [base_crv]
    for i in range(len(top_pts) - 1):
        if i%2 == 0:
            a, b = top_pts[i], bm_pts[i + 1]
        else:
            a, b = bm_pts[i], top_pts[i + 1]
        beam_lines.append(rs.AddLine(a, b))

    t1 = rs.CurveClosestPoint(lower_chord, bm_pts[1])
    t2 = rs.CurveClosestPoint(lower_chord, bm_pts[-2])
    interval = rs.CreateInterval(t1, t2)
    line2 = rs.TrimCurve(lower_chord, interval)

    #line2 = rs.AddLine(bm_pts[1], bm_pts[-2])
    line1, line3 = beam_lines[1], beam_lines[-1]
    new_bm_crv = rs.JoinCurves([line1, line2, line3], delete_input = True)
    beam_lines.append(new_bm_crv)

    border_lines = [beam_lines[0], beam_lines[-1]]
    inner_lines = beam_lines[1:-2]

    rs.DeleteObject(lower_chord)



    def process_lines(lines):
        OUT = []
        for line in lines:
            try:
                beam = MB.make_beam( profile, line)
                OUT.append(beam)
            except:
                pass
        return OUT

    border_beams = process_lines(border_lines)
    inner_beams = process_lines(inner_lines)



    """
    method 1
    """
    """
    def trim_inner_beam(inner_beam):
        copied_border_beams = rs.CopyObjects(border_beams)
        inner_beam = rs.BooleanDifference(inner_beam, copied_border_beams, delete_input = True)
        inner_beam.sort(key = lambda x: rs.SurfaceVolume(x))
        inner_beam, bad_beams = inner_beam[-1], inner_beam[0:-1]
        rs.DeleteObjects(bad_beams)
        return inner_beam
    inner_beams = [trim_inner_beam(x) for x in inner_beams]
    """

    """
    method 2
    """
    count = len(inner_beams)
    copied_border_beams = rs.CopyObjects(border_beams)
    inner_beams = rs.BooleanDifference(inner_beams, copied_border_beams, delete_input = True)
    inner_beams.sort(key = lambda x: rs.SurfaceVolume(x), reverse = True)
    inner_beam, bad_beams = inner_beams[0:count], inner_beams[count:-1]
    rs.DeleteObjects(bad_beams)

    beams = inner_beams + border_beams
    rs.AddObjectsToGroup(beams, rs.AddGroup())
    rs.AddObjectsToGroup(beam_lines, rs.AddGroup())




#####
if __name__ == "__main__":
    make_truss()
