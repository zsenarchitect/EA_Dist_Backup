
__title__ = "Turtorial"
__doc__ = "This button does Turtorial when left click"
import os
import rhinoscriptsyntax as rs
import subprocess

from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab import FOLDER, EXE, ENVIRONMENT
from EnneadTab.RHINO import RHINO_FORMS





def open_file_by_selection(folder, selected_opt):
    filepath = folder + "\\" + selected_opt
    EXE.try_open_app(filepath)

def open_gh_by_selection(folder, selected_opt):
    shortcut_path = folder + "\\" + selected_opt

    import sys
    sys.path.append("..\lib")
    from EnneadTab import SHORTCUT
    target = SHORTCUT.parse_shortcut(shortcut_path)



    rs.Command("-Grasshopper Document Open \"{}\" Enter".format(target))
 

def open_local_tutorial():
    folder = '{}\\03_Rhino\\12_EnneadTab for Rhino\\Documents\\Tutorials'.format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)
    files = os.listdir(folder)
    special_folder = "#PDF in this directory are reference only"
    files.remove(special_folder)
    special_folder = "#If Possible, place a shortcut link instead of actual original file"
    files.remove(special_folder)
    """
    for file in files:
        print(file)
    """
    keyword = "<Open Entire Code Folder...>"
    files.insert(0, keyword)
    selected_opt = RHINO_FORMS.select_from_list(files, multi_select = False, message = "How do I....?")
    if not selected_opt:
        return


    if keyword == selected_opt:

        path = "{}\\03_Rhino\\12_EnneadTab for Rhino\\Documents\\Tutorials\\#PDF in this directory are reference only".format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)
        subprocess.Popen(r'explorer /select, {}'.format(path))
        return

    if ".gh" in selected_opt:
        open_gh_by_selection(folder, selected_opt)
        return
    
    open_file_by_selection(folder,selected_opt)

def open_playlist():

    playlist = r"https://youtube.com/playlist?list=PLz3VQzyVrU1iyoGV-kzWhCPsmh9cQWWoV"
    import webbrowser

    #webbrowser.open(playlist)
    webbrowser.open_new(playlist)



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def turtorial():

    opts = ["L drive contents(PDFs, Docs, GH Scripts, Videos)", "EnneadTab YouTube Playlist"]
    res = rs.PopupMenu(items = opts, modes = [0, 0])


    if res == 0:

        open_local_tutorial()
    else:

        open_playlist()


if __name__ == "__main__":
    turtorial()