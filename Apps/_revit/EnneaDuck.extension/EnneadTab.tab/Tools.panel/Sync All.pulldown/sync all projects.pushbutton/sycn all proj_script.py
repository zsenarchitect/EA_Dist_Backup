__doc__ = "Project synchronization tool that keeps all your work up-to-date with a single click. This utility automatically synchronizes every open Revit project with its central file while keeping them open for continued work. Perfect for regular syncing throughout the day to prevent data loss and ensure changes are visible to your team."
__title__ = "Sync All\nOpen Proj"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=28744"
__tip__ = True
from pyrevit import  script

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION

doc = REVIT_APPLICATION.get_doc()



from EnneadTab.REVIT import REVIT_SYNC
from EnneadTab import SOUND, ERROR_HANDLE, LOG



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    

    REVIT_SYNC.sync_and_close(close_others = False)
    SOUND.play_sound()
    output = script.get_output()
    killtime = 30
    output.self_destruct(killtime)
################## main code below #####################
if __name__ == "__main__":

    main()
