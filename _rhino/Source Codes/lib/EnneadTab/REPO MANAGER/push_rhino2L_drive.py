

def main():
    try:
        import os
        # print (__file__)
        parent_folder = os.path.dirname(os.path.dirname(__file__))
        # print (parent_folder)
        
        
        import traceback
        import sys
        sys.path.append(parent_folder)
        # print (sys.path)
        
        import VERSION_CONTROL, NOTIFICATION
        VERSION_CONTROL._push_core_module_from_rhino_repo_to_L_drive()
        note = "core module:\nRHINO REPO------->RHINO L Drive"
        NOTIFICATION.messenger(main_text=note)
        print (note)
    except:
        pass
        print (traceback.format_exc())
        

    


if __name__ == "__main__":
    main()