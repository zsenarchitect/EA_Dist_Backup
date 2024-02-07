
from pyrevit import script
from pyrevit import forms
from Autodesk.Revit import DB 
doc = __revit__.ActiveUIDocument.Document
import EA_UTILITY
import EnneadTab

__title__ = "Open\nDWGs"
__doc__ = 'open dwgs for inspection'
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=29731"
def open_dwg_by_size():


    dwgs_list = DB.FilteredElementCollector(doc).OfClass(DB.CADLinkType ).ToElements()
    #print dwgs_list
    dwg_links = []
    for dwg in dwgs_list:
        try:
            file_ref = dwg.GetExternalFileReference ()
        except Exception as e:
            print (e)
            print dwg.LookupParameter("Type Name").AsString()
            continue
        file_path = file_ref.GetPath()
        file_path = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(file_path)
        #print file_path

        file_size = get_filesize(file_path)


        dwg_links.append((file_path, file_size))
        #print file_path.CentralServerPath
        #print file_path.ToString()

    dwg_links.sort(key = lambda x: x[1], reverse = True)

    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "**{}** --> {}".format( format_bytes(self.item[1]), self.item[0])

    ops = [MyOption(x) for x in dwg_links]
    res = forms.SelectFromList.show(ops,
                                    multiselect = True,
                                    button_name = 'Open Dwg',
                                    width = 1500,
                                    title = "N/A means cannot access size, likely saved on local drive. Dwg above 3mb are considered bad.")
    output.show()
    if res is None:
        return
    dwg_paths = [x[0] for x in res]
    for dwg_path in dwg_paths:
        try:
            EA_UTILITY.open_file_in_default_application(dwg_path)
        except:
            print "Cannot open file: {}".format(dwg_path)


def get_filesize(filepath, return_bytes = False):
    import os.path as OP

    try:
        size_bytes = int(OP.getsize(filepath))
    except:
        return "N/A"
    return size_bytes

def format_bytes(size_bytes):
    import math
    if size_bytes == -1:
        return "N/A"
    if isinstance(size_bytes, str):
        return "N/A"
    size_unit = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    size = round(size_bytes / p, 2)
    return "{}{}".format(size, size_unit[i])



#-------------main code below-------------
output = script.get_output()
output.close_others()

#get all dwgs in project
open_dwg_by_size()
