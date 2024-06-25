#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


import goslate



def translate_main():
    gs = goslate.Goslate()
    translatedText = gs.translate("a big apple",'zh')
    print translatedText

    #print "N3 East 立面图"
    texts = ["Hello World", "N3 East elevation", "N3 East 立面图", "Enlarged CW-1 plan detail"]

    
    for text in texts:
        gs = goslate.Goslate()
        translatedText = gs.translate(text,'zh')

        print translatedText


if __name__ == "__main__":
    #demo()
    translate_main()


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
