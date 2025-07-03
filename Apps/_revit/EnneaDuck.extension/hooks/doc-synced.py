import os
import random
import io
import imp
from pyrevit import EXEC_PARAMS
from Autodesk.Revit import DB # pyright: ignore
from pyrevit.coreutils import envvars
DOC = EXEC_PARAMS.event_args.Document


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, FOLDER, SOUND, LOG, NOTIFICATION, SPEAK, MODULE_HELPER, ENVIRONMENT, EMAIL, USER, DATA_FILE, IMAGE, SPEAK, TIME 
from EnneadTab.REVIT import REVIT_SYNC, REVIT_FORMS, REVIT_EVENT, REVIT_SPATIAL_ELEMENT, REVIT_PROJ_DATA
__title__ = "Doc Synced Hook"


REGISTERED_AUTO_PROJS = ["1643_lhh bod-a_new",
                         "1643_lhh_bod-a_existing",
                        "2151_a_ea_nyuli_cup_ext",
                        "2151_a_ea_nyuli_hospital_ext",
                        "2151_A_EAEC_NYULI_Hospital_INT",
                        "2151_a_ea_nyuli_parking east",
                        "2151_a_ea_nyuli_parking west",
                        "2151_a_ea_nyuli_site",
                        "2151_A_EA_NYU Melville_Site",
                        "2151_A_EA_NYU Melville_Hospital Existing",
                        "2151_A_EA_NYU Melville_Hospital New",
                        "2151_A_EA_NYU Melville_Garage North",
                        "2151_A_EA_NYU Melville_Garage South",
                        "2151_A_EA_NYU Melville_CUP",
                        "2148_textile museum",
                        "2419_Xiong An SinoChem",
                        "Facade System"]

REGISTERED_AUTO_PROJS = [x.lower() for x in REGISTERED_AUTO_PROJS]

def warn_non_enclosed_area(doc):
    # Validate document before proceeding
    if doc is None:
        print("Warning: Cannot check areas - document is None")
        return
    
    try:
        areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
        non_closed, non_placed = REVIT_SPATIAL_ELEMENT.filter_bad_elements(areas)
        note = ""
        if len(non_closed) > 0:
            note += "There are {} non-enclosed areas in need of attention.\n".format(len(non_closed))
        if len(non_placed) > 0:
            note += "There are {} non-placed areas in need of attention.".format(len(non_placed))
        if note:
            NOTIFICATION.messenger(note)
    except Exception as e:
        print("Error checking non-enclosed areas: {}".format(str(e)))


def warn_non_enclosed_room(doc):
    # Validate document before proceeding
    if doc is None:
        print("Warning: Cannot check rooms - document is None")
        return
    
    try:
        rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
        non_closed, non_placed = REVIT_SPATIAL_ELEMENT.filter_bad_elements(rooms)
        note = ""
        if len(non_closed) > 0:
            note += "There are {} non-enclosed rooms in need of attention.\n".format(len(non_closed))
        if len(non_placed) > 0:
            note += "There are {} non-placed rooms in need of attention.".format(len(non_placed))
        if note:
            NOTIFICATION.messenger(note)
    except Exception as e:
        print("Error checking non-enclosed rooms: {}".format(str(e)))



def DEPRECIATED_update_project_2151(doc):

    if not doc.Title.lower().startswith("2151_"):
        return
    


    folder = "EnneadTab Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "update_parking_data"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False, is_from_sync_hook = True)


    return
    
    if USER.USER_NAME not in ["sha.li", "szhang"]:
        return
    
    folder = "EnneadTab Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "color_pills"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    
    
    
    folder = "EnneadTab Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "all_in_one_checker"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)



    folder = "EnneadTab Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "confirm_RGB"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)




def update_project_2314(doc):

    if "2314_a-455 1st ave" not in doc.Title.lower():
        return
    
    folder = "EnneadTab Tailor.tab\\Proj. 2314.panel\\First Ave.pulldown"
    func_name = "all_in_one_checker"
    

    
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    
    return


def update_project_1643(doc):
    update_new(doc)
    update_existing(doc)


def update_new(doc):
    if "1643_lhh bod-a_new" not in doc.Title.lower():
        return


    folder = "EnneadTab Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_level_relative_value"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    
    folder = "EnneadTab Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_keyplan"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)


    

def update_existing(doc):
    if "1643_lhh bod-a_existing" not in doc.Title.lower():
        return


    folder = "EnneadTab Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_grid_bldgId"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    folder = "EnneadTab Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_level_relative_value"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    folder = "EnneadTab Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_keyplan"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    



    
def DEPRECIATED_update_DOB_numbering(doc):
    folder = "EnneadTab.tab\\ACE.panel"
    func_name = "update_DOB_page"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)


def DEPRECIATED_update_sheet_name(doc):

    try:
        doc.Title
    except Exception as e:
        if USER.USER_NAME == "szhang":
            print (str(e))
        return

    # Additional document validation
    if doc is None:
        print("Warning: Cannot update sheet names - document is None")
        return

    if doc.Title.lower() not in REGISTERED_AUTO_PROJS:
        return

    try:
        script = "EnneadTab.tab\\Tools.panel\\general_renamer.pushbutton\\general_renamer_script.py"
        func_name = "rename_views"
        sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
        is_default_format = True
        show_log = False
        MODULE_HELPER.run_revit_script(script, func_name, doc, sheets, is_default_format, show_log)
    except Exception as e:
        print("Error updating sheet names: {}".format(str(e)))

    
