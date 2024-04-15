from pyrevit import EXEC_PARAMS, script
from Autodesk.Revit import DB
import EA_UTILITY
import EnneadTab
import ENNEAD_LOG
import traceback
from pyrevit.coreutils import envvars
doc = EXEC_PARAMS.event_args.Document
import random

REGISTERED_AUTO_PROJS = ["1643_lhh bod-a_new",
                        "2151_a-nyuli_hospital",
                        "Facade System"]

REGISTERED_AUTO_PROJS = [x.lower() for x in REGISTERED_AUTO_PROJS]

def warn_non_enclosed_area():
    areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
    bad_areas = filter(lambda x: x.Area == 0, areas)
    if len(bad_areas) > 0:

        EnneadTab.NOTIFICATION.toast(sub_text = "They might have impact on the accuracy of your Area Schedule.", main_text = "There are {} non-placed/redundant/non-enclosed areas in the file.".format(len(bad_areas)))


def warn_non_enclosed_room():
    rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
    bad_rooms = filter(lambda x: x.Area == 0, rooms)
    if len(bad_rooms) > 0:

        EnneadTab.NOTIFICATION.toast(sub_text = "A bad room might be either non-placed/redudent/non-enclosed.", main_text = "There are {} bad rooms in need of attention.".format(len(bad_rooms)))




@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def update_project_2151():
    # "ea_healthcare_r22 wip"
    if doc.Title.lower() not in ["2151_a-nyuli_hospital"]  :
        return
    
    folder = "Ennead Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "color_pills"
    EnneadTab.MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    
    
    
    folder = "Ennead Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "all_in_one_checker"
    EnneadTab.MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)



    if EnneadTab.USER_CONSTANTS.USER_NAME != "sha.li":
        return
    if random.random() > 0.1:
        return
    folder = "Ennead Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "confirm_RGB"
    EnneadTab.MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)



@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def update_project_2314():

    if "2314_a-455 1st ave" not in doc.Title.lower():
        return
    
    folder = "Ennead Tailor.tab\\Proj. 2314.panel\\First Ave.pulldown"
    func_name = "all_in_one_checker"
    

    
    EnneadTab.MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    
    return

@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def update_project_1643():

    if "1634_lhh boa-a_new" not in doc.Title.lower():
        return

    folder = "Ennead Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_delta_area_graphic"
    

    
    EnneadTab.MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    
    return

    
def update_with_generic_healthcare_tool():
    if not EnneadTab.USER.is_SZ():
        return
    health_care_projects = ["2151_a-nyuli_hospital"]
    
    if doc.Title.lower() not in health_care_projects:
        return
    
    folder = "Ennead.tab\\Tools.panel"
    func_name = "generic_healthcare_tool"
    EnneadTab.MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    return

def update_sheet_name():


    
    if doc.Title.lower() not in REGISTERED_AUTO_PROJS:
        return
    
    script = "Ennead.tab\\Tools.panel\\general_renamer.pushbutton\\general_renamer_script.py"
    func_name = "rename_views"
    sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
    is_default_format = True
    show_log = False
    EnneadTab.MODULE_HELPER.run_revit_script(script, func_name, doc, sheets, is_default_format, show_log)

    
def update_working_view_name():



    
    if doc.Title.lower() not in REGISTERED_AUTO_PROJS:
        return
    
    script = "Ennead.tab\\Manage.panel\\working_view_cleanup.pushbutton\\manage_working_view_script.py"
    func_name = "modify_creator_in_view_name"

    fullpath = "{}\\ENNEAD.extension\\{}".format(EnneadTab.ENVIRONMENT.PUBLISH_FOLDER_FOR_REVIT, script)
    import imp
    ref_module = imp.load_source("manage_working_view_script", fullpath)



    
    views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    no_sheet_views = filter(ref_module.is_no_sheet, views)
    is_adding_creator = True
    EnneadTab.MODULE_HELPER.run_revit_script(script, func_name, no_sheet_views, is_adding_creator)
    
@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def update_project_2306():
    if "universal hydrogen" not in doc.Title.lower():
        return
    # if not EnneadTab.USER.is_SZ():
    #     return

    folder = "Ennead Tailor.tab\\Proj. 2306.panel\\Universal Hydro.pulldown"
    func_name = "factory_internal_check"
    EnneadTab.MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
 
    
    
