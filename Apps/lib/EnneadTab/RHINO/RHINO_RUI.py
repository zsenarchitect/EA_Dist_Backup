import ENVIRONMENT
import FOLDER


if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import rhinoscriptsyntax as rs
    import Rhino # pyright: ignore


def update_rui_v7():
    

    for tool_bar_name in rs.ToolbarCollectionNames():
        if "enneadtab" in tool_bar_name.lower():
            rs.CloseToolbarCollection(tool_bar_name, prompt=False)

    rui_file = "EnneadTab_For_Rhino_Classic.rui"

    my_local_version = FOLDER.copy_file_to_local_dump_folder(ENVIRONMENT.RHINO_FOLDER + "\\" + rui_file)
    rs.OpenToolbarCollection(my_local_version)

def update_rui_v8():
    # todo: figure out a way to deal with R8 rui handle disapear after restart
    good_rui_file = "EnneadTab_For_Rhino_Modern.rui"
    good_rui_toolbar_name = good_rui_file.replace(".rui", "")

    for tool_bar_name in rs.ToolbarCollectionNames():
        # do not close current oppedn mordern rui so it will not deacivate and disappear after restart
        if good_rui_toolbar_name == tool_bar_name:
            continue

        if "enneadtab" in tool_bar_name.lower():
            rs.CloseToolbarCollection(tool_bar_name, prompt=False)


    my_local_version = FOLDER.copy_file_to_local_dump_folder(ENVIRONMENT.RHINO_FOLDER + "\\" + good_rui_file)
    rs.OpenToolbarCollection(my_local_version)




def update_my_rui():
    if rs.ExeVersion() >= 8:
        update_rui_v8()
    else:
        update_rui_v7()


    



def add_startup_script():
    
    """hear me out here:
    python cannot add startup script directly
   
    i use this python script C to call rhino script B to call rhino script A, which is the command alias
    This will not run the startup command, it just add to the start sequence.
    """
    
    rvb_satrtup_modifier_script = "{}\\Ennead+.menu\\get_latest.button\\StartupEnable.rvb".format(ENVIRONMENT.RHINO_FOLDER)
    Rhino.RhinoApp.RunScript("-LoadScript " + rvb_satrtup_modifier_script, True)
    
def unit_test():
    pass

    
if __name__ == "__main__":

    update_my_rui()