def DEPRECIATED_update_working_view_name(doc):
    try:
        doc.Title
    except:
        return

    # Additional document validation
    if doc is None:
        print("Warning: Cannot update working view names - document is None")
        return

    if doc.Title.lower() not in REGISTERED_AUTO_PROJS:
        return

    try:
        script = "EnneadTab.tab\\Manage.panel\\working_view_cleanup.pushbutton\\manage_working_view_script.py"
        func_name = "modify_creator_in_view_name"

        fullpath = "{}\\{}".format(ENVIRONMENT.REVIT_PRIMARY_EXTENSION, script)
        import imp
        ref_module = imp.load_source("manage_working_view_script", fullpath)

        views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
        no_sheet_views = filter(ref_module.is_no_sheet, views)
        is_adding_creator = True
        MODULE_HELPER.run_revit_script(script, func_name, no_sheet_views, is_adding_creator)
    except Exception as e:
        print("Error updating working view names: {}".format(str(e)))

def update_project_2306(doc):
    if "universal hydrogen" not in doc.Title.lower():
        return
    # if not USER.IS_DEVELOPER:
    #     return

    folder = "EnneadTab Tailor.tab\\Proj. 2306.panel\\Universal Hydro.pulldown"
    func_name = "factory_internal_check"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
 
    
    

def update_sync_queue(doc):

    # dont need to do anything if pre-sycn chech was cancelled,
    if REVIT_EVENT.is_sync_cancelled():
        return


    log_file = FOLDER.get_shared_dump_folder_file("SYNC_QUEUE_{}". format(doc.Title))
  

    if not os.path.exists(log_file):
        with io.open(log_file, "w", encoding = "utf-8"): # if not existing then create
            pass

    queue = DATA_FILE.get_list(log_file)

    
    OUT = []


    for item in queue:
        if USER.USER_NAME in item:
            #this step remove current user name from any place in wait list, either beginging or last
            continue
        OUT.append(item)
        
        

    if not DATA_FILE.set_list(OUT, log_file):
        NOTIFICATION.messenger ("Your account have no access to write in DB folder.")
        return

    if REVIT_EVENT.is_sync_queue_disabled():
        # when  gloabl sync queue disabled, dont want to see dialogue, but still want to clear name from log file
        return

    if len(OUT) == 0:
        return
    try:
        next_user = OUT[0].split("]")[-1]
        # next user found!! if this step can pass
    except Exception as e:
        return


    EMAIL.email(receiver_email_list="{}@ennead.com".format(next_user),
                            subject="Your Turn To Sync!",
                            body="Hi there, it is your turn to sync <{}>!".format(doc.Title),
                            body_image_link_list=[IMAGE.get_image_path_by_name("meme_you_sync_first.jpg")])

    REVIT_FORMS.notification(main_text = "[{}]\nshould sync next.".format(next_user), sub_text = "Expect slight network lag between SH/NY server to transfer waitlist file.", window_width = 500, window_height = 400, self_destruct = 15)


def warn_revit_session_too_long():
    uptime = TIME.get_revit_uptime(return_number = True)
    if uptime > 3 * 24 * 60 * 60:
        NOTIFICATION.messenger("Revit has been open for {}. Please consider restarting your computer.".format(TIME.get_revit_uptime()))
        return
    if uptime > 5 * 24 * 60 * 60:
        NOTIFICATION.messenger("Ahhhh! Revit has been open for {}. Please consider restarting your computer soon.".format(TIME.get_revit_uptime()))
        return
    if uptime > 10 * 24 * 60 * 60:
        NOTIFICATION.messenger("This is ridiculous! Revit has been open for {}. Please consider restarting your computer.".format(TIME.get_revit_uptime()))
        return
    if uptime > 15 * 24 * 60 * 60:
        NOTIFICATION.messenger("I am begging you! please restart your computer. Revit has been open for {}. ".format(TIME.get_revit_uptime()))
        return

def play_success_sound():
    file = 'sound_effect_mario_1up.wav'
    SOUND.play_sound(file)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error(is_silent=True)
