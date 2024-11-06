#!/usr/bin/python
# -*- coding: utf-8 -*-
import REVIT_APPLICATION
try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
    from pyrevit import script #
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()



from EnneadTab.REVIT import REVIT_FORMS, REVIT_VIEW, REVIT_EVENT, REVIT_APPLICATION
from EnneadTab import CONFIG, EXE, DATA_FILE, NOTIFICATION, SPEAK, ERROR_HANDLE, FOLDER

import time


SYNC_MONITOR_FILE = "last_sync_record_data.sexyDuck"




@ERROR_HANDLE.try_catch_error()
def kill_record():
    from pyrevit import forms

    with DATA_FILE.update_data(SYNC_MONITOR_FILE) as data:
        if not data:
            NOTIFICATION.messenger(main_text = "No Active Record Found!!!")
            return

        """
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "{} :Last Record {}".format(self.item)

        ops = [MyOption(key, value) for key, value in data]
        """
        selected_keys = forms.SelectFromList.show(data.keys(),
                                                multiselect = True,
                                                title = "Want to kill curtain record from last sync monitor?",
                                                button_name = 'Kill Selected Record(s)')
        if not selected_keys:
            return

        for key in selected_keys:
            del data[key]




@ERROR_HANDLE.try_catch_error(is_silent=True)
def update_last_sync_data_file(doc):

    if "detach" in doc.Title.lower():
        return

    # old_data = DATA_FILE.get_data(SYNC_MONITOR_FILE)
    # if old_data:
    #     for key, value in old_data.items():
    #         if time.time() - value  > 60*60*24:#record older than 24 hour should be removed
    #             print ("deleting key", key)
    #             del old_data[key]
    # else:
    #     old_data = dict()

    # old_data[doc.Title] = time.time()
    # DATA_FILE.set_data(old_data, SYNC_MONITOR_FILE)
    # return 



    with DATA_FILE.update_data(SYNC_MONITOR_FILE, keep_holder_key=time.time()) as data:
        if data:

            for key, value in data.items():
                if key == "key_holder":
                    continue
                if time.time() - value  > 60*60*24:#record older than 24 hour should be removed
                    print ("deleting key", key)
                    del data[key]
        else:
  
            data = dict()
        

        if doc.IsModified:
            punish_long_gap_time(data)


   
        data[doc.Title] = time.time()



    


@ERROR_HANDLE.try_catch_error(is_silent=True)
def remove_last_sync_data_file(doc):

    with DATA_FILE.update_data(SYNC_MONITOR_FILE) as data:
        if not data:
            return

        if doc.Title in data.keys():
            del data[doc.Title]


@ERROR_HANDLE.try_catch_error()
def punish_long_gap_time(data):

    now = time.time()
    min_max = 90
    for key, value in data.items():
        if now - value  > 60 * min_max:
            
            #print int( (now - value - 60 * min_max) / 60)
            try:
                pass
                # ENNEAD_LOG.sync_gap_too_long(mins_exceeded = int( (now - value - 60 * min_max) / 60), doc_name = key )
            except:
                pass
                # ENNEAD_LOG.sync_gap_too_long(mins_exceeded = int( (now - value - 60 * min_max) / 60) )





@ERROR_HANDLE.try_catch_error()
def is_doc_opened(doc):
    data = DATA_FILE.get_data(SYNC_MONITOR_FILE)
    if not data:
        return False

    if doc.Title in data.keys():
        NOTIFICATION.messenger(main_text = "Wait a minutes...\nThis document seems to be opened already.")
        SPEAK.speak("Unless you recently crashed Revit, this document seems to be opened already. You should prevent opening same file on same machine, because this will confuse central model which local version to allow sync.")
        REVIT_FORMS.notification(main_text = "This document seems to be opened already in other session.\nOr maybe recently crashed.\nAnyway, I have detected the record already existing.",
                                        sub_text = "Double check if this double opening is intentional.\nThere is another possibility that your last session crashed and the exit is not logged. In that case, please ignore this message box.",
                                        self_destruct = 20)
        return True
    return False

@ERROR_HANDLE.try_catch_error()
def is_hate_sync_monitor():
    return CONFIG.get_setting("radio_bt_sync_monitor_never", False)

