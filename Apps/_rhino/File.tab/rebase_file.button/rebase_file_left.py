__title__ = "RebaseFile"
__doc__ = "Try to rebase the file center to new origin point, include all the views."
__is_popular__ = True
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore

from EnneadTab import ERROR_HANDLE, LOG, SOUND

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def rebase_file():
    # Get new base point from user
    point = rs.GetPoint("Pick a new base point. I suggest you mark a line that is the difference between the old origin and new origin and move it to the current origin, then you pick the end pt of this line.")
    if point is None: return

    rebase_objects(point)
    rebase_views(point)
    SOUND.play_sound()

def rebase_objects(point):
    # Calculate the vector from the World Origin to the new point
    vector = rs.VectorCreate([0, 0, 0],point)
    
    # Move all objects
    objects = rs.AllObjects(select=False)
    if objects:
        rs.MoveObjects(objects, vector)

def rebase_views(point):
    # Move all named views (cameras)
    start_pt = Rhino.Geometry.Point3d(0, 0, 0)
    end_pt = point

    all_views = rs.NamedViews()
    source_array = [end_pt, rs.PointAdd(end_pt, Rhino.Geometry.Point3d(1, 0, 0))]
    target_array = [start_pt, rs.PointAdd(start_pt, Rhino.Geometry.Point3d(1, 0, 0))]

    for view in sorted(all_views, reverse=True):
        print("Reorienting view [{}]".format(view))
        rs.RestoreNamedView(view, view=None, restore_bitmap=False)
        current_cam, current_cam_target = rs.ViewCameraTarget(view=view, camera=None, target=None)

        # Create temporary points for camera and target
        temp_cam_pt = rs.AddPoint(current_cam)
        temp_cam_target_pt = rs.AddPoint(current_cam_target)

        # Orient camera and target
        new_cam = rs.OrientObject(temp_cam_pt, source_array, target_array)
        new_cam_target = rs.OrientObject(temp_cam_target_pt, source_array, target_array)
        rs.ViewCameraTarget(view=view, camera=new_cam, target=new_cam_target)

        rs.AddNamedView(view, view)  # Override existing view

        # Clean up temporary objects
        rs.DeleteObject(temp_cam_pt)
        rs.DeleteObject(temp_cam_target_pt)

    # Redraw the viewport to reflect changes
    rs.Redraw()

if __name__ == "__main__":
    rebase_file()
