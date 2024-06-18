#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
sys.path.append("..\lib")
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


from google_trans_new import google_translator  
  


def translate_main():
    translator = google_translator()  
    translate_text = translator.translate('Hola mundo!', lang_src='es', lang_tgt='en')  
    print(translate_text)
    return

    
    #translator = Translator(service_urls=['translate.googleapis.com'])
    translator = Translator()
    res = translator.translate("Der Himmel ist blau und ich mag Bananen", dest='en')
    print(res.text)
    
    translations = translator.translate(['The quick brown fox', 'jumps over', 'the lazy dog'], dest='ko')
    for translation in translations:
        print(translation.origin, ' -> ', translation.text)


    translator = Translator()
    texts = ["Hello World", "N3 East elevation"]

    
    
    
    for text in texts:
        print(text)
        result = translator.translate(text, dest='zh-cn')

        print(result.origin)
        print(result.text)


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
