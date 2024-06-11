#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "For the views not placed on sheet, you can export them by the view creator name, and view them as jpg in a folder to decide if you want to delete. This is handy after you have noticed 100+ working view from different people and only want to clean views related to you or a specific person."
__title__ = "Export NoSheet View As Jpgs"
import ENNEAD_LOG
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
import time
import os

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def created_by_who(view):
    view_history = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, view.Id)
    return view_history.Creator

def get_view_group(view):
    out = ""
    try:
        view_group = view.LookupParameter("Views_$Group").AsString()
        view_series = view.LookupParameter("Views_$Series").AsString()
        out = "--->[ViewGroup = {}, ViewSeries = {}]".format(view_group, view_series)
    except Exception as e:
        pass
    return out


def export_image_from_view(view, doc, adding_creator):

    print("-----")
    global counter
    counter += 1

    time_start = time.time()

    file_name = view.Name
    if adding_creator:
        file_name = "Created By [{}]_{}".format(created_by_who(view), view.Name)

    """
    file_name = file_name.replace("{", "[")
    file_name = file_name.replace("}", "]")
    """

    print("preparing [{}].jpg".format(file_name))
    #EA_UTILITY.remove_exisitng_file_in_folder(output_folder, file_name + ".jpg")

    #output_folder = "{}\Documents".format(os.environ["USERPROFILE"])
    output_folder = "{}\Documents\{}".format(os.environ["USERPROFILE"], "###UnSheeted Views Jpgs for [{}]".format(doc.Title))

    #dir = os.path.join("C:\\","temp","python")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)


    opts = DB.ImageExportOptions()
    opts.FilePath = output_folder + r'\{}.jpg'.format(file_name)
    opts.ImageResolution = DB.ImageResolution.DPI_300
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 6000
    opts.SetViewsAndSheets(EA_UTILITY.list_to_system_list([view.Id]))

    attempt = 0

    while True:
        if attempt > 0:
            break
        try:
            doc.ExportImage(opts)
            print("Image export succesfully")
            break
        except Exception as e:
            attempt += 1
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

            else:
                print("failed export view [{}] becasue: {}".format(view.Name, e))
                return
    time_end = time.time()
    #cleanup_jpg_name()
    print("view to Jpg takes {} seconds".format( time_end - time_start))
    cleanup_jpg_name(output_folder, file_name, str(view.ViewType))
    #add_to_log(file_name + ".jpg", time_end - time_start)
    EA_UTILITY.show_toast(app_name = "EnneadTab Exporter",
                            title = "[{}.jpg] saved.".format(file_name),
                            message = "{} more to do in current document".format(total - counter))



def cleanup_jpg_name(output_folder, desired_name, keyword):
    EA_UTILITY.remove_exisitng_file_in_folder(output_folder, desired_name + ".jpg")

    #print keyword

    file_names = os.listdir(output_folder)

    for file_name in file_names:
        if desired_name in file_name and ".jpg" in file_name.lower():
            #new_name = file_name.split(keyword)[0]
            new_name = desired_name

            try:
                os.rename(os.path.join(output_folder, file_name),os.path.join(output_folder, new_name + ".jpg"))
            except Exception as e:
                print("skip {} becasue: {}".format(file_name, e))

def is_no_sheet(view):

    if str(view.ViewType) in [ "Legend", "Schedule", "SystemBrowser", "ProjectBrowser", "DrawingSheet"]:
        return False
    if "revision" in view.Name.lower():
        return False
    if "schedule" in view.Name.lower():
        return False
    if view.IsTemplate:
        return False
    if view.LookupParameter("Sheet Number") is None:
        return True
    if view.LookupParameter("Sheet Number").AsString() == "---":
        return True
    return False



def main():
    opts = ["Yes", "No"]
    res = EA_UTILITY.dialogue(main_text = "Should it prefix the creator name when doing the JPG export?", sub_text = "So even in Windows folder you can see this info.", options = opts)
    if not res:
        return
    if res == opts[0]:
        adding_creator = True
    else:
        adding_creator = False

    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()

    no_sheet_views = filter(is_no_sheet, all_views)
    no_sheet_views.sort(key = lambda x:x.Name)


    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{}{}".format(self.item.Name,  get_view_group(self.item))

    #no_sheet_views = [MyOption(x) for x in no_sheet_views]
    collection = dict()
    collection["Everyone"] = [MyOption(x) for x in no_sheet_views]
    for view in no_sheet_views:
        creator = created_by_who(view)
        if creator in collection.keys():
            collection[creator].append(MyOption(view))
        else:
            collection[creator] = [MyOption(view)]
    no_sheet_views = forms.SelectFromList.show(collection,
                                                multiselect = True,
                                                name_attr = "Name",
                                                title = "Search the view names that you want to export.",
                                                width = 1200,
                                                group_selector_title = "Group by Creator:",
                                                default_group = "Everyone")
    if no_sheet_views is None:
        return
    global total
    total = len(no_sheet_views)
    global counter
    counter = 0

    t = DB.Transaction(doc, "export no sheet views")
    t.Start()
    will_sync_and_close = EA_UTILITY.do_you_want_to_sync_and_close_after_done()
    map(lambda x: export_image_from_view(x, doc, adding_creator), no_sheet_views)
    t.Commit()


    if will_sync_and_close:
        EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close()


    print("################### finish")
################## main code below #####################
output = script.get_output()
output.close_others()

if __name__ == "__main__":
    main()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__, show_toast = True)
