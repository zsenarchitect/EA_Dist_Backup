"""Reload pyRevit into new session."""
__title__ = "Reload\nEnneadTab"
__context__ = 'zero-doc'
# -*- coding=utf-8 -*-
#pylint: disable=import-error,invalid-name,broad-except
from pyrevit import EXEC_PARAMS
from pyrevit import script
from pyrevit.loader import sessionmgr
from pyrevit.loader import sessioninfo
import EA_UTILITY
import EnneadTab


import traceback

def reload_action():
    res = True
    if EXEC_PARAMS.executed_from_ui:
        pass
        """
        if not EA_UTILITY.is_SZ():
            EA_UTILITY.dialogue(icon = "warning", main_text = "Only when instructed to do so, you need to manual reload from here. When you start a new revit session, EnneadTab will always load the latest. \n\nNew release usually happens over weekend, but occassionally new update will be released during office hour(NY,SH timezone reason).")
        """
        # res = forms.alert("Only when instructed to do so, you need to manual reload from here. When you start a new revit session, EnneadTab will always load the latest. \nNew release usually happens over weekend, but occassionally new update will be released during office hour(NY,SH timezone reason)." )


    if res:
        logger = script.get_logger()
        results = script.get_results()

        # re-load pyrevit session.
        logger.info('Reloading....')
        sessionmgr.reload_pyrevit()

        results.newsession = sessioninfo.get_session_uuid()
        EA_UTILITY.set_doc_change_hook_depressed(is_depressed = False)



def update_repo():

    EnneadTab.GIT.run_updater()


@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():
    
    try:
        update_repo()
    except Exception as e:
        print (traceback.format_exc())
    
    reload_action()

##############################################
if __name__ == '__main__':
    main()