#!/usr/bin/python
# -*- coding: utf-8 -*-

__title__ = "Startup"
__doc__ = "The magical kickstarter for EnneadTab! This script initializes all the wonderful EnneadTab tools and features when Revit launches. It handles essential setup tasks like path registration, version checking, context menu creation, and graphic server registration - quietly working behind the scenes so all your favorite tools are ready to use."

import os
import sys
import threading
import uuid  # added for potential future use
JOB_ID = os.environ.get("ACC_JOB_ID")
import traceback

# Helper for ACC automation
# ------------------------------------------------------

def _finish_job_with_state(job_record, job_file, state_value, run_log = ""):
    """Set job state, save file, and close Revit"""
    try:
        if job_record is not None:
            job_record["state"] = state_value
            if run_log:
                job_record["run_log"] = run_log
            DATA_FILE.set_data(job_record, job_file)
    except Exception as _e:
        print("Error saving job state: {}".format(_e))
    try:
        REVIT_APPLICATION.close_revit_app()
    except Exception as _e:
        print("Error closing Revit: {}".format(_e))


"""need to navigate to duckking lib first before it can auto detect further. 
This is special treatment for te startup script only"""
# Define the relative path to the "lib" directory (2 levels up, then into "lib")
relative_lib_path = os.path.join('..',  'KingDuck.lib')

# Convert the relative path to an absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.abspath(os.path.join(current_dir, relative_lib_path))

# Add the "lib" directory to sys.path
if lib_dir not in sys.path:
    sys.path.append(lib_dir)



try:

    import proDUCKtion # pyright: ignore 
    proDUCKtion.validify()



    import os
    import random
    import time

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    from pyrevit import versionmgr

    import System # pyright: ignore
    from EnneadTab import NOTIFICATION, DATA_FILE, FOLDER, OUTPUT, TIME, VERSION_CONTROL
    from EnneadTab import MODULE_HELPER, ERROR_HANDLE, USER, KEYBOARD, ENVIRONMENT, SOUND, DOCUMENTATION, LOG, IMAGE
    from EnneadTab import JOKE, EMOJI, ENCOURAGING, HOLIDAY, EXE
    from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION, REVIT_EVENT, REVIT_SELECTION


    # need below for the C drive space check
    import clr # pyright: ignore
    clr.AddReference('System.IO')
    from System.IO import DriveInfo # pyright: ignore

except:
    print (ERROR_HANDLE.get_alternative_traceback())

    
def check_minimal_version_for_enneadtab():
    v = versionmgr.get_pyrevit_version()

    desired_major = 4
    desired_minor = 8
    major, minor, patch = v.as_int_tuple()
    if major > desired_major:
        return
    if minor < desired_minor:
        NOTIFICATION.messenger("Please update pyrevit from self service port\n{}.{} ---> {}.{}".format(major, minor, desired_major, desired_minor))
        output = OUTPUT.get_output()

        output.write("Please update pyrevit from self service port!!!",OUTPUT.Style.Title)
        output.write("Your version: {}.{} ---> Suggested version: {}.{}".format(major, minor, desired_major, desired_minor),OUTPUT.Style.Subtitle)
        output.insert_divider()
        output.write ("Did you know pyrevit 4.7 was released at end of 2019? That was so long ago Covid was not even a thing yet.")

        # covid_img = IMAGE.get_one_image_path_by_prefix("covid_joke")
        # output.write(covid_img)

        output.plot()


def annouce_hibration_mode():
    if random.random() > 0.000000001:
        return
    output = OUTPUT.get_output()
    if random.random() > 0.7:
        output.write("EnneadTab in hibernation mode.", OUTPUT.Style.Title) 
        output.write("Due to staffing plan change, Sen Zhang is no longer maintaining ")
        output.write("Bug-fix and feature-build are suspended.")
        output.write("{}\\hibernation_large.png".format(ENVIRONMENT.IMAGE_FOLDER))
        """https://www.fontspace.com/cobemat-cartoon-font-f104361
        this is the font webpage"""
    else:
        output.write("EnneaDuck is on vacation to get a tan.", OUTPUT.Style.Title) 
        output.write("He is not available at the moment, check back later.")
        output.write("{}\\beijing duck.jpg".format(ENVIRONMENT.IMAGE_FOLDER))
    output.plot()








