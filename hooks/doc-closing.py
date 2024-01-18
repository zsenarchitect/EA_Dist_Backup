from pyrevit import EXEC_PARAMS


import EnneadTab

doc = EXEC_PARAMS.event_args.Document

def remove_last_sync_data_file(doc):
    script_subfolder = 'Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py'
    func_name = 'remove_last_sync_data_file'
    EnneadTab.MODULE_HELPER.run_revit_script(script_subfolder, func_name,doc)
    return


    import imp
    full_file_path = r'C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Utility.panel\exe_1.stack\LAST_SYNC_MONITOR.pushbutton\update_last_sync_datafile_script.py'
    if not EnneadTab.USER.is_SZ():
        full_file_path = EnneadTab.FOLDER.remap_filepath_to_folder(full_file_path)
    ref_module = imp.load_source("update_last_sync_datafile_script", full_file_path)

    ref_module.remove_last_sync_data_file(doc)


def check_unrelingquished_elements(doc):
    pass

@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():
    remove_last_sync_data_file(doc)
    check_unrelingquished_elements(doc)

###################################################
if __name__ == '__main__':
    main()
    
    
