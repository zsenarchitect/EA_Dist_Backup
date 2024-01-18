__doc__ = "for every open document(except family document), it sync with central. Then Close"
__title__ = "Sync All Open Proj and Close"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=28744"
__tip__ = True

import EnneadTab
from pyrevit import script

uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()

@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close()
    import ENNEAD_LOG
    ENNEAD_LOG.use_enneadtab(coin_change = 30, tool_used = "Sync All Projs. and Close", show_toast = True)
    output = script.get_output()
    killtime = 30
    output.self_destruct(killtime)

################## main code below #####################
if __name__ == "__main__":
    main()