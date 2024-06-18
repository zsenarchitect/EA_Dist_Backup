import rhinoscriptsyntax as rs
import os
import sys
import traceback
sys.path.append("..\lib")

import EnneadTab




def override_user_version(original):



    folder = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Users"
    folders = EnneadTab.FOLDER.get_filenames_in_folder(folder)
    for user_folder in folders:
        target = "{}\{}\EnneadTab.rui".format(folder, user_folder)
        try:
            EnneadTab.FOLDER.copy_file(original, target)
        except Exception as e:
            print (e)


@EnneadTab.ERROR_HANDLE.try_catch_error
def publish_latest_toolbar(show_feedback = False):
    try:
        EnneadTab.RHINO.RHINO_RUI.publish_rui()
    except:
        print (traceback.format_exc())
        EnneadTab.NOTIFICATION.duck_pop("new publisher failed")
        old_publisher(show_feedback)


def old_publisher(show_feedback):
    if show_feedback:
        options = ["Exit without action", "Confirm"]
        res = rs.ListBox(items = options, message =  "Wait...Only proceed if your name is Sen Zhang", title = "STOP!", default = options[0])
        if res != options[1]:
            return


    save_res = rs.SaveToolbarCollection("EnneadTab")
    #rs.MessageBox(message = "saving 'EnneadTab.rui' file = {}".format(res), buttons= 0 | 48, title = "EA monitor")

    original = r"{}\Working\EnneadTab.rui".format(EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_RHINO)
    target = r"{}\EnneadTab for Rhino\EnneadTab.rui".format(EnneadTab.ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)

    #copy rui file from working folder to L drive
    EnneadTab.FOLDER.copy_file(original, target)



    override_user_version(original)




    purge_bad_rui_baks()

    toolbar_details = ""
    names = rs.ToolbarCollectionNames()
    if names:
        for name in names:
            toolbar_details += "\t\t\t\t{}:   {}\n".format(name, rs.ToolbarCollectionPath(name))

    if show_feedback:
        rs.TextOut(message = "Current Toolbar Collection\n{}".format(toolbar_details))

        #rs.MessageBox(message = "Publishing Done.\n\nSave 'EnneadTab.rui' file = {}".format(save_res), buttons= 0 | 48, title = "EA monitor")
        EnneadTab.NOTIFICATION.toast(main_text = r'Save "EnneadTab.rui" file = {}'.format(save_res), sub_text = "Publishing Done.")





def purge_bad_rui_baks():
    folder = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\EnneadTab for Rhino"
    for file in os.listdir(folder):
        if not file.endswith(".rui"):
            os.remove(os.path.join(folder, file))



##########################################################################

if( __name__ == "__main__" ):

    publish_latest_toolbar(show_feedback = True)
