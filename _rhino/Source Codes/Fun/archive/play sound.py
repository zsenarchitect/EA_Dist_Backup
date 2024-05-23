import sys
sys.path.append("..\lib")
import EnneadTab


@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    path = 'L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\Fun\Temp.wav'
    print(path)
    path = 'abc.wav'
    EnneadTab.SOUNDS.play_sound(path)
    
    
###############################
if __name__ == "__main__":
    main()