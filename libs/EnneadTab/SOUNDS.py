#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import ENVIRONMENT
import ENVIRONMENT_CONSTANTS

def play_sound(file = "sound effect_popup msg3.wav"):
    if not ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return
    #print "in = " + file
    #case 1: come in as wav file only----> add fun folder in front
    #case 2: come in any format of path
    if not os.path.exists(file):
        folder = '{}\\Source Codes\\Fun\\sound effects'.format(ENVIRONMENT_CONSTANTS.PUBLISH_FOLDER_FOR_RHINO)
        path = folder + "\\" + file
        if not os.path.exists(path):
            path = "{}\\{}".format(ENVIRONMENT_CONSTANTS.CORE_AUDIOS_FOLDER_FOR_PUBLISHED_REVIT,
                                  file)
    else:
        path = file
        
    # print (path)

    #print "final path = " + path
    try:
        from System.Media import SoundPlayer
        sp = SoundPlayer()
        sp.SoundLocation = path
        sp.Play()
        return
    except Exception as e:
        # print ("Cannot use system media becasue: " + str(e))
        pass

    try:
        import sys
        sys.path.append(ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER)
        import playsound
        playsound.playsound(path)
    except Exception as e:
        # print ("cannot use playsound module becasue: " + str(e))
        pass





def prank_play_sound(file):
    import random
    chance = random.random()
    #print chance
    if chance < 0.1:
        file = "sound effect_mario game over.wav"
        play_sound(file)


def play_meme_sound():
    import random
    folder = '{}\Source Codes\Fun\sound effects\meme'.format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    file = random.choice([x for x in os.listdir(folder) if x.endswith(".wav")])
    file = os.path.join(folder, file)
    play_sound(file)

def unit_test():
    print ("Playing stupid sound effect")
    # play_sound("sound effect_mario powerup.wav")
    play_meme_sound()
    

#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")
    # unit_test() 
    file = 'sound effect_xmas_hohoho.wav'
    file = 'sound effect_xmas_hohoho.mp3'
    play_sound(file)
    