import rhinoscriptsyntax as rs
import clr # pyright: ignore
import Rhino # pyright: ignore
import sys
sys.path.append("..\lib")
import EnneadTab

"""
### TO-DO:
- Matching irregularly scaled blocks does not work
#### Assigned to: **CM**
"""


@EnneadTab.ERROR_HANDLE.try_catch_error
def match_block_distortion():

    bad_blocks = rs.GetObjects(
        "Select block instances to change", filter=4096, preselect=True)
    if not bad_blocks:
        return
    good_block = rs.GetObject(
        "Select block instances that has desired distortion", filter=4096, preselect=True)
    if not good_block:
        return
    rs.EnableRedraw(False)

    transform = rs.BlockInstanceXform(good_block)
    translation = clr.StrongBox[Rhino.Geometry.Vector3d](
        Rhino.Geometry.Vector3d(0, 0, 0))
    rotation = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
    othor = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
    diagono = clr.StrongBox[Rhino.Geometry.Vector3d](
        Rhino.Geometry.Vector3d(0, 0, 0))
    transform.DecomposeAffine(translation, rotation, othor, diagono)
    # diagono is the unoiform scale XYZ

    map(lambda x: replace_block_transform(x, diagono), bad_blocks)


def replace_block_transform(bad_block, source_diagono):
    transform = rs.BlockInstanceXform(bad_block)

    translation = clr.StrongBox[Rhino.Geometry.Vector3d](
        Rhino.Geometry.Vector3d(0, 0, 0))
    rotation = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
    othor = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
    diagono = clr.StrongBox[Rhino.Geometry.Vector3d](
        Rhino.Geometry.Vector3d(0, 0, 0))
    transform.DecomposeAffine(translation, rotation, othor, diagono)

    """
    print(translation)
    print(rotation)
    print(othor)
    print(diagono)
    print(source_diagono)
    """

    translate_X, translate_Y, translate_Z = translation.X, translation.Y, translation.Z
    scale_X, scale_Y, scale_Z = source_diagono.X, source_diagono.Y, source_diagono.Z
    source_scale_transform = rs.XformScale((scale_X, scale_Y, scale_Z))
    translate_transform = rs.XformTranslation(
        (translate_X, translate_Y, translate_Z))
    othor_transform = convert_transform(othor)
    rotation_transform = convert_transform(rotation)

    # in multiple, AxB, you applu B first, then A
    reconstructed_transform = Rhino.Geometry.Transform.Multiply(
        othor_transform, source_scale_transform)
    reconstructed_transform = Rhino.Geometry.Transform.Multiply(
        rotation_transform, reconstructed_transform)
    reconstructed_transform = Rhino.Geometry.Transform.Multiply(
        translate_transform, reconstructed_transform)

    bad_block_name = rs.BlockInstanceName(bad_block)
    rs.InsertBlock2(bad_block_name, reconstructed_transform)
    rs.DeleteObject(bad_block)


def convert_transform(strongbox_transform):
    return strongbox_transform.Clone()
    transform = Rhino.Geometry.Transform()
    for i in range(4):
        for j in range(4):
            transform[i, j] = strongbox_transform[i][j]
    return transform


if __name__ == "__main__":
    match_block_distortion()