def open_scheduled_docs():
    """this will also require the exe to run a schedule to active the revit, with version required.
    """

    data_file = "action_schedule_opener_data"
    data = DATA_FILE.get_data(data_file)
    if not data:
        return
    
    begin_time = time.time()
    
    folder = "EnneadTab.tab\\Tools.panel"
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
    
    os.remove(FOLDER.get_local_dump_folder_file(data_file))
    used_time = time.time() - begin_time
    REVIT_FORMS.notification(main_text = "{} have been preloaded to this revit session.\nIt took {}.".format(success_docs_note, TIME.get_readable_time(used_time)),
                                             sub_text = "Even you are not seeing them right now, they hare been openned in the background.\nTo show them, open those files as normal(click from 'recently open list') to see them instantly open.")

    try:
        KEYBOARD.send_control_D()
    except:
        pass




def check_C_drive_space():
    drive = DriveInfo("C")
    percent_used = int(float(drive.TotalSize - drive.AvailableFreeSpace) / drive.TotalSize * 100)
    
    if percent_used > 85:
        NOTIFICATION.messenger(main_text = "Your C drive is almost full, {}% used.\nSome revit file might fail to open. Please clean cache with ".format(percent_used))



def register_auto_update():
    return
    
    try:# need pyrevit 5 or higher to work in revit 2025
        from pyrevit.userconfig import user_config
        user_config.check_updates = True
        user_config.save_changes()
    except:
        
        pass







class TempGraphicServer(UI.ITemporaryGraphicsHandler):

    @ERROR_HANDLE.try_catch_error(is_silent=True)
    def OnClick(self, data):
        """this data is TemporaryGraphicsCommandData class that return during click,
        not InCanvasControlData class used to add control"""

        manager = DB.TemporaryGraphicsManager.GetTemporaryGraphicsManager(data.Document)
        manager.RemoveControl(data.Index)
        SOUND.play_sound("sound_effect_duck.wav")




        temp_graphic_data = DATA_FILE.get_data("CANVAS_TEMP_GRAPHIC_DATA_{}".format(data.Document.Title))
        record = temp_graphic_data.get(str(data.Index))
        if record and record.get("additional_info").get("description"):
            NOTIFICATION.messenger(record["additional_info"]["description"])
        
    def GetName(self):
        return "My Graphics Service"
        
    def GetDescription(self):
        return "This is a graphics service"
        
    def GetVendorId(self):
        return ENVIRONMENT.PLUGIN_NAME
        
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
        # NOTIFICATION.messenger("Remove old graphical server...")
    external_service.AddServer(my_graphics_service)
    external_service.SetActiveServers(System.Collections.Generic.List[System.Guid]([my_graphics_service.GetServerId()]))


def register_xaml_path():
    """Register XAML file paths in a persistent background thread.
    This function scans all extensions to locate XAML files for quick lookup later.
    The thread will continue running even after main program exit.
    """
    def _register_xaml_path_worker():
        try:
            data = {}
            for root, dirs, files in os.walk(ENVIRONMENT.REVIT_FOLDER):
                for file in files:
                    if file.endswith(".xaml"):
                        data[file] = os.path.join(root, file)
            DATA_FILE.set_data(data, "xaml_path")
        except Exception as e:
            print("Error in XAML path registration thread: {}".format(str(e)))

    thread = threading.Thread(target=_register_xaml_path_worker)
    thread.daemon = False  # Thread will continue running after main program exits
    thread.start()

def set_RIR_clicker():
    
    if not USER.IS_DEVELOPER:
        return
    with DATA_FILE.update_data("auto_click_data") as data:
        if "ref_images" not in data or data["ref_images"] is None:
            data["ref_images"] = []
            
        data["ref_images"].append(IMAGE.get_image_path_by_name("search_RIR_7.png"))
    EXE.try_open_app("AutoClicker.exe")

