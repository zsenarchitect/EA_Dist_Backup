


import time
import pygame
import button

import os
import math

from gtts import gTTS
import random
import pyautogui
import math
import sys
sys.path.append(r'L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension\lib')
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')
from EnneadTab import DATA_FILE, FOLDER, ERROR_HANDLE

def try_catch_error(func):
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out
        except Exception as e:
            print (e)
    return wrapper

class TTS:

    def __init__(self):
        pass


    @try_catch_error
    def speak(self, text, lang = 'en', accent = 'com'):

        tts = gTTS(text = text, lang = lang, tld = accent)
        filename = "{}\TTS_{}.mp3".format(FOLDER.get_EA_local_dump_folder(), random.random())#the save address should be in user desktop for folder access reason
        tts.save(filename)

        """
        #method 1
        from System.Media import SoundPlayer
        sp = SoundPlayer()
        sp.SoundLocation = filename
        sp.Play()
        """


        #method2
        pygame.mixer.init()
        pygame.mixer.music.set_volume(float(self.volume) / 100)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():

            pygame.time.Clock().tick(10)

        pygame.mixer.quit()

        os.remove(filename)

        return True

    def read_from_file(self):

        file_name = "EA_Text2Speech.json"
        dump_folder = FOLDER.get_EA_local_dump_folder()
        file_path = "{}\{}".format(dump_folder, file_name)


        if not FOLDER.is_file_exist_in_folder(file_name, dump_folder):
            return False

        #dont speak for file too old
        if time.time() - os.path.getctime( file_path) > 60 or time.time() - os.path.getmtime( file_path) > 60:
            print ("old file")
            now =  time.time()
            print (now)
            print (now - os.path.getctime( file_path))
            print( now - os.path.getmtime( file_path))
            FOLDER.remove_exisitng_file_in_folder(dump_folder, file_name)
            return False



        try:
            data = DATA_FILE.read_json_as_dict(file_path)
        except:
            return False
        if not data:
            return False
        text = data["text"]
        language = data["language"]
        accent = data["accent"]

        res = self.speak(text, language, accent)
        if res:
            print("speak finish")

            FOLDER.remove_exisitng_file_in_folder(dump_folder, file_name)
            return True
        
        return False


    def rotate_img_around_center(self, image, rect, angle):
        """Rotate the image while keeping its center."""
        # Rotate the original image without modifying it.
        new_image = pygame.transform.rotate(image, angle)
        # Get a new rect with the center of the old rect.
        rect = new_image.get_rect(center=rect.center)
        return new_image, rect


    def get_pointer_angle(self, pt_x, pt_y):
        """get the angle of a line[current mouse position to a given pt] to X axis"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x == pt_x:
          return 90 + 180 * (mouse_y > pt_y)
        angle = math.atan(-float(mouse_y - pt_y) / float(mouse_x - pt_x))* 180 / math.pi
        angle += 180 * (mouse_x < pt_x)# force extra rotate
        return angle

    def is_another_TTS_running(self):

        #print [x.title for x in pyautogui.getAllWindows()]
        for window in pyautogui.getAllWindows():
            #print window.title
            if window.title == u"EnneadTab Talkie":
                return True
        return False

    def is_lady_killed(self):
        return not DATA_FILE.get_revit_ui_setting_data(("toggle_bt_is_talkie", True))
        """
        file_name = 'revit_ui_setting.json'
        if not FOLDER.is_file_exist_in_dump_folder(file_name):
            return False


        setting_file = FOLDER.get_EA_dump_folder_file(file_name)
        data = DATA_FILE.read_json_as_dict(setting_file)
        return not data.get("toggle_bt_is_talkie", True)
        """

    """
        dump_folder = FOLDER.get_EA_local_dump_folder()
        file_name = "EA_TALKIE_KILL.kill"
        if FOLDER.is_file_exist_in_folder(file_name, dump_folder):
            print("Lets the murder begin...")
            return True
        return False
    """

    def mark_kill_file(self):
        DATA_FILE.set_revit_ui_setting_data("toggle_bt_is_talkie", False)
        """
        file_name = 'revit_ui_setting.json'
        if not FOLDER.is_file_exist_in_dump_folder(file_name):
            return 


        setting_file = FOLDER.get_EA_dump_folder_file(file_name)
        data = DATA_FILE.read_json_as_dict(setting_file)
        data["toggle_bt_is_talkie"] = False
        DATA_FILE.save_dict_to_json(data, setting_file)
        """

        """
        dump_folder = FOLDER.get_EA_local_dump_folder()
        file_name = "EA_TALKIE_KILL.kill"
        filepath = "{}\{}".format(dump_folder, file_name)

        with open(filepath, 'w') as f:
            f.write("Kill!")
        """


    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    @ERROR_HANDLE.try_catch_error_silently
    def main(self):
        if self.is_another_TTS_running():
            #speak("there is another 'EnneadTab Talkie' opened. Now quiting")
            print("other TTS running")
            return



        #script_dir = os.path.abspath( os.path.dirname( __file__ ) )
        #print "A GUI designed by Sen Zhang for Ennead Architect."
        # print ("%%%%%%%%%%%%%%%%%%%%%")
        # print (script_dir)
        pygame.init()


        #create game window
        SCREEN_WIDTH = 800
        SCREEN_HEIGHT = 600

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.iconify()

        pygame.display.set_caption("EnneadTab Talkie")

        #game variables
        game_paused = False
        menu_state = "main"

        #define fonts
        font_title = pygame.font.SysFont("arialblack", 30)
        font_subtitle = pygame.font.SysFont("arialblack", 20)
        font_body = pygame.font.SysFont("arial", 15)
        font_note = pygame.font.SysFont("arialblack", 10)

        #define colours
        TEXT_COL = (255, 255, 255)
        TEXT_COL_FADE = (150, 150, 150)

        # logo
        content_folder = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published\\ENNEAD.extension\\Ennead.tab\\Utility.panel\\exe_1.stack\\text2speech.pushbutton"
        EA_logo = pygame.image.load("{}\\images\\Ennead_Architects_Logo.png".format(content_folder)).convert_alpha()
        target_img_size = (100, 100)
        EA_logo = pygame.transform.scale(EA_logo, target_img_size)
        original_logo = EA_logo
        logo_rect = EA_logo.get_rect(center=(100, SCREEN_HEIGHT - 100))
        angle = 0

        # Clock
        clock = pygame.time.Clock()
        FPS = 30

        self.volume = 20

        #load button images
        mute_img = pygame.image.load("{}\\images\\button_audio_mute.png".format(content_folder)).convert_alpha()
        unmute_img = pygame.image.load("{}\\images\\button_audio_unmute.png".format(content_folder)).convert_alpha()
        louder_img = pygame.image.load("{}\\images\\button_audio_higher_voice.png".format(content_folder)).convert_alpha()
        quieter_img = pygame.image.load("{}\\images\\button_audio_lower_voice.png".format(content_folder)).convert_alpha()
        quit_img = pygame.image.load("{}\\images\\button_quit.png".format(content_folder)).convert_alpha()
        coffin_img = pygame.image.load("{}\\images\\button_coffin.png".format(content_folder)).convert_alpha()


        #create button instances
        mute_button = button.Button(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, mute_img, 1)
        unmute_button = button.Button(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, unmute_img, 1)
        kill_button = button.Button(60, SCREEN_HEIGHT/2 + 50, coffin_img, 0.2)

        louder_button = button.Button(SCREEN_WIDTH/2, SCREEN_HEIGHT - 200, louder_img, 0.7)
        quiter_button = button.Button(SCREEN_WIDTH/2 + 170, SCREEN_HEIGHT - 200, quieter_img, 0.7)
        quit_button = button.Button(SCREEN_WIDTH/2, SCREEN_HEIGHT - 120, quit_img, 1)




        #game loop
        run = True
        is_mute = False
        life_max = 60 * 60 * FPS# 60mins x FPS
        life_count = life_max
        while run:
            self.screen.fill((52, 78, 91))

            if self.is_lady_killed():
                run = False
                break

            self.draw_text("Click on coffin to never hear her again.", font_note, TEXT_COL, 50, SCREEN_HEIGHT/2 + 100)
            if kill_button.draw(self.screen):
                self.speak("Gentlemen, it has been a privilege playing with you tonight.")
                self.mark_kill_file()
                run = False
                break

            if not is_mute:
                res = self.read_from_file()
                if res:
                    life_count = life_max




            angle = self.get_pointer_angle(*logo_rect.center)# this is to keep it facing mouse
            EA_logo, logo_rect = self.rotate_img_around_center(original_logo, logo_rect, angle)
            self.screen.blit(EA_logo, logo_rect)

            #check if game is paused
            self.draw_text("EnneadTab Talkie. ", font_title, TEXT_COL, 50, 50)
            # self.draw_text("Keep this window alive. ", font_title, TEXT_COL_FADE, 50, 100)
            # self.draw_text("Do not close after every talk.", font_title, TEXT_COL_FADE, 50, 130)
            # self.draw_text("Minimize it is ok though.", font_title, TEXT_COL_FADE, 50, 160)

            # self.draw_text("So other tools keep broadcast messages without initiating talkie", font, TEXT_COL_FADE, 50, 200)
            # self.draw_text("over and over again. Every initiation takes a few seconds, so let's", font, TEXT_COL_FADE, 50, 230)
            # self.draw_text("initiate as few times as possible.", font, TEXT_COL_FADE, 50, 260)




            if is_mute:
                self.draw_text("Currently Muted.", font_subtitle, TEXT_COL, 50, SCREEN_HEIGHT/2)
                if unmute_button.draw(self.screen):
                    is_mute = not is_mute
                    self.speak("Thank God! I can talk again.")
                    life_count = life_max
            else:
                self.draw_text("Currently Talky.", font_subtitle, TEXT_COL, 50, SCREEN_HEIGHT/2)
                if mute_button.draw(self.screen):
                    is_mute = not is_mute
                    self.speak("Ok, I will not talk to you anymore!")

            if louder_button.draw(self.screen):
                self.volume = min(self.volume + 10, 100)
                self.speak("Increasing voice level.")


            if quiter_button.draw(self.screen):
                self.volume = max(self.volume - 10, 0)
                self.speak("Decreasing voice level.")

            self.draw_text("Voice Volume = {}. (Range 0~100)".format(self.volume), font_note, TEXT_COL, SCREEN_WIDTH/2, SCREEN_HEIGHT - 220)




            if quit_button.draw(self.screen):
                run = False

            if life_count < 0:
                run = False
            text_life = int(life_count / FPS)
            text_min = int(math.floor(text_life / 60))
            text_secs = text_life % 60
            self.draw_text("To save memory, EnneadTab Talkie will close itself in {}m {}s if there is nothing to say.".format(text_min, text_secs), font_note, TEXT_COL, 50, SCREEN_HEIGHT - 20)
            life_count -= 1


            #event handler
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_paused = True
                if event.type == pygame.QUIT:
                    run = False

            clock.tick(FPS)
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":

    TTS().main()


