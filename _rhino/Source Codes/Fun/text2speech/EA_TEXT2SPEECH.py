


import time
import pygame
import button
import traceback
import os
import math
import playsound
from gtts import gTTS
import random
import pyautogui
import math
import sys
sys.path.append("..\lib")
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)






def speak(text, lang = 'en', accent = 'com'):

    tts = gTTS(text = text, lang = lang, tld = accent)
    filename = "{}\TTS_{}.mp3".format(EnneadTab.FOLDER.get_EA_local_dump_folder(), random.random())#the save address should be in user desktop for folder access reason
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
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():

        pygame.time.Clock().tick(10)

    pygame.mixer.quit()

    os.remove(filename)

def read_from_file():

    file_name = "EA_Text2Speech.json"
    dump_folder = EnneadTab.FOLDER.get_EA_local_dump_folder()
    file_path = "{}\{}".format(dump_folder, file_name)


    if not EnneadTab.FOLDER.is_file_exist_in_folder(file_name, dump_folder):
        return False

    #dont speak for file too old
    if time.time() - os.path.getctime( file_path) > 60 or time.time() - os.path.getmtime( file_path) > 60:
        EnneadTab.FOLDER.remove_exisitng_file_in_folder(dump_folder, file_name)
        return False



    try:
        data = EnneadTab.DATA_FILE.read_json_as_dict(file_path)
    except:
        return False
    text = data["text"]
    language = data["language"]
    accent = data["accent"]

    speak(text, language, accent)

    EnneadTab.FOLDER.remove_exisitng_file_in_folder(dump_folder, file_name)
    return True


def rotate_img_around_center(image, rect, angle):
    """Rotate the image while keeping its center."""
    # Rotate the original image without modifying it.
    new_image = pygame.transform.rotate(image, angle)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect


def get_pointer_angle(pt_x, pt_y):
    """get the angle of a line[current mouse position to a given pt] to X axis"""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_x == pt_x:
      return 90 + 180 * (mouse_y > pt_y)
    angle = math.atan(-float(mouse_y - pt_y) / float(mouse_x - pt_x))* 180 / math.pi
    angle += 180 * (mouse_x < pt_x)# force extra rotate
    return angle

def is_another_TTS_running():

    #print [x.title for x in pyautogui.getAllWindows()]
    for window in pyautogui.getAllWindows():
        #print window.title
        if window.title == u"EnneadTab Talkie":
            return True
    return False

def main():
    if is_another_TTS_running():
        #speak("there is another 'EnneadTab Talkie' opened. Now quiting")
        return



    #script_dir = os.path.abspath( os.path.dirname( __file__ ) )
    #print "A GUI designed by Sen Zhang for Ennead Architect."
    # print ("%%%%%%%%%%%%%%%%%%%%%")
    # print (script_dir)
    pygame.init()


    #create game window
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.iconify()

    pygame.display.set_caption("EnneadTab Talkie")

    #game variables
    game_paused = False
    menu_state = "main"

    #define fonts
    font = pygame.font.SysFont("arialblack", 20)
    font_title = pygame.font.SysFont("arialblack", 30)
    font_note = pygame.font.SysFont("arialblack", 10)

    #define colours
    TEXT_COL = (255, 255, 255)

    # logo
    exe_folder = r"L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\lib\EA_TEXT2SPEECH"
    EA_logo = pygame.image.load("{}\images\\Ennead_Architects_Logo.png".format(exe_folder)).convert_alpha()
    target_img_size = (100, 100)
    EA_logo = pygame.transform.scale(EA_logo, target_img_size)
    original_logo = EA_logo
    logo_rect = EA_logo.get_rect(center=(100, SCREEN_HEIGHT - 100))
    angle = 0

    # Clock
    clock = pygame.time.Clock()
    FPS = 30

    #load button images
    mute_img = pygame.image.load("{}\images\\button_audio_mute.png".format(exe_folder)).convert_alpha()
    unmute_img = pygame.image.load("{}\images\\button_audio_unmute.png".format(exe_folder)).convert_alpha()
    quit_img = pygame.image.load("{}\images\\button_quit.png".format(exe_folder)).convert_alpha()

    #create button instances
    mute_button = button.Button(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, mute_img, 1)
    unmute_button = button.Button(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, unmute_img, 1)
    quit_button = button.Button(SCREEN_WIDTH/2, SCREEN_HEIGHT - 200, quit_img, 1)

    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    #game loop
    run = True
    is_mute = False
    life_max = 60 * 60 * FPS# 60mins x FPS
    life_count = life_max
    while run:

        if not is_mute:
            res = read_from_file()
            if res:
                life_count = life_max


        screen.fill((52, 78, 91))


        angle = get_pointer_angle(*logo_rect.center)# this is to keep it facing mouse
        EA_logo, logo_rect = rotate_img_around_center(original_logo, logo_rect, angle)
        screen.blit(EA_logo, logo_rect)

        #check if game is paused
        draw_text("EnneadTab Text2Speech. ", font, TEXT_COL, 50, 50)
        draw_text("Keep this window alive. ", font_title, TEXT_COL, 50, 100)
        draw_text("Do not close after every talk.", font_title, TEXT_COL, 50, 130)
        draw_text("So other tools keep broadcast messages without initiating talkie", font, TEXT_COL, 50, 180)
        draw_text("over and over again. Every initiation takes a few seconds, so let's", font, TEXT_COL, 50, 210)
        draw_text("initiate as few times as possible.", font, TEXT_COL, 50, 240)




        if is_mute:
            draw_text("Currently Muted.", font_title, TEXT_COL, 50, SCREEN_HEIGHT/2)
            if unmute_button.draw(screen):
                is_mute = not is_mute
                speak("Thank God! I can talk again.")
                life_count = life_max
        else:
            draw_text("Currently Talky.", font_title, TEXT_COL, 50, SCREEN_HEIGHT/2)
            if mute_button.draw(screen):
                is_mute = not is_mute
                speak("Ok, I will not talk to you anymore!")


        if quit_button.draw(screen):
            run = False

        if life_count < 0:
            run = False
        text_life = int(life_count / FPS)
        text_min = int(math.floor(text_life / 60))
        text_secs = text_life % 60
        draw_text("To save memory, EnneadTab Talkie will close itself in {}m {}s if there is nothing to say.".format(text_min, text_secs), font_note, TEXT_COL, 50, SCREEN_HEIGHT - 20)
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
    try:

        main()

    except:
        error = traceback.format_exc()
        error_file = "{}\error_log.txt".format(EnneadTab.FOLDER.get_user_folder())
        with open(error_file, "w") as f:
            f.write(error)
        EnneadTab.EXE.open_file_in_default_application(error_file)
