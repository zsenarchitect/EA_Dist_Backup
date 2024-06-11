__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "!!!save all usernames"

from pyrevit import DB, revit
import EA_UTILITY
import EnneadTab

################## main code below #####################

# print EA_UTILITY.get_real_name()

views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).ToElements()
for view in views:
    info = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc, view.Id)
    EA_UTILITY.save_autodesk_name(info.Creator)
    EA_UTILITY.save_autodesk_name(info.LastChangedBy)
    EA_UTILITY.save_autodesk_name(info.Owner)
