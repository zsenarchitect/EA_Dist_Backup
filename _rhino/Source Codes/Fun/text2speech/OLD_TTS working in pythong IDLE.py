import sys
sys.path.append("..\lib")
import EnneadTab
import playsound
import os

file = "C:\Users\szhang\Documents\EnneadTab Settings\Local Copy Dump\EA_Text2Speech_12.wav"
#file = os.path.dirname(__file__) + 'audio.mp3'
#playsound.playsound(file, False)



"""
package the following function to pygame exe:
translate and speak
read text and remove
gui check only onle speaker exsit, do not run if already has one
mute auido
change Eng or Chinese



this app will keep looking for text to read. Other program can just dump speak text and dont worry about talking.
"""
@EnneadTab.ERROR_HANDLE.try_catch_error
def speak(text):
    import os
    from gtts import gTTS
    import pygame
    import random
    tts=gTTS(text=text, lang='en')
    filename="XXX_{}.mp3".format(random.random())#the save address should be in user desktop for folder access reason
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    os.remove(filename)


if __name__ == "__main__":
    speak("hello sunnyside?")