@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def warn_bad_sized_meeting_rm():
    # only deal with N3 model

    if doc.Title != "2135_BiliBili SH HQ_N3":
        return

    if envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED"):
        # when  gloabl sync queue disabled, dont want to see dialogue
        return

    # get all rooms
    all_rms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()

    # filter room under department == visitor center
    visitor_rooms = filter(lambda x: x.LookupParameter("Department").AsString() == "VISITOR TRAINING", all_rms)

    # filter meeting rooms
    meeting_rms = filter(lambda x: "MEETING RM" in x.LookupParameter("Name").AsString(), visitor_rooms)

    # s, m ,l room group
    def is_room_area_ok(room):
        room_name = room.LookupParameter("Name").AsString()
        if "(S)" in room_name:
            low_bound, up_bound = 20, 28
        elif "(M)" in room_name:
            low_bound, up_bound = 28, 38
        elif "(L)" in room_name:
            low_bound, up_bound = 38, 9999
        else:
            low_bound, up_bound = 1, 0 # force bad display becasue up bound is smaller than low bound

        if EA_UTILITY.sqm_to_internal(low_bound) <= room.Area <= EA_UTILITY.sqm_to_internal(up_bound):
            return True
        return False

    bad_rooms = filter(lambda x: not(is_room_area_ok(x)), meeting_rms)

    if len(bad_rooms) == 0:
        return

    """
    t = DB.Transaction(doc, "mark bad room")
    t.Start()
    map()
    """
    bad_rooms.sort(key = lambda x: (x.Level.Name, x.LookupParameter("Name").AsString(), x.Area ))

    EA_UTILITY.show_toast(message = "Go to '(6_Visitor Center) Meeting Room Schedule' for details", title = "There are {} meeting rooms not meeting area requirement".format(len(bad_rooms)))

    for room in bad_rooms:
        print ("{}_{}: {} sqm --->{}".format(room.Level.Name, room.LookupParameter("Name").AsString(), EA_UTILITY.sqft_to_sqm(room.Area), script.get_output().linkify(room.Id, title = "Go To Room")))
    print ("\n\n")

    note = "N3 visitor center has {} meeting rooms not meeting desired area target for typical meeting room.\n\nYou can also go to '(6_Visitor Center) Meeting Room Schedule' for details".format(len(bad_rooms))
    print (note)

    print ("\n")
    sub_note = "Rule:\nMeeting RM(S):20~28 sqm\nMeeting RM(M):28~38 sqm\nMeeting RM(L):38+ sqm"
    print (sub_note)
    user_name = EA_UTILITY.get_application().Username
    if user_name in ["Jun.XuV6Q5Q", "xsunAFPUE", "kang.yuCYULD"] or EA_UTILITY.is_SZ():
        try:
            if envvars.get_pyrevit_env_var("IS_AFTER_SYNC_WARNING_DISABLED"):
                return
        except Exception as e:
            EA_UTILITY.print_note("error getting <IS_AFTER_SYNC_WARNING_DISABLED> varable: " + e)
        EnneadTab.REVIT.REVIT_FORMS.notification(main_text = note, sub_text = sub_note, window_width = 500, window_height = 500, self_destruct = 10)
        #EA_UTILITY.dialogue(main_text = note, sub_text = sub_note)



@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def update_sync_queue():

    # dont need to do anything if pre-sycn chech was cancelled,
    if envvars.get_pyrevit_env_var("IS_SYNC_CANCELLED"):
        return

    log_file = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Sync_Queue\Sync Queue_{}.queue". format(doc.Title)
  

    try:
        with open(log_file, "r"):
            pass
    except:
        with open(log_file, "w+"): # if not existing then create
            pass

    queue = EA_UTILITY.read_txt_as_list(log_file)

    autodesk_user_name = EA_UTILITY.get_application().Username
    user_name = EnneadTab.USER.get_user_name()
    OUT = []


    for item in queue:
        if user_name in item or autodesk_user_name in item:
            #this step remove current user name from any place in wait list, either beginging or last
            continue
        OUT.append(item)
        
        
    try:
        EA_UTILITY.save_list_to_txt(OUT, log_file)
    except:
        print ("Your account have no access to write in this address.")
        return

    if envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED"):
        # when  gloabl sync queue disabled, dont want to see dialogue, but still want to clear name from log file
        return

    if len(OUT) == 0:
        return
    try:
        next_user = OUT[0].split("]")[-1]
        # next user found!! if this step can pass
    except Exception as e:
        EA_UTILITY.print_note("cannot find next user.")
        EA_UTILITY.print_note(e)
        EA_UTILITY.print_traceback()
        return


    EnneadTab.EMAIL.email(receiver_email_list="{}@ennead.com".format(next_user),
                            subject="Your Turn To Sync!",
                            body="Hi there, it is your turn to sync <{}>!".format(doc.Title),
                            body_image_link_list=["L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published\\ENNEAD.extension\\lib\\EnneadTab\\images\\you sync first.jpg"])

    EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "[{}]\nshould sync next.".format(next_user), sub_text = "Expect slight network lag between SH/NY server to transfer waitlist file.", window_width = 500, window_height = 400, self_destruct = 15)



def play_success_sound():

    file = 'sound effect_mario join.wav'
    file = 'sound effect_mario 1up.wav'
    EnneadTab.SOUNDS.play_sound(file)
    pass


@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def play_text_to_speech_audio():

    try:
        doc.Title
    except:
        return

    EnneadTab.SPEAK.speak("Document {} has finished syncing.".format(doc.Title))


@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def update_sync_time_record():

    
    script_subfolder = "Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py"
    func_name = "update_last_sync_data_file"
    EnneadTab.MODULE_HELPER.run_revit_script(script_subfolder, func_name, doc)
    
    func_name = "run_exe"
    EnneadTab.MODULE_HELPER.run_revit_script(script_subfolder, func_name)



    
@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():

    try:
        doc.Title
    except:
        return
    
    if EnneadTab.ENVIRONMENT_CONSTANTS.is_Revit_limited():
        return

    if not EnneadTab.ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return

    
    play_success_sound()
    update_sync_time_record()



    if random.random() < 0.3:
        warn_non_enclosed_area()
        warn_non_enclosed_room()
    output = script.get_output()
    output.close_others(all_open_outputs = True)

    warn_bad_sized_meeting_rm()



    update_project_2314()
    update_project_2306()
    update_project_2151()
    update_project_1643()

    update_with_generic_healthcare_tool()


    update_sync_queue()


    ENNEAD_LOG.warn_revit_session_too_long(non_interuptive = False)





    if ENNEAD_LOG.is_money_negative():
        print ("Your Current balance is {}".format(ENNEAD_LOG.get_current_money()))

    ENNEAD_LOG.update_local_warning(doc)


    play_text_to_speech_audio()
    
    update_sheet_name()
    update_working_view_name()
    
    envvars.set_pyrevit_env_var("IS_DOC_CHANGE_HOOK_ENABLED", True)





#################################################################
if __name__ == "__main__":
    main()
