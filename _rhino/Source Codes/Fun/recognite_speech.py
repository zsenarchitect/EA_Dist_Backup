import sys
sys.path.append("..\lib")
import EnneadTab
###########################

"""this is supposed to run in python 3.11. In NYC workstation

Returns:
    _type_: _description_
"""

###########################
import os

import speech_recognition as sr

from pydub import AudioSegment

 

def transcribe_wav_files(folder_path):

    results = {}

    recognizer = sr.Recognizer()

    

    for file_name in os.listdir(folder_path):

        if file_name.endswith('.wav'):

            file_path = os.path.join(folder_path, file_name)

            

            with sr.AudioFile(file_path) as source:

                audio_data = recognizer.record(source)

                text = recognizer.recognize_google(audio_data)

            

            results[file_name] = text

    

    return results

@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    folder_path = "C:\\Users\\szhang\\github\\EnneadTab-for-Rhino\\Source Codes\\Fun\\sound effects\\red alert\\Announcer Speech"

    transcriptions = transcribe_wav_files(folder_path)

    print(transcriptions)
    
#################

if __name__ == '__main__':  
    main()