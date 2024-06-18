#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import ENVIRONMENT

def play_sound(file = "sound effect_popup msg3.wav"):
    if not ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return
    #print "in = " + file
    #case 1: come in as wav file only----> add fun folder in front
    #case 2: come in any format of path
    if "\\" not in str(file).lower():
        folder = '{}\Source Codes\Fun\sound effects'.format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
        path = folder + "\\" + file
    else:
        path = file

    #print "final path = " + path
    try:
        from System.Media import SoundPlayer
        sp = SoundPlayer()
        sp.SoundLocation = path
        sp.Play()
        return
    except Exception as e:
        print ("Cannot use system media becasue: " + str(e))

    try:
        import sys
        sys.path.append(r'{}\Dependency Modules'.format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO))
        import playsound
        playsound.playsound(path)
    except Exception as e:
        print ("cannot use playsound module becasue: " + str(e))





def prank_play_sound(file):
    import random
    chance = random.random()
    #print chance
    if chance < 0.1:
        file = "sound effect_mario game over.wav"
        play_sound(file)




#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")