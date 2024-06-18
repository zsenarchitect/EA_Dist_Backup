
import sys
sys.path.append("..\lib")
import EnneadTab
import random
import os
import rhinoscriptsyntax as rs


def tell_a_joke():


    main_text = EnneadTab.FUN.JOKES.give_me_a_joke(talk = False)
    EnneadTab.NOTIFICATION.duck_pop(main_text)        
    audio_folder = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published\\ENNEAD.extension\\Ennead.tab\\Utility.panel\\exe_2.stack\\duck_pop\\audio"
    
    # pick a random duck sound from the folder
    duck_sound_list = [x for x in os.listdir(audio_folder) if x.endswith(".wav")]
    audio = os.path.join(audio_folder,random.choice(duck_sound_list))

    EnneadTab.SOUNDS.play_sound(audio)
       
       
        
@EnneadTab.ERROR_HANDLE.try_catch_error
def tell_many_jokes():
    tell_a_joke()
    return
    for i in range(5):
        tell_a_joke()
        rs.Sleep(10000)

######################  main code below   #########
if __name__ == "__main__":
    tell_many_jokes()



