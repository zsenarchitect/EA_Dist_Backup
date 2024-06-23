
#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import threading
import ENVIRONMENT
import ENVIRONMENT_CONSTANTS
import USER

def get_aduio_path_by_name(file_name):
    if os.path.exists("{}\\{}".format(ENVIRONMENT_CONSTANTS.AUDIO_FOLDER, file_name)):
        return "{}\\{}".format(ENVIRONMENT_CONSTANTS.AUDIO_FOLDER, file_name)
    #print ("A ha! {}\\{} is not valid or accessibile. Better luck next time.".format(ENVIRONMENT_CONSTANTS.AUDIO_FOLDER, file_name))


def get_aduio_path_by_name(file_name):
    if os.path.exists("{}\\{}".format(ENVIRONMENT_CONSTANTS.AUDIO_FOLDER, file_name)):
        return "{}\\{}".format(ENVIRONMENT_CONSTANTS.AUDIO_FOLDER, file_name)
    print ("A ha! {}\\{} is not valid or accessibile. Better luck next time.".format(ENVIRONMENT_CONSTANTS.AUDIO_FOLDER, file_name))


def play_sound(file = "sound effect_popup msg3.wav"):
    

    #print "in = " + file
    #case 1: come in as wav file only----> add fun folder in front
    #case 2: come in any format of path
    if not os.path.exists(file):
        # print (get_aduio_path_by_name(file))
        if get_aduio_path_by_name(file):
            path = get_aduio_path_by_name(file)
        else:  
            # if USER.is_SZ():
            #     print ("SZ only: cannot find {} in default method".format(file))     
            folder = '{}\\Source Codes\\Fun\\sound effects'.format(ENVIRONMENT_CONSTANTS.PUBLISH_FOLDER_FOR_RHINO)
            path = folder + "\\" + file
            if not os.path.exists(path):
                path = "{}\\{}".format(ENVIRONMENT_CONSTANTS.CORE_AUDIOS_FOLDER_FOR_PUBLISHED_REVIT,
                                        file)
    else:
        path = file
        
    # if USER.is_SZ():    
    #     print (path)

    #print "final path = " + path
    try:
        from System.Media import SoundPlayer # pyright : ignore
        sp = SoundPlayer()
        sp.SoundLocation = path
        sp.Play()
        return
    except Exception as e:
        if USER.is_SZ():
            print ("Cannot use system media becasue: " + str(e))
        

    try:
        import sys
        sys.path.append(ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER_LEGACY)
        import playsound # pyright : ignore
        playsound.playsound(path)
    except Exception as e:
        if USER.is_SZ():
            print ("cannot use playsound module becasue: " + str(e))
        





def prank_play_sound():
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
    
class Player:
    """
    the music file start to play, and a FlagListener will start running, when 
    detecting a stop flag snet by any program, it stops.

    Can be usewd to play 'elevator music' continously but not infiniately during long process
    such as doc syncing dyc opening

    I think this Listerner will use threading to keep it running without blocking main program

    player = Player(file)
    player.start()
    # do other stuff
    player.stop()

    
    """

    def play(self):
        while not self.stop_flag.is_set():
            print("Playing elevator music...")
            play_sound(self.file)

            
    def start(self, file):
        self.file = file


        # Create a flag to control the music playback
        self.stop_flag = threading.Event()

        # Create a thread to play music
        self.music_thread = threading.Thread(target=self.play)

        # Start the music thread
        self.music_thread.start()

    def stop(self):

        # Set the stop flag to terminate the music thread
        self.stop_flag.set()

        # Wait for the music thread to finish
        self.music_thread.join()

        print("Music stopped.")
        pass

#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")
    # unit_test() 
    file = 'sound effect_xmas_hohoho.wav'
    # file = 'sound effect_xmas_hohoho.mp3'
    play_sound(file)
    