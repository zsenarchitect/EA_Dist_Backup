from pyrevit import EXEC_PARAMS
from pyrevit.coreutils import envvars
import EnneadTab



def check_is_template_folder():
    if envvars.get_pyrevit_env_var("IS_L_DRIVE_WORKING_ALARM_DISABLED"):
        return
    path = EXEC_PARAMS.event_args.PathName
    if not EnneadTab.USER.is_SZ():
        return

    extension = EnneadTab.FOLDER.get_file_extension_from_path(path)
    #print extension
    if extension not in [".rft", ".rfa"]:
        return
    if r"L:\4b_Applied Computing\01_Revit\02_Template" in path or r"L:\4b_Applied Computing\01_Revit\03_Library" in path:
        EnneadTab.REVIT.REVIT_FORMS.notification(self_destruct = 3,main_text = "This is a family in L drive...", sub_text = path)

@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():

    
    check_is_template_folder()

##########################################

if __name__ == '__main__':
    main()