def register_selection_owner_checker():
    # to-do: this is too slow, i am goint to disable it untile better solution found.
    if not USER.IS_DEVELOPER:
        return
    from pyrevit import HOST_APP
    if not HOST_APP.is_newer_than(version = 2023, or_equal = True):
        return

    from System import EventHandler
    from Autodesk.Revit.UI.Events import SelectionChangedEventArgs
    __revit__.SelectionChanged += EventHandler[SelectionChangedEventArgs](selection_owner_checker)


def selection_owner_checker(sender, args):
    selection_ids = list(args.GetSelectedElements ())
    
    if len(selection_ids) == 0:
        return

    doc = args.GetDocument ()
    for x in selection_ids:
        try:
            element = doc.GetElement(DB.ElementId(x.Value))
        except:
            element = doc.GetElement(DB.ElementId(x.IntegerValue)) # this is kept for backward compability

        if element.Category and element.Category.Name == "Views":
            continue
        if not REVIT_SELECTION.is_changable(element):
            NOTIFICATION.messenger("Note that your selection contains element owned by [{}]".format(REVIT_SELECTION.get_owner(element)))
            SOUND.play_error_sound()
            return

def purge_dump_folder_families():
    FOLDER.cleanup_folder_by_extension(FOLDER.DUMP_FOLDER, ".rfa", old_file_only=True)
    FOLDER.cleanup_folder_by_extension(FOLDER.DUMP_FOLDER, ".3dm", old_file_only=True)
    FOLDER.cleanup_folder_by_extension(FOLDER.DUMP_FOLDER, ".dwg", old_file_only=True)



if REVIT_APPLICATION.is_version_at_least(2025):
    class EnneadTabContextMenuMaker(UI.IContextMenuCreator):
        def BuildContextMenu(self, context_menu):
            def is_enneadtab_command(command):
                if command.name and command.extension == ENVIRONMENT.PRIMARY_EXTENSION_NAME:
                    if command.tooltip:
                        tooltips = command.tooltip.lower()
                        if "legacy" in tooltips or "not in use" in tooltips:
                            return False
                    if command.script:
                        script_path = command.script.lower()
                        if "tailor" in script_path or "library" in script_path:
                            return False
                    return True
                return False

            
            try:
                from pyrevit.loader import sessionmgr
                for i, command in enumerate(filter(is_enneadtab_command, sessionmgr.find_all_available_commands())):
                    print (command.name, command.tooltip, command.script)
                    item = UI.CommandMenuItem("some menu button name TBD", "LocalCommand", command.script)
                    item.SetAvailabilityClassName("Autodesk.Revit.DB.View") # this is important to call pyrevit
                    context_menu.AddItem(item)

                    return

            except Exception as e:
                import traceback
                ERROR_HANDLE.print_note(traceback.format_exc())

    class LocalCommand(UI.IExternalCommand):
        def Execute(self, command_data, message, elements):
            print("Custom context menu action executed!")
            return DB.Result.Succeeded
        
def register_context_menu():
    return

    import traceback
    try:
        uiapp = REVIT_APPLICATION.get_uiapp()
        if not hasattr(uiapp, "RegisterContextMenu"):
            return
        
        context_menu_maker = EnneadTabContextMenuMaker()
        uiapp.RegisterContextMenu("EnneaDuck", context_menu_maker)

        print ("context menu registered")


        

    except:
        print (traceback.format_exc())



