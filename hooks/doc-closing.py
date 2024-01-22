from pyrevit import EXEC_PARAMS


import EnneadTab

doc = EXEC_PARAMS.event_args.Document

def remove_last_sync_data_file(doc):
    script_subfolder = 'Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py'
    func_name = 'remove_last_sync_data_file'
    EnneadTab.MODULE_HELPER.run_revit_script(script_subfolder, func_name,doc)



@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():
    remove_last_sync_data_file(doc)


###################################################
if __name__ == '__main__':
    main()
    
    
