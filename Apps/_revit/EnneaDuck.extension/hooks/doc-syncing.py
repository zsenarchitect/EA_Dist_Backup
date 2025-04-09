from pyrevit import EXEC_PARAMS
from Autodesk.Revit import DB # pyright: ignore
import random
import io

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import MODULE_HELPER, VERSION_CONTROL, ERROR_HANDLE, LOG, DATA_FILE, TIME, USER, DUCK, CONFIG, FOLDER, TIMESHEET
from EnneadTab.REVIT import REVIT_FORMS, REVIT_SELECTION, REVIT_EVENT

__title__ = "Doc Syncing Hook"
DOC = EXEC_PARAMS.event_args.Document



def update_2151(doc):
    if doc.Title.lower() in[ "2151_a_ea_nyuli_hospital_ext",
                            "2151_A_EA_NYU Melville_Hospital Existing"]:

        folder = "EnneadTab Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
        func_name = "update_dummy_patient_room"
        MODULE_HELPER.run_revit_script(folder, func_name, doc)

        folder = "EnneadTab Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
        func_name = "dgsf_area_data_check"
        MODULE_HELPER.run_revit_script(folder, func_name, doc)

        update_modified_date(doc)

    if not doc.Title.lower().startswith("2151_"):
        return
    folder = "EnneadTab Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "update_material_setting"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

def check_sync_queue(doc):
    """
    return True is sync can go
    return False is sync have been stopped
    """

    log_file = FOLDER.get_shared_dump_folder_file("SYNC_QUEUE_{}". format(doc.Title))
    
    try:
        with io.open(log_file, "r", encoding = "utf-8"):
            pass
    except:
        with io.open(log_file, "w+", encoding = "utf-8"): # if not existing then create
            pass
    queue = DATA_FILE.get_list(log_file)
    wait_num = len(queue)
    time = TIME.get_formatted_current_time()
    user_name = USER.USER_NAME

    # define default value for succeful sync
    # envvars.set_pyrevit_env_var("IS_SYNC_CANCELLED", False)

    data = "[{}]{}".format(time, user_name)

    # clean very old record from queue
    bad_record = []
    for existing_item in queue:
        try:
            record_unix_time = existing_item.split("]")[0].split("_")[1]
        except:
            continue

        #the checking include current user, if this user has a record too old, he/she should go to the back of the line.
        if TIME.time_has_passed_too_long(record_unix_time):
            #default is 30mins
            bad_record.append(existing_item)
            #might make too old record removed later but not here,

    for bad in bad_record:
        queue.remove(bad)
        print ("Removing record that is older than 2 hours so it is not holding queue: {}".format(bad))


    # add to back of the list only if not registered before. Also only save the text if there is a change in queue
    for existing_item in queue:
        if user_name in existing_item:
            break
    else:
        queue.append(data)
        try:
            DATA_FILE.set_list(queue, log_file)
        except:
            # sh cannot write to L drive 
            return True
        

    if wait_num == 0 or user_name in queue[0] or REVIT_EVENT.is_sync_queue_disabled():

        # no one is on wait list now, should go ahead sync
        # or maybe username is at the begining of line, he can go sync as well.
        #or processing by sync all and close---> no dialogue wanted, but still write name to log
        return True


    current_queue = "Current Sync Queue:\n"
    quene_length = len(queue)
    for item in queue:
        current_queue += "\n  -" + item
    current_queue += "\n\nWhen There are no other people on the list, or you are the first on the wait list you can sync normally.\nRecord older than 30mins will be removed from the queue to avoid holding line too long."
    opts = [["I will join the waitlist and sync later.(Click 'Close' when you see Revit Sync Fail on next step, it just means the sync has been cancelled. You still hold position on the waitlist.)","Resume working and try syncing later.(+ $50 EA Coins)"], ["I don't care! Sync me now!","Jump in line will make other people who are syncing has to wait longer.(- $100 EA Coins for every position cut line)"]]
    res = REVIT_FORMS.dialogue(main_text = "There are other people queuing before you, do you want to resume working and try sync later?\n\nYour name has been added to the wait list even if you cancel current sync.\n\n[You are also welcomed to save local while waiting.]",
                            sub_text = current_queue,
                            options = opts)
    if res == opts[1][0]:
        # LEGACY_LOG.sync_queue_cut_in_line(quene_length - 1)
        return True

    # if after all checking you are this step, that means you want to cancel now
    EXEC_PARAMS.event_args.Cancel()
    # envvars.set_pyrevit_env_var("IS_SYNC_CANCELLED", True)
    # LEGACY_LOG.sync_queue_wait_in_line()

    
    if CONFIG.get_setting("toggle_bt_is_duck_allowed", False):
        DUCK.quack()
 
    try:
        doc.Save()

    except Exception as e:

        pass
    return False





@ERROR_HANDLE.try_catch_error(is_pass=True)
def fill_drafter_info(doc):
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).ToElements()
    free_sheets = REVIT_SELECTION.filter_elements_changable(all_sheets)
    
    t = DB.Transaction(doc, "Fill Drafter Info")
    t.Start()
    for sheet in free_sheets:
        sheet.LookupParameter("Drawn By").Set(DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, sheet.Id).Creator)
        
        sheet.LookupParameter("Designed By").Set(DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, sheet.Id).LastChangedBy)
    t.Commit()



def update_modified_date(doc):
    if random.random() < 0.9:
        return

    # Get collectors for both categories at once
    collectors = {
        "sheets": DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets),
        "views": DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Views)
    }

    for collector in collectors.values():
        sample_element = collector.FirstElement()
        if not sample_element.LookupParameter("ModifiedDate"):
            continue

        # Get all elements and process in single transaction
        t = DB.Transaction(doc, "Update Modified Date")
        t.Start()
        for element in collector.ToElements():
            if REVIT_SELECTION.is_borrowed(element):
                element.LookupParameter("ModifiedDate").Set(TIME.get_YYYY_MM_DD())
        t.Commit()

    
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error(is_silent=True)
def doc_syncing(doc):
    VERSION_CONTROL.update_EA_dist()


    can_sync = check_sync_queue(doc)
    if can_sync:
        # LEGACY_LOG.update_account_by_local_warning_diff(doc)
        pass

    if REVIT_EVENT.is_all_sync_closing():
        return

    # do this after checking ques so the primary EXE_PARAM is same as before
    fill_drafter_info(doc)
    
    update_2151(doc)

    TIMESHEET.update_timesheet(doc.Title)


    

#################################################################

if __name__ == "__main__":
    doc_syncing(DOC)