def doc_synced(doc):

    # Comprehensive document validation at the start
    if doc is None:
        print("Error: doc_synced received None document, skipping sync operations")
        return
    
    try:
        # Test document validity by accessing basic properties
        doc_title = doc.Title
        if not doc_title:
            print("Error: doc_synced received document with empty title, skipping sync operations")
            return
        
        # Additional validation to ensure document methods are available
        if not hasattr(doc, "GetElement"):
            print("Error: doc_synced received invalid document object, skipping sync operations")
            return
            
    except Exception as e:
        print("Error: doc_synced document validation failed: {}, skipping sync operations".format(str(e)))
        return

    play_success_sound()
    REVIT_SYNC.update_last_sync_data_file(doc)


    update_sync_queue(doc)
    

    if random.random() < 0.1:
        warn_non_enclosed_area(doc)
    if random.random() < 0.1:
        warn_non_enclosed_room(doc)

    if REVIT_EVENT.is_all_sync_closing():
        return
        


    if not REVIT_PROJ_DATA.is_setup_project_data_para_exist(doc):
        run_legacy_updates(doc)
    else:
        proj_data = REVIT_PROJ_DATA.get_revit_project_data(doc)
        if proj_data:
            if proj_data.get("area_tracking", {}).get("auto_update_enabled", False):
                update_area_tracking(doc)
            if proj_data.get("is_update_view_name_format", False):
                update_view_names(doc)

    if USER.IS_DEVELOPER:
        SPEAK.speak("Document {} has finished syncing.".format(doc.Title))
        NOTIFICATION.messenger("Document {} has finished syncing.".format(doc.Title))


    warn_revit_session_too_long()
    return


    update_project_2314(doc)
    update_project_2306(doc)
    update_project_1643(doc)






    LEGACY_LOG.warn_revit_session_too_long(non_interuptive = False)





    if LEGACY_LOG.is_money_negative():
        print ("Your Current balance is {}".format(LEGACY_LOG.get_current_money()))

    LEGACY_LOG.update_local_warning(doc)



    
    
    envvars.set_pyrevit_env_var("IS_DOC_CHANGE_HOOK_ENABLED", True)
    



def run_legacy_updates(doc):
    """Run all the deprecated update functions - they're old but gold!"""
    DEPRECIATED_update_DOB_numbering(doc)
    DEPRECIATED_update_sheet_name(doc)
    DEPRECIATED_update_working_view_name(doc)
    DEPRECIATED_update_project_2151(doc)

def update_view_names(doc):
    """Update view names - because nobody likes unnamed views wandering around!"""
    # Validate document before proceeding
    if doc is None:
        print("Error: Cannot update view names - document is None")
        return
    
    try:
        # Test document validity by accessing a basic property
        doc_title = doc.Title
        if not doc_title:
            print("Error: Cannot update view names - document title is empty")
            return
    except Exception as e:
        print("Error: Cannot update view names - document validation failed: {}".format(str(e)))
        return
    
    try:
        # Update sheet views
        script = "EnneadTab.tab\\Tools.panel\\general_renamer.pushbutton\\general_renamer_script.py"
        sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
        MODULE_HELPER.run_revit_script(script, "rename_views", doc, sheets, True, False)

        # Update working views
        script = "EnneadTab.tab\\Manage.panel\\working_view_cleanup.pushbutton\\manage_working_view_script.py"
        fullpath = "{}\\{}".format(ENVIRONMENT.REVIT_PRIMARY_EXTENSION, script)
        ref_module = imp.load_source("manage_working_view_script", fullpath)
        
        views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
        no_sheet_views = filter(ref_module.is_no_sheet, views)
        MODULE_HELPER.run_revit_script(script, "modify_creator_in_view_name", no_sheet_views, True)
    except Exception as e:
        print("Error during view names update: {}".format(str(e)))
        ERROR_HANDLE.print_note("View names update failed: {}".format(str(e)))

def update_area_tracking(doc):
    """Update area tracking - keeping those square feet in check!"""
    # Validate document before proceeding
    if doc is None:
        print("Error: Cannot update area tracking - document is None")
        return
    
    try:
        # Test document validity by accessing a basic property
        doc_title = doc.Title
        if not doc_title:
            print("Error: Cannot update area tracking - document title is empty")
            return
    except Exception as e:
        print("Error: Cannot update area tracking - document validation failed: {}".format(str(e)))
        return
    
    try:
        fullpath = "{}\\EnneadTab.tab\\Tools.panel\\generic_healthcare_tool.pushbutton\\dgsf_chart.py".format(
            ENVIRONMENT.REVIT_PRIMARY_EXTENSION)
        ref_module = imp.load_source("dgsf_chart", fullpath)
        ref_module.dgsf_chart_update(doc, show_log=False)
    except Exception as e:
        print("Error during area tracking update: {}".format(str(e)))
        ERROR_HANDLE.print_note("Area tracking update failed: {}".format(str(e)))

def validate_document(doc, operation_name="operation"):
    """
    Centralized document validation function.
    
    Args:
        doc: Revit document to validate
        operation_name: Name of the operation for logging purposes
    
    Returns:
        bool: True if document is valid, False otherwise
    """
    if doc is None:
        print("Error: Cannot perform {} - document is None".format(operation_name))
        return False
    
    try:
        # Test document validity by accessing basic properties
        doc_title = doc.Title
        if not doc_title:
            print("Error: Cannot perform {} - document title is empty".format(operation_name))
            return False
        
        # Additional validation to ensure document methods are available
        if not hasattr(doc, "GetElement"):
            print("Error: Cannot perform {} - invalid document object".format(operation_name))
            return False
            
        return True
            
    except Exception as e:
        print("Error: Cannot perform {} - document validation failed: {}".format(operation_name, str(e)))
        return False

#################################################################
if __name__ == "__main__":
    doc_synced(DOC)