@ERROR_HANDLE.try_catch_error()
def start_monitor():

    if is_hate_sync_monitor():
        return

    EXE.try_open_app("LastSyncMonitor")





def do_you_want_to_sync_and_close_after_done():
    will_sync_and_close = False
    res = REVIT_FORMS.dialogue(main_text = "Sync and Close after done?", options = ["Yes", "No"])
    if res == "Yes":
        will_sync_and_close = True

    return will_sync_and_close



def sync_and_close(close_others = True, disable_sync_queue = True):

    from pyrevit import script
    from pyrevit.coreutils import envvars
    output = script.get_output()
    killtime = 30
    output.self_destruct(killtime)

    
    REVIT_EVENT.set_sync_queue_enable_stage(disable_sync_queue)
    if close_others:
        envvars.set_pyrevit_env_var("IS_AFTER_SYNC_WARNING_DISABLED", True)
        # if you descide to close others, they should be no further warning. Only recover that warning behavir in DOC OPENED event


    def get_docs():
        try:
            doc = __revit__.ActiveUIDocument.Document # pyright: ignore
            docs = doc.Application.Documents
            ERROR_HANDLE.print_note("get docs using using method 1")
        except:
            docs = __revit__.Documents #pyright: ignore
            ERROR_HANDLE.print_note("get docs using using method 2")
        ERROR_HANDLE.print_note( "Get all docs, inlcuding links and family doc = {}".format(str([x.Title for x in docs])))
        return docs

    ERROR_HANDLE.print_note("getting docs before sync")
    docs = get_docs()
    logs = []

    for doc in docs:

        if doc.IsLinked or doc.IsFamilyDocument:
            continue

        try:
            REVIT_VIEW.switch_to_sync_draft_view(doc)
        except Exception as e:
            ERROR_HANDLE.print_note(e)
            continue
        # print "#####"
        # print ("# {}".format( doc.Title) )
        #with revit.Transaction("Sync {}".format(doc.Title)):
        t_opts = DB.TransactWithCentralOptions()
        #t_opts.SetLockCallback(SynchLockCallBack())
        s_opts = DB.SynchronizeWithCentralOptions()
        s_opts.SetRelinquishOptions(DB.RelinquishOptions(True))

        s_opts.SaveLocalAfter = True
        s_opts.SaveLocalBefore = True
        s_opts.Comment = "EnneadTab Batch Sync"
        s_opts.Compact = True


        try:
            doc.SynchronizeWithCentral(t_opts,s_opts)
            logs.append( "\tSync [{}] Success.".format(doc.Title))
            import SPEAK
            SPEAK.speak("Document {} has finished syncing.".format(doc.Title))
        except Exception as e:
            logs.append( "\tSync [{}] Failed.\n{}\t".format(doc.Title, e))

        REVIT_VIEW.switch_from_sync_draft_view()
    
    envvars.set_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED", not(disable_sync_queue))
    for log in logs:
        ERROR_HANDLE.print_note( log)
    if not close_others:
        return

    ERROR_HANDLE.print_note("getting docs before active safty doc")
    docs = get_docs()
    REVIT_APPLICATION.open_safety_doc_family()
    ERROR_HANDLE.print_note("active doc set as safety doc")
    for doc in docs:
        if doc is None:
            ERROR_HANDLE.print_note("doc is None, skip")
            continue
        try:
            if doc.IsLinked:
                ERROR_HANDLE.print_note("doc {} is a link doc, skip".format(doc.Title))
                continue
        except Exception as e:
            ERROR_HANDLE.print_note ("Sync&Close Info:")
            ERROR_HANDLE.print_note (e)
            ERROR_HANDLE.print_note(str(doc))
            continue

        title = doc.Title
        try:
            ERROR_HANDLE.print_note ("Trying to close [{}]".format(title))
            doc.Close(False)
            doc.Dispose()
        except Exception as e:
            ERROR_HANDLE.print_note (e)
            try:
                ERROR_HANDLE.print_note ("skip closing [{}]".format(title))
            except:
                ERROR_HANDLE.print_note ("skip closing some doc")
        """
        try to open a dummy family rvt file in the buldle folder and switch to that as active doc then close original active doc
        """


################## main code below #####################
if __name__== "__main__":
    output = script.get_output()
    output.close_others()
    


