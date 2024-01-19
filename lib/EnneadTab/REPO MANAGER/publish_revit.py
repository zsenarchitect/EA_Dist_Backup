

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
        
        import VERSION_CONTROL, NOTIFICATION, SOUNDS
        
        
        publish_stable_version = True
        publish_beta_version = True
        
        VERSION_CONTROL._publish_Revit_source_code(publish_stable_version, publish_beta_version)

        SOUNDS.play_sound("sound effect_mario stage clear.wav")
        note = "Revit Published!"
        NOTIFICATION.messenger(main_text=note)
        print (note)
    except:
        pass
        print (traceback.format_exc())

    print ("TO-DO: add try git push for dist repo")
        

    


if __name__ == "__main__":
    main()
