import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


@EnneadTab.ERROR_HANDLE.try_catch_error
def set_unique_unit():

    unit_name = rs.StringBox(message = "Your Unit Name", default_value = EnneadTab.USER.get_user_name(), title = "Set Unique Unit")
    if not unit_name:
        return


    factor = rs.RealBox(message = "Ratio of unit [{}] to meter".format(unit_name), default_number = 1, title = "Set Unique Unit", minimum = 0.000000000000001, maximum = None)
    if not factor:
        return

    opts = ["Yes, scale it so size is same", "No, keep digits, just replace unit"]
    res = rs.ListBox(opts, message = "Should the model be scaled based on this unit change?", title = "Set Unique Unit")
    if not res:
        return
    will_scale = True if res == opts[0] else False
    sc.doc.SetCustomUnitSystem (True, unit_name, factor, will_scale)


######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    set_unique_unit()
