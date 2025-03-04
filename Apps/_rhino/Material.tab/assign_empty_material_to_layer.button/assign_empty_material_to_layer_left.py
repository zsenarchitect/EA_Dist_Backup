
__title__ = "AssignEmptyMaterialToLayer"
__doc__ = "Same as EA_AssignEmptyMaterial"


from EnneadTab import ERROR_HANDLE, LOG
import rhinoscriptsyntax as rs
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def assign_empty_material_to_layer():

    rs.Command("EA_AssignEmptyMaterial _Enter")

if __name__ == "__main__":
    assign_empty_material_to_layer()
