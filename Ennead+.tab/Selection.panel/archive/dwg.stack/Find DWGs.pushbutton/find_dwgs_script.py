#from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils

output = script.get_output()

__title__ = "Find DWGs\nimport&link"
__doc__ = 'Find imported and linked DWG view names and total number count.'
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=29731"

def get_dwgs():
    try:
        dwgs_list = DB.FilteredElementCollector(revit.doc).OfClass(DB.ImportInstance).WhereElementIsNotElementType().ToElements()
    except:
        print("fail to get DWGs. Action cancelled.")
        script.exit()


    list(dwgs_list).sort(key = lambda x: x.LookupParameter("Name"), reverse = True)
    return dwgs_list

def GetParamByName(el,name):

    for para in el.Parameters:
        #print para.Definition.Name #enable this to see what parameter is available
        if para.Definition.Name == name:
            #print "OK, found para ID" + str(para.Id)

            #return el.LookupParameter(name).Id # can be used to return para ID
            return para

def is_linked(dwg):

    if dwg.IsLinked:
        return True
    else:
        return False


def output_info(elements):
    if len(elements) == 0:
        print("None found.")
        return
    for el in elements:
        print("DWG Id = {} --->{}".format(el.Id, output.linkify(el.Id, title = "Select DWG")))

        """
        for para in el.Parameters:
            print(para.Definition.Name, para.AsString())
        """

        """
        print(el.WorksetId, revit.doc,DB.Document)
        """





        dwg_name = GetParamByName(el, "Name").AsString()
        workset = revit.doc.GetWorksetTable().GetWorkset(el.WorksetId).Name
        print ("DWG name = {}".format(dwg_name))
        creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc, el.Id).Creator
        print("Initially created by [{}]".format(creator))

        if el.ViewSpecific:
            view_id = el.OwnerViewId
            try:#revit 2020 and 2019 use diffrent propety for names
                view_name = revit.doc.GetElement(view_id).ViewName
            except AttributeError:
                view_name = revit.doc.GetElement(view_id).Name

            print ("It is view specific 2D dwg in view '{}' --->{}".format(view_name, output.linkify(view_id, title = "Go To View")))

            if el.IsHidden(revit.doc.GetElement(view_id)):
                print("It is currently hidden in the view.")
        else:
            print ("It is 3D dwg. ")
            print ("Workset = {}".format(workset))


        print(seperation_small)


def list_dwg_size():

    print("\n\n\nrank size")
    dwgs_list = DB.FilteredElementCollector(revit.doc).OfClass(DB.CADLinkType ).ToElements()
    #print dwgs_list
    dwg_links = []
    for dwg in dwgs_list:
        try:
            file_ref = dwg.GetExternalFileReference ()
        except Exception as e:
            print (e)
            print(dwg.LookupParameter("Type Name").AsString())
            continue
        file_path = file_ref.GetPath()
        file_path = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(file_path)
        #print file_path

        file_size = get_filesize(file_path, return_bytes = True)


        dwg_links.append((file_path, file_size))
        #print file_path.CentralServerPath
        #print file_path.ToString()

    dwg_links.sort(key = lambda x: x[1], reverse = True)
    for item in dwg_links:
        output.print_md( "**{}** --> {}".format( get_filesize(item[0], return_bytes = False), item[0]))
    print("\n\nrank size done")


def get_filesize(filepath, return_bytes = False):
    import os.path as OP
    import math
    try:
        size_bytes = int(OP.getsize(filepath))
    except:
        return "N/A"
    if return_bytes:
        return size_bytes

    if size_bytes == -1:
        return "N/A"
    size_unit = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    size = round(size_bytes / p, 2)
    return "{}{}".format(size, size_unit[i])


seperation_big = "################################################################"
seperation_small = "----------------"
seperation_special = "----"
#-------------main code below-------------
output = script.get_output()
output.close_others()

#get all dwgs in project
all_dwgs = get_dwgs()


#check if it is linked
dwgs_imported = []
dwgs_linked = []
for dwg in all_dwgs:
    if is_linked(dwg):
        dwgs_linked.append(dwg)
    else:
        dwgs_imported.append(dwg)

#output info

output.print_md("#" + seperation_special + "Linked DWGs Below" + seperation_special)
output_info(dwgs_linked)
print(seperation_big)
output.print_md("#" + seperation_special + "Imported DWGs Below" + seperation_special)
output_info(dwgs_imported)


#do summary
print(seperation_big)
output.print_md("# Summary")
output.print_md("Total {} **linked** DWGs found.".format(len(dwgs_linked)))
output.print_md("Total {} **imported** DWGs found.".format(len(dwgs_imported)))
if len(dwgs_imported)>5:
    print("Too many imported DWGs.")
print("If possible, use as little as possible imported DWGs.")

list_dwg_size()


print("\n"*8)
output.print_md( "***Tool Tips 1: If you click to jump to dwg first, Revit search view could be slow, so it is better to jump to the specific listed view first before select the dwg.***")
output.print_md( "***Tool Tips 2: You can pin the window to keep it stay on top. Very handy when you have multiple dwg to track.***")
path = script.get_bundle_file('pin.png')
output.print_image(path)
