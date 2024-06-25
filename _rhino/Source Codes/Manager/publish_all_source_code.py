import sys

sys.path.append("..\lib")
import EnneadTab


import rhinoscriptsyntax as rs

@EnneadTab.ERROR_HANDLE.try_catch_error
def main():

    items = ["Yes, after core script also copy backup to archive(slowwwwer)", "No, just core scripts(quicker)"]
    res = rs.ListBox(items, message = "publish with Deep copy to archive?", title = "Repo Manager", default = items[1])
    if not res:
        return
    deep_copy = True if res == items[0] else False
    EnneadTab.VERSION_CONTROL.publish_Rhino_source_code(deep_copy)

    print ("done")



if  __name__ == "__main__" :

    main()
