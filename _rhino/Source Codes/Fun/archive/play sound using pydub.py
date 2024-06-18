import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
from pydub import AudioSegment
from pydub.playback import play
  
@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    # for playing wav file
    folder = 'L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\Fun\sound effects'
    file = "sound effect_mario game over.wav"
    path = folder + "\\" + file
    song = AudioSegment.from_wav(path)
    print('playing sound using  pydub')
    play(song)
    
    
#########################
if __name__ == "__main__":
    main()