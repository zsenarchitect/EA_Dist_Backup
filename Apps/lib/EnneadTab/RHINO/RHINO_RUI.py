import ENVIRONMENT
import FOLDER


if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import rhinoscriptsyntax as rs
    import Rhino # pyright: ignore


def update_my_rui():

    rs.CloseToolbarCollection("EnneadTab_For_Rhino_Installer", prompt=False)
    # close current toolbar so not holding it.
    rs.CloseToolbarCollection("EnneadTab_For_Rhino", prompt=False)

    # close existing toolbar from 1.0 if exists
    if "EnneadTab" in rs.ToolbarCollectionNames():
        rs.CloseToolbarCollection("EnneadTab.rui", prompt=False)

    my_local_version = FOLDER.copy_file_to_local_dump_folder(ENVIRONMENT.RHINO_FOLDER + "\\EnneadTab_For_Rhino.rui")
    rs.OpenToolbarCollection(my_local_version)


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