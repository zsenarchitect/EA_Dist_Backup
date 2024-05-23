# import sys
# sys.path.append("..\lib")
# import EnneadTab
from pydub import AudioSegment
import os
import soundfile as sf
import numpy as np
import os

"""run this in dell laptop
"""
# @EnneadTab.ERROR_HANDLE.try_catch_error
def convert_unit_talk():
    # Set directory paths
    input_folder = "C:\\Users\\sen.zhang\\github\\EnneadTab-for-Rhino\\Source Codes\\Fun\\sound effects\\red alert"
    output_folder = input_folder

    # Loop through all files in input directory
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp3"):
            mp3_path = os.path.join(input_folder, filename)
            wav_path = os.path.join(output_folder, filename.replace(".mp3", ".wav"))
            print ("##################################")
            print (mp3_path)
            
            # Read MP3 file
            data, samplerate = sf.read(mp3_path)

            # Write to WAV
            sf.write(wav_path, data, samplerate)
            
            continue
            # Load MP3 and export as WAV
            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")

    print("Conversion done!")



# @EnneadTab.ERROR_HANDLE.try_catch_error
def convert_announcer_talk():
    # Set directory paths
    input_folder = "C:\\Users\\sen.zhang\\github\\EnneadTab-for-Rhino\\Source Codes\\Fun\\sound effects\\red alert\\Announcer Speech"
    output_folder = input_folder

    # Loop through all files in input directory
    for filename in os.listdir(input_folder):
        if filename.endswith(".wav"):
            mp3_path = os.path.join(input_folder, filename)
            wav_path = os.path.join(output_folder, filename.replace(".wav", ".wav"))
            print ("##################################")
            print (mp3_path)
            
            # Read MP3 file
            data, samplerate = sf.read(mp3_path)

            # Write to WAV
            sf.write(wav_path, data, samplerate)
            
            continue
            # Load MP3 and export as WAV
            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")

    print("Conversion done!")

# @EnneadTab.ERROR_HANDLE.try_catch_error
def convert_mp3_to_wav(input_folder):
    # Set directory paths
    output_folder = input_folder

    # Loop through all files in input directory
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp3"):
            mp3_path = os.path.join(input_folder, filename)
            wav_path = os.path.join(output_folder, filename.replace(".mp3", ".wav"))
            print ("##################################")
            print (mp3_path)
            
            # Read MP3 file
            data, samplerate = sf.read(mp3_path)

            # Write to WAV
            sf.write(wav_path, data, samplerate)
            
            continue
            # Load MP3 and export as WAV
            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")

    print("Conversion done!")



if __name__ == "__main__":
    #convert_announcer_talk()
    # convert_unit_talk()
    convert_mp3_to_wav(r"C:\Users\sen.zhang\Downloads\temp")