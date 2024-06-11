
import ENVIRONMENT
import sys

if ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
    sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
    try:
        # cli platform does not support pyautoGUI
        import pyautogui
    except:
        pass


def send_control_D():
    pyautogui.hotkey('ctrl', 'd')