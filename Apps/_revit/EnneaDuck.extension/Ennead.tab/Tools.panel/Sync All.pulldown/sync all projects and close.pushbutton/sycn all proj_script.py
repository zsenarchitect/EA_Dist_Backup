__doc__ = "for every open document(except family document), it sync with central. Then Close"
__title__ = "Sync All Open Proj and Close"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=28744"
__tip__ = True

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