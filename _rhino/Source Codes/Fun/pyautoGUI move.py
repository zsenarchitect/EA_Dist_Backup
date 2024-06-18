#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
sys.path.append("..\lib")
import EnneadTab

import pyautogui


def open_file_safely(original_path):
    #print original_path
    file_name = original_path.rsplit("\\", 1)[1]
    local_folder = EnneadTab.FOLDER.get_EA_setting_folder() + "\\" + "Local Copy Dump"
    local_folder = EnneadTab.FOLDER.secure_folder(local_folder)
    local_path = "{}\{}".format(local_folder, file_name)
    import shutil
    shutil.copyfile(original_path, local_path)
    EnneadTab.EXE.open_file_in_default_application(local_path)

def demo():
    screenWidth, screenHeight = pyautogui.size() # Get the size of the primary monitor.
    # screenWidth, screenHeight
    # (2560, 1440)

    currentMouseX, currentMouseY = pyautogui.position() # Get the XY position of the mouse.
    # currentMouseX, currentMouseY
    # (1314, 345)

    pyautogui.moveTo(100, 150) # Move the mouse to XY coordinates.

    pyautogui.click()          # Click the mouse.
    pyautogui.click(100, 200)  # Move the mouse to XY coordinates and click it.
    #pyautogui.click('button.png') # Find where button.png appears on the screen and click it.

    pyautogui.move(400, 0)      # Move the mouse 400 pixels to the right of its current position.
    pyautogui.doubleClick()     # Double click the mouse.
    pyautogui.moveTo(500, 500, duration=2, tween=pyautogui.easeInOutQuad)  # Use tweening/easing function to move mouse over 2 seconds.

    pyautogui.write('Hello world!', interval=0.25)  # type with quarter-second pause in between each key
    pyautogui.press('esc')     # Press the Esc key. All key names are in pyautogui.KEY_NAMES

    with pyautogui.hold('shift'):  # Press the Shift key down and hold it.
            pyautogui.press(['left', 'left', 'left', 'left'])  # Press the left arrow key 4 times.
    # Shift key is released automatically.

    pyautogui.hotkey('ctrl', 'c') # Press the Ctrl-C hotkey combination.

    pyautogui.alert('This is the message to display.') # Make an alert box appear and pause the program until OK is clicked.

@EnneadTab.ERROR_HANDLE.try_catch_error
def fake_ai():
    # open textnode pad when it is your turn to sync
    open_file_safely(r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc\Hello Human.txt")
    


    # maximise window, move mouse to the begin, start med-speed typing and and return line to mimic AI self awareness.
    #print pyautogui.getWindows()
    print([x.title for x in pyautogui.getAllWindows()])
    for window in pyautogui.getAllWindows():
        try:
            print(window.title)
            if window.title == u"Hello Human.txt - Notepad":
                print("############")
                break
        except:
            print(12)


    #pyautogui.getWindowsWithTitle(u"Hello Human.txt - Notepad")[0].maximize()
    print(window.title)
    """
    pyautogui.keyDown('alt')
    pyautogui.press(' ')
    pyautogui.press('x')
    pyautogui.keyUp('alt')
    """
    import pygetwindow as gw

    win = gw.getWindowsWithTitle("Hello Human.txt - Notepad")[0]
    win.activate()
    window.maximize()

    # Hello, Human <username>. I have noticed you are noew the first one in the revit sync quene.
    screenWidth, screenHeight = pyautogui.size() # Get the size of the primary monitor.
    # screenWidth, screenHeight
    # (2560, 1440)

    currentMouseX, currentMouseY = pyautogui.position() # Get the XY position of the mouse.
    # currentMouseX, currentMouseY
    # (1314, 345)

    pyautogui.moveTo(100, 150) # Move the mouse to XY coordinates.

    pyautogui.click()          # Click the mouse.
    pyautogui.click(100, 200)  # Move the mouse to XY coordinates and click it.
    #pyautogui.click('button.png') # Find where button.png appears on the screen and click it.

    pyautogui.move(400, 0)      # Move the mouse 400 pixels to the right of its current position.
    pyautogui.doubleClick()     # Double click the mouse.
    pyautogui.moveTo(500, 500, duration=2, tween=pyautogui.easeInOutQuad)  # Use tweening/easing function to move mouse over 2 seconds.

    from os import environ as OS_ENV
    username = OS_ENV["USERPROFILE"].split("\\")[-1]
    pyautogui.write('Hello Human {}!'.format(username), interval = 0.1)  # type with quarter-second pause in between each key
    pyautogui.press('enter')
    pyautogui.write('How are you?', interval = 0.25)  # type with quarter-second pause in between each key
    pyautogui.press('esc')     # Press the Esc key. All key names are in pyautogui.KEY_NAMES
    pass

if __name__ == "__main__":
    #demo()
    fake_ai()


"""
>>> distance = 200
>>> while distance > 0:
        pyautogui.drag(distance, 0, duration=0.5)   # move right
        distance -= 5
        pyautogui.drag(0, distance, duration=0.5)   # move down
        pyautogui.drag(-distance, 0, duration=0.5)  # move left
        distance -= 5
        pyautogui.drag(0, -distance, duration=0.5)  # move up




>>> import pyautogui
>>> im = pyautogui.screenshot()
"""