def handle_acc_slave_job():
    """Handle ACC job based on job_id passed from external orchestrator.

    Reads job record, attempts to open the cloud model, and updates state.
    No f-strings are used to keep compatibility with older Python versions.
    """
    run_log = ""
    if not JOB_ID:
        # Interactive Revit session; nothing to do.
        return

    job_file = "ACC_JOB_{}".format(JOB_ID)
    job_record = DATA_FILE.get_data(job_file)
    if not job_record:
        run_log += "Job record not found: {}".format(job_file)
        dummy = {"state": "FAILED_JOB_RECORD"}
        DATA_FILE.set_data(dummy, job_file)
        try:
            REVIT_APPLICATION.close_revit_app()
        except:
            pass
        return

    # Only continue if orchestrator placed us in REVIT_STARTING state
    if job_record.get("state") != "REVIT_STARTING":
        run_log += "Job {} in unexpected state: {}".format(JOB_ID, job_record.get("state"))
        _finish_job_with_state(job_record, job_file, "FAILED_STATE_MISMATCH", run_log)
        return

    task = job_record.get("task", {})
    model_guid = task.get("model_guid")
    project_guid = task.get("project_guid")
    # Build candidate regions list using helper for maximum compatibility
    candidate_regions = REVIT_APPLICATION.get_known_regions()

    if not model_guid or not project_guid:
        run_log += "Missing model_guid or project_guid in task data"
        _finish_job_with_state(job_record, job_file, "FAILED_TASK_DATA", run_log)
        return

    # Update state to OPENING_DOC so outer process knows progress
    job_record["state"] = "OPENING_DOC"
    DATA_FILE.set_data(job_record, job_file)

    open_success = False
    for region in candidate_regions:
        try:
            run_log += "Attempting to open cloud model in region '{}'\n".format(region)
            cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(region,
                                                                        System.Guid(project_guid),
                                                                        System.Guid(model_guid))
            open_opts = DB.OpenOptions()
            open_opts.SetOpenWorksetsConfiguration(DB.WorksetConfiguration(DB.WorksetConfigurationOption.CloseAllWorksets))
            open_opts.Audit = True
            try:
                # Use Application API first (faster, headless)
                REVIT_APPLICATION.get_app().OpenDocumentFile(cloud_path, open_opts)
            except Exception as e:
                run_log += "Primary open failed for region '{}': {}\n".format(region, e)
                # Try UI API as fallback
                REVIT_APPLICATION.get_uiapp().OpenAndActivateDocument(cloud_path, open_opts, False)

            # If we reach here, open succeeded
            open_success = True
            job_record["region_used"] = region
            break
        except Exception as e:
            run_log += "Region '{}' failed: {}\n".format(region, e)

    if not open_success:
        run_log += "Error creating cloud path or opening document: traceback below\n{}".format(traceback.format_exc())
        _finish_job_with_state(job_record, job_file, "FAILED_OPEN_DOC", run_log)
        return

    # Document opened successfully. Doc-opened hook will continue the flow.
    job_record["state"] = "PROCESSING"
    DATA_FILE.set_data(job_record, job_file)



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error(is_silent=True)
def EnneadTab_startup():
    # Run ACC automation only in developer sessions for now
    if USER.IS_DEVELOPER:
        handle_acc_slave_job()

    # Additional developer-specific behaviour can go here

    if ENVIRONMENT.IS_AVD:
        set_RIR_clicker()

        
    register_context_menu()

    
    VERSION_CONTROL.update_dist_repo()
    register_xaml_path()
    check_minimal_version_for_enneadtab()


    if  USER.IS_DEVELOPER:
        if random.random() < 0.5:
            ENCOURAGING.warming_quote()
        elif random.random() < 0.9:
            JOKE.joke_quote()
        else:
            NOTIFICATION.duck_pop(main_text = "Hello {}!\nEnneaDuck welcome you back!".format(USER.USER_NAME))
        

        HOLIDAY.festival_greeting()
    
    check_C_drive_space()


    DOCUMENTATION.tip_of_day()

  
        
    
    
    
    # use this part to force clear a user from database, in case the file is corrupted
    # LEGACY_LOG.force_clear_user(target_user_names = ["fliu"])
    
    # LEGACY_LOG.open_revit_successful()
    
    # if LEGACY_LOG.is_money_negative():
    #     print ("Your Current balance is {}".format(LEGACY_LOG.get_current_money()))
    


    
    open_scheduled_docs()
    
    REVIT_EVENT.set_doc_change_hook_depressed(stage = False)
    REVIT_EVENT.set_sync_queue_enable_stage(stage = True)
    REVIT_EVENT.set_family_load_hook_stage(stage = True)
    REVIT_EVENT.set_L_drive_alert_hook_depressed(stage = False)

    TIME.update_revit_uptime()


    

    register_auto_update()

    register_temp_graphic_server()
    register_selection_owner_checker()
    purge_dump_folder_families()

    if USER.IS_DEVELOPER:
        NOTIFICATION.messenger(main_text = "[Developer Only] startup run ok.")





if __name__ == "__main__":
    EnneadTab_startup()

