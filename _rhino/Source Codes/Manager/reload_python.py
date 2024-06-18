from imp import reload as reload
import sys
import os



def main():
    reload_enneadtab_module()
    reload_ea_utility_module()

    #EA_UTILITY.add_alias_set()
    import alias_manager
    alias_manager.add_alias_set()

def reload_ea_utility_module():
    return
    # sys.path.append("..\lib")
    # import EA_UTILITY
    # import EA_FORMS
    # import EA_FORMS_LIST_SELECTION
    # import EA_FORMS_LIST2LIST_SELECTION
    # import EA_SOUND
    # import EA_TEXT2SPEECH
    # import EA_FORMS_NOTIFICATION


    # reload(EA_UTILITY)
    # reload(EA_FORMS)
    # reload(EA_FORMS_LIST_SELECTION)
    # reload(EA_FORMS_LIST2LIST_SELECTION)
    # reload(EA_SOUND)
    # reload(EA_TEXT2SPEECH)
    # reload(EA_FORMS_NOTIFICATION)



def reload_enneadtab_module():
    path = r"C:\Users\szhang\github\EnneadTab-for-Rhino\Source Codes\lib"
    if os.path.exists(path):
        pass
    else:
        path = r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib'
    sys.path.append(path)
    #from EnneadTab import ENVIRONMENT
    #sys.path.append(r'{}\Source Codes\lib'.format(ENVIRONMENT.get_EnneadTab_For_Rhino_root()))
    import EnneadTab


    reload(EnneadTab)
    print("######## in reload")
    for file in EnneadTab.FOLDER.get_filenames_in_folder('{}\EnneadTab'.format(path)):
        if ".py" in file:

            print(file.replace(".py", ""))
            #reload(  getattr(EnneadTab, file.replace(".py", ""))  )
            #reload(  file.replace(".py", "")  )
    print("%%%%%%%%")

    print(dir(EnneadTab))
    """
    reload(EnneadTab.FOLDER)
    reload(EnneadTab.ENVIRONMENT)
    reload(EnneadTab.VERSION_CONTROL)
    reload(EnneadTab.ERROR_HANDLE)
    reload(EnneadTab.NOTIFICATION)
    reload(EnneadTab.MODULE_HELPER)
    #reload(EnneadTab.IMAGES)
    reload(EnneadTab.EMAIL)
    reload(EnneadTab.DATA_FILE)


    reload(EnneadTab.EXCEL)
    reload(EnneadTab.LOG)
    reload(EnneadTab.MATH)

    reload(EnneadTab.PDF)
    reload(EnneadTab.SOUNDS)
    reload(EnneadTab.SPEAK)
    reload(EnneadTab.TIME)
    reload(EnneadTab.USER)
    """



    EnneadTab.NOTIFICATION.toast(main_text = "Python Engine Reloaded")



####################
if __name__ == "__main__":
    main()
