
"""consider getting doc changed hook in here to subscribe so it does not start new window...

but still not a good idea to doc change hook. performance issue 
"""

import imp
import os
import random
import time

from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
from pyrevit import forms, script
from pyrevit.coreutils import envvars
from pyrevit import versionmgr

import EA_UTILITY
import System # pyright: ignore
from EnneadTab import NOTIFICATION, DATA_FILE, FOLDER, ENVIRONMENT_CONSTANTS, OUTPUT, TIME, VERSION_CONTROL
from EnneadTab import MODULE_HELPER, ERROR_HANDLE, USER, KEYBOARD, ENVIRONMENT, SOUNDS, DOCUMENTATION
from EnneadTab.FUN import JOKES, EMOJI, ENCOURAGING, HOLIDAY
from EnneadTab.REVIT import REVIT_REPO, REVIT_FORMS
import ENNEAD_LOG


# need below for the C drive space check
import clr # pyright: ignore
clr.AddReference('System.IO')
from System.IO import DriveInfo # pyright: ignore


def check_minimal_version_for_enneadtab():
    v = versionmgr.get_pyrevit_version()

    desired_major = 4
    desired_minor = 8
    major, minor, patch = v.as_int_tuple()
    if major < desired_major or minor < desired_minor:
        NOTIFICATION.messenger("Please update pyrevit from self service port\n{}.{} ---> {}.{}".format(major, minor, desired_major, desired_minor))
        output = OUTPUT.get_output()

        output.write("Please update pyrevit from self service port!!!",OUTPUT.Style.Title)
        output.write("Your version: {}.{} ---> Suggested version: {}.{}".format(major, minor, desired_major, desired_minor),OUTPUT.Style.SubTitle)
        output.insert_division()
        output.write ("Did you know pyrevit 4.7 was released at end of 2019? That was so long ago Covid was not even a thing yet.")

        covid_imgs = [f for f in os.listdir(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT) if "covid_joke" in f]
        covid_img = random.choice(covid_imgs)
        output.write("{}\\{}".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT,
                                                     covid_img))

        output.plot()

# alwasy register dimension assist, but dont open it until button clicked

class DimNoteDockable(forms.WPFPanel):
    panel_title = "@@EnneadTab Dimension Text Assist"
    panel_id = "3110e336-f81c-4927-87da-4e0d30d4d64a"
    panel_source = os.path.join(os.path.dirname(__file__), "DimNoteDockable.xaml")




    def dim_text(self, target_text):

        docs = __revit__.Documents # pyright: ignore
        for doc in docs:
            print (doc.Title)

        print ("----")
        uidoc = UI.UIApplication.ActiveUIDocument
        print (uidoc)
        try:
            print( uidoc.ActiveView.Name)
        except Exception as e:
            print( e)
        doc = uidoc.Document
        print (doc.Title)
        print( "/////")

        selection_ids = uidoc.Selection.GetElementIds ()
        selection = [doc.GetElement(x) for x in selection_ids]
        # test to use UI.Selection.GetElemendIds, avoid using pyrevit's revit function

        print (selection)
        for el in selection:
            print (el)
        print( "*****")


        selection = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(DB.Dimension).WhereElementIsNotElementType().ToElements()
        print (selection)
        t = DB.Transaction(doc, "dim segement")
        t.Start()
        for dim in selection:
            print (dim)
            # try:
            #     dim.NumberOfSegments
            # except:
            #     continue
            if dim.NumberOfSegments == 0:
                print( "ok, 0 segement")
                dim.Below  = target_text
                continue

            print ("ah, dim with many segements")
            for dim_seg in dim.Segments:
                dim_seg.Below  = target_text
        t.Commit()


    def mark_FOG(self, sender, args):
        
        forms.alert("mark FOG")
        self.debug_textbox.Text = "mark FOG"

        try:
            self.dim_text("FOG")
        except Exception as e:
            print (e)



    def mark_EOS(self, sender, args):
        forms.alert("mark EOS")
        self.debug_textbox.Text = "mark EOS"



def register_sample_dockpane():
    import Sample_DockPane_Simple
    Sample_DockPane_Simple.register_sample_dockpane()

