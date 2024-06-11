__doc__ = "xxxxxx"
__title__ = "[Obsolate]21_Open Many\nBili Proj"

from pyrevit import forms, DB, revit, script
import System
import EA_UTILITY
import EnneadTab
class OpenCloudCallBack(DB.IOpenFromCloudCallback):
    def OnOpenConflict (self):
        return False


def export_all_docs():
    docs = app.Documents
    for doc in docs:

        if doc.IsLinked or doc.IsFamilyDocument:
            continue
        sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
        print(main_output)
        main_output.print_md( new_doc.Title)
        for sheet in sheets:
            main_output.print_md( sheet.Name)

################## main code below #####################
main_output = script.get_output()
main_output.close_others()


print(main_output)
#script.exit()
#cloud_path = "BIM 360://2135_Bilibili Shanghai Headquarters/2135_BiliBili SH HQ_N4.rvt"
cloud_path = r"BIM 360://2135_Bilibili Shanghai Headquarters/***.rvt"


GUID_list = [
        ["2135_BiliBili SH HQ_N3", "7bb487db-c370-408e-9a97-9441ef91c51c", "9652bd4b-03b2-4016-8af3-2742efa27968"],
        ["2135_BiliBili SH HQ_N4", "7bb487db-c370-408e-9a97-9441ef91c51c", "ca4336c2-ea68-4d16-97a5-32c09a7c607b"],
        ["2135_BiliBili SH HQ_N5", "7bb487db-c370-408e-9a97-9441ef91c51c", "bc6dc5d7-8833-4564-aa74-c64dc14f50a1"],
        ["2135_BiliBili SH HQ_N6", "7bb487db-c370-408e-9a97-9441ef91c51c", "50ce9b1b-6ecf-4a7b-aec1-8f0af5acfe06"],
        ["2135_BiliBili SH HQ_Site", "7bb487db-c370-408e-9a97-9441ef91c51c", "8e18fa0b-26ec-4ddd-99d1-799953f5e2b3"]
        ]


target_list = ["2135_BiliBili SH HQ_N4",
                "2135_BiliBili SH HQ_N5",
                "2135_BiliBili SH HQ_N6",
                "2135_BiliBili SH HQ_N3",
                "2135_BiliBili SH HQ_Site"]

app = revit.doc.Application
docs = app.Documents
for doc in docs:

    if doc.IsLinked or doc.IsFamilyDocument:
        continue
    print("#####")
    main_output.print_md("# {}".format( doc.Title) )
    cloud_model_path = doc.GetCloudModelPath().CentralServerPath
    print(cloud_model_path)
    print(DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(doc.GetCloudModelPath()))
    model_path = DB.ModelPathUtils.ConvertUserVisiblePathToModelPath (cloud_model_path)



    print(doc.PathName)
    print("--------")
    print("{} path".format(doc.Title))
    cloud_project_GUID = doc.GetCloudModelPath().GetProjectGUID ()
    cloud_model_GUID = doc.GetCloudModelPath().GetModelGUID ()

    print(cloud_project_GUID)
    print(cloud_model_GUID)
    print(DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(cloud_project_GUID, cloud_model_GUID ))
    #if doc.Title in target_list:
    target_list.remove(doc.Title)

print(target_list)
print("***********"*3)
script.exit()


EA_UTILITY.set_open_hook_depressed(True)

for target in target_list:



    """
    print("---")
    path_str = cloud_path.replace("***", target)
    print(path_str)
    path = DB.ModelPathUtils.ConvertUserVisiblePathToModelPath (path_str)
    print(path)
    open_options = DB.OpenOptions()
    callback = OpenCloudCallBack()
    print(app.OpenDocumentFile(path,)
                                DB.OpenOptions())
    """

    for data in GUID_list:
        if data[0] == target:
            break

    #print data[1]
    #print data[2]
    cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(System.Guid(data[1]), System.Guid(data[2]) )
    open_options = DB.OpenOptions()
    new_doc = app.OpenDocumentFile(cloud_path,
                                open_options)
    main_output = script.get_output()
    main_output.close()

    main_output.print_md( "background open file {}".format(target))

    export_all_docs()
    new_doc.Close(False)


    """
    try:
        print("---")
        path_str = cloud_path.replace("***", target)
        print(path_str)
        path = DB.ModelPathUtils.ConvertUserVisiblePathToModelPath (path_str)
        open_options = DB.OpenOptions()
        callback = OpenCloudCallBack()
        print(app.OpenDocumentFile(path,)
                                    DB.OpenOptions(),
                                    OpenCloudCallBack())
        print("\tOpen {} Success.".format(target))
    except Exception as e:
        print("\topen {} Failed.\n{}\t".format(target, e))
    """

sheets = DB.FilteredElementCollector(reivt.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

EA_UTILITY.set_open_hook_depressed(False)
main_output.close_others(all_open_outputs = True)
main_output.print_md( "tool finished")
