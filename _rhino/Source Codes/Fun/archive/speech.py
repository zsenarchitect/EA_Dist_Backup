
import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


@EnneadTab.ERROR_HANDLE.try_catch_error
def method1():
    
    
    from gtts import gTTS
      
    # This module is imported so that we can 
    # play the converted audio
    import os
      
    # The text that you want to convert to audio
    mytext = 'Revit has finished syncing document Bilibili HQ_N3. What do you want to do next?'
      
    # Language in which you want to convert
    language = 'en'
      
    # Passing the text and language to the engine, 
    # here we have marked slow=False. Which tells 
    # the module that the converted audio should 
    # have a high speed
    myobj = gTTS(text=mytext, lang=language, slow=False)
      
    # Saving the converted audio in a mp3 file named
    # welcome
    myobj.save('sample.mp3')
    myobj.save('C:\Users\szhang\Documents\EnneadTab Settings\sample.wav')
  
def method2():
    
   
    import pyttsx
    engine = pyttsx.init()
    engine.say('Sally sells seashells by the seashore.')
    engine.say('The quick brown fox jumped over the lazy dog.')
    engine.runAndWait()

if __name__== "__main__":
    method1()