def register_rhino_dockpane():
    import imp
    #C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Rhino.panel\Rhino2Revit.pulldown\open_rhino_dockpane.pushbutton\Rhino_DockPane.py
    full_file_path = script.get_bundle_file("Ennead.tab\Rhino.panel\Rhino2Revit.pulldown\open_rhino_dockpane.pushbutton\Rhino_DockPane.py")
    full_file_path = FOLDER.remap_filepath_to_folder(full_file_path)
    #print full_file_path
    ref_module = imp.load_source("Rhino_DockPane", full_file_path)

    ref_module.register_rhino_dockpane()


def register_dimension_note_dockpane():
    if not forms.is_registered_dockable_panel(DimNoteDockable):
        forms.register_dockable_panel(DimNoteDockable, default_visible = EA_UTILITY.is_SZ())
        EA_UTILITY.show_toast(message = "Go to [DIM TEXT] panel for opener",title = "Dim Assist Panel ready", app_name = "EnneadTab")
    else:
        EA_UTILITY.print_note( "Skipped registering dockable pane. Already exists.")


def annouce_hibration_mode():
    if random.random() > 0.01:
        return
    output = OUTPUT.get_output()
    if random.random() > 0.7:
        output.write("EnneadTab in hibernation mode.", OUTPUT.Style.Title) 
        output.write("Due to staffing plan change, Sen Zhang is no longer maintaining ")
        output.write("Bug-fix and feature-build are suspended.")
        output.write("{}\\hibernation_large.png".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        """https://www.fontspace.com/cobemat-cartoon-font-f104361
        this is the font webpage"""
    else:
        output.write("EnneaDuck is on vacation to get a tan.", OUTPUT.Style.Title) 
        output.write("He is not available at the moment, check back later.")
        output.write("{}\\beijing duck.jpg".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
    output.plot()

def general_annoucement():
    annouce_hibration_mode()

    from datetime import date
    today = date.today().strftime("%m/%d/%y")
    #09/16/19

    if today not in ["06/27/22",
                    "06/24/22",
                    "07/04/22",
                    "07/08/22"]:
        return


    output = script.get_output()
    output.print_md("**SH team please note that Autodesk will maintain cloud server on July 10, this might overlap with your working hour on Monday.**")
    output.print_image(r'file:\\L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\lib\annoucement\revit maintain.png')
    EA_UTILITY.show_toast(message = "Please check with your team ACE to plan ahead.",title = "Autodesk Scheduled maintenance on July 10, 1~6pm ET.", app_name = "EnneadTab")
    # EA_UTILITY.dialogue(main_text = "SH team please note that Autodesk will maintain cloud server on July 10, 1-6pm EST.", sub_text = "This might partially overlap with your working hour on Monday depending on your work plan. Please check with your team ACE to plan ahead.", footer_link = "https://health.autodesk.com/incidents/9m442dbcmt72", footer_text = "Autodesk Health")
    #"http://www.ennead.com"
    #http://usa.autodesk.com/adsk/servlet/index?siteID=123112&id=2484975
    pass




def start_monitor_edit_request():



    if not EA_UTILITY.is_SZ(additional_tester_ID = ["scott.mackenzieG4RJ9"]):
        return



    import imp
    full_file_path = r'C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Utility.panel\exe_1.stack\urge_request.pushbutton\urge_request_script.py'
    if not USER.is_SZ():
        full_file_path = FOLDER.remap_filepath_to_folder(full_file_path)
    ref_module = imp.load_source("urge_request_script", full_file_path)

    ref_module.run_exe()
    




@ERROR_HANDLE.try_catch_error
def read_beta_annoucment():
    if not USER.is_revit_beta_tester(include_SZ = True):
        # print( "Not a beta tester")
        return

    """
    topic = "2023-06-01: Update Setting"
    main_text = "Dear Beta Testers, please go to your EnneadTab setting to update.\n\nSee output image for reference."
    sub_text = "You can change popup reminder level, talkie, sync gap and email frequency level."
    images = [r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc\annoucement imgs\go to setting.png"]
    
    NOTIFICATION.let_read_annoucement(topic, main_text, sub_text, images)
    """


    topic = "2023-06-20: Update UI"
    main_text = "Dear Beta Testers, in order to make tab name shorter and unify some spelling, the EnneadTab UI is updated. You do NOT need to take any action. So far no dependency issues are found, but if you do find, please let me know."
    sub_text = "EnneadTab_Basic-->Ennead\nEnneadTab_Advanced-->Ennead+\nEnneadTab_Tailor-->Ennead Tailor\nEnneadTab_Library-->Ennead Library"
    images = None
    
    NOTIFICATION.let_read_annoucement(topic, main_text, sub_text, images)


def open_scheduled_docs():
    """this will also require the exe to run a schedule to active the revit, with version required.
    """
    # if not EA_UTILITY.is_SZ(additional_tester_ID = ["scott.mackenzieG4RJ9"]):
    #     return
    # check dump folder if there are queued jobs
    data_file = "action_" + "EA_SCHEDULE_OPENER.json"
    if not FOLDER.is_file_exist_in_dump_folder(data_file):
        return
    data = DATA_FILE.read_json_as_dict_in_dump_folder(data_file)
    if not data:
        return
    
    begin_time = time.time()
    
    folder = "Ennead.tab\\Tools.panel"
    func_name = "open_doc_silently"
    

    success_docs_note = ""
    failed_docs_note = ""
    for doc in data["docs"]:
        try:
            MODULE_HELPER.run_revit_script(folder, func_name, [doc])
            # ref_module.Solution().main([doc])
            success_docs_note += "[{}]\n".format(doc)
        except:
            print ("Cannot open <{}>".format(doc))
            failed_docs_note += "[{}]\n".format(doc)
    

    
    # if so, check the GUID and open each one, use silent openner.
    
    FOLDER.remove_file_from_dump_folder(data_file)
    used_time = time.time() - begin_time
    REVIT_FORMS.notification(main_text = "{} have been preloaded to this revit session.\nIt took {}.".format(success_docs_note, TIME.get_readable_time(used_time)),
                                             sub_text = "Even you are not seeing them right now, they hare been openned in the background.\nTo show them, open those files as normal(click from 'recently open list') to see them instantly open.")

    try:
        KEYBOARD.send_control_D()
    except:
        pass


def starter_quote():
    if NOTIFICATION.get_toaster_level_setting() != 0:
        return
    
    
    if random.random() < 0.5:
        warming_quote()
    else:
        joke_quote()


def joke_quote():
    emoji = EMOJI.random_emoji()
    quote = JOKES.random_loading_message()
    

    import textwrap
    # Wrap this text.
    wrapper = textwrap.TextWrapper(width = 100)
    quote = wrapper.fill(text = quote)


    NOTIFICATION.messenger(main_text = "{}\n{}".format(quote, emoji), animation_stay_duration = 10)


def warming_quote():
    quote = ENCOURAGING.random_warming_quote()
    

    import textwrap
    # Wrap this text.
    wrapper = textwrap.TextWrapper(width = 100)
    quote = wrapper.fill(text = quote)


    NOTIFICATION.messenger(main_text = quote, animation_stay_duration = 10)



    if not DATA_FILE.get_revit_ui_setting_data(key_defaule_value = ("toggle_bt_is_duck_allowed", True)):
        return


    NOTIFICATION.duck_pop(main_text = "Hello {}!\nEnneaDuck welcome you back!".format(USER.get_user_name() ))
    
    
    
    audio_folder = "{}\\ENNEAD.extension\\Ennead.tab\\Utility.panel\\exe_2.stack\\duck_pop\\audio".format(ENVIRONMENT_CONSTANTS.PUBLISH_FOLDER_FOR_REVIT)
    # pick a random duck sound from the folder
    duck_sound_list = [x for x in os.listdir(audio_folder) if x.endswith(".wav")]
    audio = os.path.join(audio_folder,random.choice(duck_sound_list))

    SOUNDS.play_sound(audio)




def check_C_drive_space():
    drive = DriveInfo("C")
    percent_used = int(float(drive.TotalSize - drive.AvailableFreeSpace) / drive.TotalSize * 100)
    
    if percent_used > 85:
        NOTIFICATION.duck_pop(main_text = "Your C drive is almost full, {}% used.\nSome revit file might fail to open. Please clean cache with ".format(percent_used))
    else:
        NOTIFICATION.messenger(main_text = "Your C drive is {}% used.".format(percent_used))
            



def register_auto_update():
    from pyrevit.userconfig import user_config
    user_config.check_updates = True
    user_config.save_changes()


    return # disable autoupdater for now for better performace.--> do this after doc closing is better
    
    from pyrevit.versionmgr import updater
    if updater.check_for_updates():
        updater.update_pyrevit()




class TempGraphicServer(UI.ITemporaryGraphicsHandler):

    @ERROR_HANDLE.try_catch_error_silently
    def OnClick(self, data):
        """this data is TemporaryGraphicsCommandData class that return during click,
        not InCanvasControlData class used to add control"""

        manager = DB.TemporaryGraphicsManager.GetTemporaryGraphicsManager(data.Document)
        manager.RemoveControl(data.Index)
        SOUNDS.play_sound("sound effect_duck.wav")




        temp_graphic_data = DATA_FILE.read_json_as_dict_in_dump_folder("CANVAS_TEMP_GRAPHIC_DATA_{}.json".format(data.Document.Title),
                                                                                 create_if_not_exist=True)
        record = temp_graphic_data.get(str(data.Index))
        if record and record.get("additional_info").get("description"):
            NOTIFICATION.messenger(record["additional_info"]["description"])
        
    def GetName(self):
        return "My Graphics Service"
        
    def GetDescription(self):
        return "This is a graphics service"
        
    def GetVendorId(self):
        return "EnneadTab"
        
    def GetServiceId(self):
        return DB.ExternalService.ExternalServices.BuiltInExternalServices.TemporaryGraphicsHandlerService
        
    def GetServerId(self):
        return System.Guid("a8debc37-19fe-4198-1198-01a891ff1a7f")

    
def register_temp_graphic_server():
    external_service = DB.ExternalService.ExternalServiceRegistry.GetService(
        DB.ExternalService.ExternalServices.BuiltInExternalServices.TemporaryGraphicsHandlerService
    )
    my_graphics_service = TempGraphicServer()
    if external_service.IsRegisteredServerId (my_graphics_service.GetServerId()):
        external_service.RemoveServer(my_graphics_service.GetServerId())
        NOTIFICATION.messenger("Remove old graphical server...")
    external_service.AddServer(my_graphics_service)
    external_service.SetActiveServers(System.Collections.Generic.List[System.Guid]([my_graphics_service.GetServerId()]))



@ERROR_HANDLE.try_catch_error_silently
def main():
    if ENVIRONMENT_CONSTANTS.is_Revit_limited():
        return
    
    if not ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return

    check_minimal_version_for_enneadtab()

    HOLIDAY.festival_greeting()
    
    # this need to be up front becasue some of the file during 
    # import module will clear out all the output window.
    # for developer, it will also kill the loadding status window so if 
    # developer, do not show this tips very often
    chance = 1
    if USER.is_SZ():
        chance = random.random()
        chance = 1 # when testing tip of day
 
    if chance > 0.8:
        DOCUMENTATION.tip_of_day()
    else:
        pass
  
        
    
    
    check_C_drive_space()
    
    # use this part to force clear a user from database, in case the file is corrupted
    # ENNEAD_LOG.force_clear_user(target_user_names = ["fliu"])
    
    ENNEAD_LOG.open_revit_successful()
    
    if ENNEAD_LOG.is_money_negative():
        print ("Your Current balance is {}".format(ENNEAD_LOG.get_current_money()))
    
    # all kinds of anouncers..........
    starter_quote()
    general_annoucement()



    read_beta_annoucment()
    
    
    EA_UTILITY.set_doc_change_hook_depressed(is_depressed = False)
    envvars.set_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED", False)

    try:
        TIME.set_revit_uptime()
    except:
        envvars.set_pyrevit_env_var("APP_UPTIME", time.time())




    start_monitor_edit_request()
    
    open_scheduled_docs()


    REVIT_REPO.update_pyrevit_extension_json()
    register_auto_update()

    register_temp_graphic_server()

    VERSION_CONTROL.install_EA_dist()

    if not USER.is_SZ(pop_toast = True):
        return
    
    
################### main code below ###############

#print "app init.py"

if __name__ == "__main__":

    main()
    

"""
# dockpane can only be registered when zero doc context!!!!

try:
    register_dimension_note_dockpane()
except Exception as e:
    EA_UTILITY.print_note(e)


try:
    register_sample_dockpane()
except Exception as e:
    EA_UTILITY.print_note(e)
    error = traceback.format_exc()
    error_file = "{}\error_log.txt".format(EA_UTILITY.get_user_folder())
    with open(error_file, "w") as f:
        f.write(error)
    EA_UTILITY.open_file_in_default_application(error_file)

register_rhino_dockpane()
"""






"""
import DockPane_DimTextHelper
try:
    DockPane_DimTextHelper.register_dimension_note_dockpane()

    panel_uuid = "a35a21da2b4e86ab0502ef58bad11be1"
    forms.open_dockable_panel(panel_uuid)

except Exception as e:
    EA_UTILITY.print_note(e)

"""
