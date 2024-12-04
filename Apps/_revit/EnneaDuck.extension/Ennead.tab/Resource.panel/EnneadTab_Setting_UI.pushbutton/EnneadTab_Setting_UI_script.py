#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """All basic setting for the EnneadTab for Revit.
+Tabs avaliablity
+Tab Color.
+Switching between Lite and Pro version.
+Notification Setting.
+Duck Setting.
etc"""
__title__ = "EnneadTab\nSetting"
__context__ = "zero-doc"
__tip__ = [__doc__,
           "You can enjoy much more functions from the Ennead+ Version instead of staying in Lite Version."]

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent # pyright: ignore 
from Autodesk.Revit.Exceptions import InvalidOperationException # pyright: ignore 


import System # pyright: ignore 



import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS
from EnneadTab import DATA_FILE, USER, NOTIFICATION, ENVIRONMENT, SPEAK, ERROR_HANDLE, FOLDER, IMAGE, LOG, DUCK, CONFIG


from pyrevit import script
from pyrevit.coreutils import ribbon
try:
    from pyrevit.revit import tabs as TABS
except:
    NOTIFICATION.messenger("Please update pyrevit to 4.8+.")





uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True



@ERROR_HANDLE.try_catch_error()
def change_extension_folder(is_force_tester, include_game):
    from EnneadTab import NOTIFICATION # to be resolved, there is a scope leak so have to import again..
    NOTIFICATION.messenger("This feature is disabled for now")
    return
    """this arg has no effect"""


    from pyrevit.userconfig import user_config
    from pyrevit.loader.sessionmgr import execute_command
    """Reads the user extension folders and updates the list"""
    current_external_folders = user_config.get_thirdparty_ext_root_dirs(include_default=False)
    print (current_external_folders)



    beta_version_extension_folder = filter(lambda x: "Published_Beta_Version"  in x, current_external_folders)
    stable_version_extension_folder = filter(lambda x: x not in beta_version_extension_folder, current_external_folders)
    print (beta_version_extension_folder)
    print (stable_version_extension_folder)




    enneadtab_stable_version_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published"
    enneadtab_beta_tester_version_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version"
    enneadtab_game_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Misc"

    
    from EnneadTab.REVIT import REVIT_APPLICATION
    from EnneadTab import DATA_FILE, USER, NOTIFICATION, ENVIRONMENT, SPEAK, ERROR_HANDLE, FOLDER

    if not USER.IS_DEVELOPER:
            
        
        if enneadtab_beta_tester_version_folder  in current_external_folders:
            current_external_folders.remove(enneadtab_beta_tester_version_folder)
        if enneadtab_stable_version_folder not in current_external_folders:
            current_external_folders.append(enneadtab_stable_version_folder)


    if include_game:
        if enneadtab_game_folder not in current_external_folders:
            current_external_folders.append(enneadtab_game_folder)
    else:
        if enneadtab_game_folder in current_external_folders:
            current_external_folders.remove(enneadtab_game_folder)
            
            
    user_config.set_thirdparty_ext_root_dirs(current_external_folders)
    from pyrevit.loader import sessionmgr
    sessionmgr.reload_pyrevit()
    return
    import pyrevitcore_globals
    execute_command(pyrevitcore_globals.PYREVIT_CORE_RELOAD_COMMAND_NAME)
    return




# A simple WPF form used to call the ExternalEvent
class MainSetting(REVIT_FORMS.EnneadTabModelessForm):

    def __init__(self, title, summary, xaml_file_name, **kwargs):
        super(MainSetting, self).__init__(title, summary, xaml_file_name, **kwargs)
        # call supper first so can connect to xaml to get all compenent, 
        # otherwise the load setting will have nothing to load
        self.Height = 800
        self.load_setting()

    @ERROR_HANDLE.try_catch_error()
    def load_setting(self):
        super(MainSetting, self).load_setting(CONFIG.GLOBAL_SETTING_FILE)
    

        self.toggle_bt_is_tab_color.IsChecked = TABS.get_doc_colorizer_state()
        self.update_UI()
            

    @ERROR_HANDLE.try_catch_error()
    def save_setting(self):
        super(MainSetting, self).save_setting(CONFIG.GLOBAL_SETTING_FILE)

        #  the handle of say or not is inside speak
        SPEAK.speak("I am back! How are you doing?")


    @ERROR_HANDLE.try_catch_error()
    def send_duck_click(self, sender, args):
        DUCK.quack()
 

    @ERROR_HANDLE.try_catch_error()
    def tab_setting_changed(self, sender, args):
        for tab in ribbon.get_current_ui():

            if tab.name == "Ennead Tailor":
                # not new state since the visible value is reverse
                tab.visible = self.checkbox_tab_tailor.IsChecked
            if tab.name == "Ennead Library":
                # not new state since the visible value is reverse
                tab.visible = self.checkbox_tab_library.IsChecked


    @ERROR_HANDLE.try_catch_error()
    def apply_setting_click(self, sender, args):
        self.save_setting()
        is_tester = self.toggle_bt_is_beta_tester.IsChecked
        is_game_included = self.checkbox_game.IsChecked
        
        self.event_runner.run("change_extension_folder", is_tester, is_game_included)
        # from EnneadTab.REVIT import REVIT_APPLICATION
        # from EnneadTab import DATA_FILE, USER, NOTIFICATION, ENVIRONMENT, SPEAK, ERROR_HANDLE, FOLDER
        # self.change_extension_event_handler.kwargs = is_tester, is_game_included
        # self.ext_event.Raise()
        # res = self.change_extension_event_handler.OUT
        # self.Close()



    @ERROR_HANDLE.try_catch_error()
    def toggle_tab_color_click(self, sender, args):
        
        TABS.toggle_doc_colorizer()

        # below line is intentional comment out so it does not self trigger
        # self.toggle_bt_is_tab_color.IsChecked = not(self.toggle_bt_is_tab_color.IsChecked)


    @ERROR_HANDLE.try_catch_error()
    def radio_bt_sync_monitor_click(self, sender, args):
        self.update_UI()

    @ERROR_HANDLE.try_catch_error()
    def update_UI(self):
        if  self.radio_bt_sync_monitor_is_checking.IsChecked:
            self.textbox_sync_monitor_interval.IsEnabled = True
            self.textbox_sync_monitor_interval.Background = System.Windows.Media.Brushes.White
        else:
            self.textbox_sync_monitor_interval.IsEnabled = False
            self.textbox_sync_monitor_interval.Background = System.Windows.Media.Brushes.Gray


    def save_setting_click(self, sender, args):
        self.save_setting()





@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    MainSetting(title = __title__, 
                summary = __doc__, 
                xaml_file_name = 'EnneadTab_Setting_UI.xaml', 
                external_funcs = [change_extension_folder])


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
    
