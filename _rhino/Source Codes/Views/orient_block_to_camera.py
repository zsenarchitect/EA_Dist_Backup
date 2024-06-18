import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math
import sys



sys.path.append("..\lib")
import EnneadTab



def process_block(block, cam_vector):
    transform = rs.BlockInstanceXform(block)
    print(transform)

    """
    # Rotate an object by theta degrees about the world Z axis
    degrees = 90.0 # Some angle
    radians = math.radians(degrees)
    c = math.cos(radians)
    s = math.sin(radians)
    matrix = []
    matrix.append( [c,-s, 0, 0] )
    matrix.append( [s, c, 0, 0] )
    matrix.append( [0, 0, 1, 0] )
    matrix.append( [0, 0, 0, 1] )
    rs.TransformObject( block, matrix )
    """
    angle_degree = 45
    rotate_transform = rs.XformRotation2(angle_degree,
                                        [0,0,1],
                                        rs.BlockInstanceInsertPoint(block))
    rs.TransformObject( block, rotate_transform )


def get_camera_vector():

    ground_plane = rs.WorldXYPlane()
    xform = rs.XformPlanarProjection(ground_plane)
    cam_pt, target_pt = rs.ViewCameraTarget()
    #print cam_pt
    #print target_pt
    #print "@@@@@@"

    #cam_pt, target_pt = rs.TransformObjects( rs.ViewCameraTarget(), xform, False )
    #print cam_pt
    #print target_pt
    x0, y0, z0 = cam_pt
    x1, y1, z1 = target_pt
    return [x1-x0, y1-y0, 0]


@EnneadTab.ERROR_HANDLE.try_catch_error
def orient_block_to_camera():

    # get blocks with [EA_TRUE_FLAT] in block name
    blocks = []
    for block_name in rs.BlockNames():
        if "[EA_TRUE_FLAT]" in block_name:
            blocks.extend(rs.BlockInstances(block_name))

    # process blocks
    cam_vec = get_camera_vector()
    map(lambda x:process_block(x, cam_vec), blocks)


    """
    view = rs.CurrentView()
    target = rs.ViewTarget(view)
    camplane = rs.ViewCameraPlane(view)
    camplane = rs.MovePlane(camplane, target)
    rs.ViewCPlane( view, camplane )
    """



######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    orient_block_to_camera()
