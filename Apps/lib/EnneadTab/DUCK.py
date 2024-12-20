"""the dancing call duck"""
import EXE
import USER


def quack ():
    if not USER.IS_DEVELOPER:
        return
    EXE.try_open_app("EnneaDuck.exe")