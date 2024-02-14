#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Review\nIn Miro"

import shutil
from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB 
import os
# from Autodesk.Revit import UI
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()
            
@EnneadTab.ERROR_HANDLE.try_catch_error
def update_miro():

    print ("Note: At the moment CBI does not allow me to connect to Miro, so your team can ask me for a board on my personal account.")
    key = "recent_miro_url"
    recent_url = EnneadTab.DATA_FILE.get_revit_ui_setting_data(key_defaule_value=(key,"https://miro.com/app/board/uXjVNtUGSrc=/"))
    miro_url = forms.ask_for_string(
        prompt = "Please input the Miro board URL:",
        default= recent_url,
        title = "Makrup Sheet In Miro")

    print ("Miro URL: " + miro_url)
    EnneadTab.DATA_FILE.set_revit_ui_setting_data(key, miro_url)

    sheets = forms.select_sheets(title = "Select sheets to update")
    if not sheets:
        return

    dump_folder = "{}\\miro_dump".format(EnneadTab.FOLDER.get_EA_local_dump_folder())

    # make sure everytig is the lastest in this folder
    if os.path.exists(dump_folder):
        shutil.rmtree(dump_folder)
    os.mkdir(dump_folder)

    for i, sheet in enumerate(sheets):
        sheet_name = sheet.Name
        sheet_num = sheet.SheetNumber
        guid = sheet.UniqueId
        file = "{}^{}^{}.jpg".format(guid,
                                        sheet_num,
                                        sheet_name)

        EnneadTab.NOTIFICATION.messenger ("Exporting image {}/{}==> {}:{}".format(i + 1, len(sheets), sheet_num, sheet_name))
        EnneadTab.REVIT.REVIT_EXPORT.export_image(sheet, file, dump_folder)
    
    EnneadTab.NOTIFICATION.duck_pop("Image Export done!\nPreparing to upload to Miro!")
    
    with EnneadTab.DATA_FILE.update_data("miro.json") as data:
        data['url'] = miro_url
        data["images"] = [os.path.join(dump_folder, f) for f in os.listdir(dump_folder)]
        data["app"] = "revit_sheet"

    EnneadTab.EXE.open_exe("MIRO")
    


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_miro()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







