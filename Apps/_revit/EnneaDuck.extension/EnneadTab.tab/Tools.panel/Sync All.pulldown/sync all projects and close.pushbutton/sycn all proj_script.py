__doc__ = "End-of-day project synchronization tool that tidies up your work environment with one click. This utility automatically synchronizes all open project documents with their central files, then cleanly closes everything. Perfect for when you're heading home and want to make sure all your work is safely submitted to the central model."
__title__ = "Sync All Open Proj and Close"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=28744"
__tip__ = True
__is_popular__ = True
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SYNC, REVIT_EVENT
from EnneadTab import ERROR_HANDLE, LOG
from pyrevit import script

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    REVIT_EVENT.set_all_sync_closing(True)
    REVIT_SYNC.sync_and_close()
    REVIT_EVENT.set_all_sync_closing(False)

    output = script.get_output()
    killtime = 30
    output.self_destruct(killtime)

################## main code below #####################
if __name__ == "__main__":
    main()