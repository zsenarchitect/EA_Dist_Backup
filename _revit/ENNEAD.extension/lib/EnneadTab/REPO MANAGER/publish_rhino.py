

def publish_rhino():
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
        VERSION_CONTROL.publish_Rhino_source_code(deep_copy=True)
        note = "RHINO Published!"
        NOTIFICATION.messenger(main_text=note)
        print (note)
    except:
        pass
        print (traceback.format_exc())
        

    


if __name__ == "__main__":
    publish_rhino()