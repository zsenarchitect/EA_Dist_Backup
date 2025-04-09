#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import random
import io


import FOLDER
import NOTIFICATION
import SPEAK
import EXE
import TIME
import SOUND
import EMOJI
import CONFIG
import DUCK
import DOCUMENTATION

    
def open_red_alert_online():
    url = "https://game.chronodivide.com/"
    import webbrowser
    webbrowser.open(url)



def is_hate_fun():
    return not CONFIG.get_setting("radio_bt_popup_full", False)

def get_all_jokes():
    with io.open(DOCUMENTATION.get_text_path_by_name('_dad_jokes.txt'), "r", encoding="utf8") as f:
        lines = f.readlines()
    return [x.strip() for x in lines if x.strip()]

def get_all_loading_screen_message():
    with io.open(DOCUMENTATION.get_text_path_by_name('_loading_screen_message.txt'), "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [x.strip() for x in lines if x.strip()]

def random_joke():
    lines = get_all_jokes()
    return random.choice(lines)

def random_loading_message():
    """get some fun message for loading screen
    Returns:
        str: a random line of funny message
    """
    lines = get_all_loading_screen_message()
    return random.choice(lines)


def prank_ph():
    return
    if is_hate_fun():
        return
    
    icon = '{}\prank\pornhub.png'.format(FOLDER.get_folder_path_from_path(__file__))
   
    NOTIFICATION.messenger(sub_text="Please login again at www.pornhub.com",
                        main_text="{} videos failed to download.".format(random.randint(2,6)),
                        app_name="Chrome",
                        icon=icon,
                        force_toast=True)
    
def prank_meme():
    if is_hate_fun():
        return
    link = "https://www.instagram.com/reel/C0KA4-kxioj/?igsh=MWN6cmg4cW5qeXV5NA%3D%3D"
    import webbrowser
    webbrowser.open(link)


def prank_dvd():
    # if is_hate_fun():
    #     return
    EXE.try_open_app("Bouncer.exe")
    
def joke_quote():

    quote = random_loading_message()
    emoji = EMOJI.random_emoji()
    if emoji and len(emoji) > 0:
        quote = "{}\n{}".format(quote, emoji)
    

    import textwrap
    # Wrap this text.
    wrapper = textwrap.TextWrapper(width = 100)
    quote = wrapper.fill(text = quote)


    NOTIFICATION.messenger(main_text = quote, animation_stay_duration = 10)



     
def give_me_a_joke(talk=False, max_len=None):
    joke = random_joke()
    if not max_len:
        import textwrap as TW
        wrapper = TW.TextWrapper(width=70)
        joke = "\n".join(wrapper.wrap(joke))

    if talk:
        SPEAK.speak(joke.replace("\n", " "))
    return joke.replace("\n", " ")


def validating_jokes():
    with io.open("_dad_jokes.txt", "r", encoding="utf-8") as f:

        lines = f.readlines()


    OUT = []
    for line in lines:
        #print "\n#######################"
        #print line
        if r"â€™" in line:
            print (line)
            print ("find a bad string" + "*" * 50)
            line = line.replace(r"â€™", r"\'")
        if r"â??" in line:
            print (line)
            print ("find a bad string" + "*" * 50)
            line = line.replace(r"â??", r"\"")
        if r".â" in line:
            print (line)
            print ("find a bad string" + "*" * 50)
            line = line.replace(r".â", r"\"")
        if line.endswith("?"):
            print ("find a questiong ending:" + "*" * 100)
            print (line)
        OUT.append(line)

    with io.open("dad_jokes.txt", "w", encoding="utf-8") as f:
        f.writelines(OUT)


# Define chance once at module level
PRANK_CHANCE = 0.0000000000001

if random.random() < PRANK_CHANCE:
    prank_ph()

if random.random() < PRANK_CHANCE:
    prank_meme()

if random.random() < PRANK_CHANCE:
    prank_dvd()

if random.random() < PRANK_CHANCE:
    DUCK.quack()

def april_fool():

    y, m, d = TIME.get_date_as_tuple(return_string=False)

    marker_file = FOLDER.get_local_dump_folder_file("{}_april_fooled3.stupid".format(y))
    
    if m == 4 and d in [1] and random.random() < 0.02 :


        if os.path.exists(marker_file):
            return
        dice = random.random()
        if dice < 0.2:
            prank_ph()
        # elif dice < 0.45:
        #     NOTIFICATION.duck_pop(random_joke())
        # elif dice < 0.48:
        #     NOTIFICATION.messenger(random_loading_message())
        elif dice < 0.95:
            max = 10
            for _ in range(random.randint(3, max)):
                prank_dvd()

        else:
            SOUND.play_meme_sound()
        with io.open(marker_file, 'w', encoding="utf-8") as f:
            f.write("You have been pranked.")


        # FUN.EnneaDuck.quack()

def ennead_duck():
    EXE.try_open_app("Pet.exe")

april_fool()

if __name__ == "__main__":


 
    # joke_quote()
    for x in get_all_loading_screen_message():
        print (x)

