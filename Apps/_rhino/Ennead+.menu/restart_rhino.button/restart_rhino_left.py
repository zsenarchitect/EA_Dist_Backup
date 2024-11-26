
__title__ = "RestartRhino"
__doc__ = "Restart Rhino to test new core."


from EnneadTab import ERROR_HANDLE, LOG
import rhinoscriptsyntax as rs
import os

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def restart_rhino():
    
    os.startfile("C:\\Program Files\\Rhino {}\\System\\Rhino.exe".format(rs.ExeVersion()))
    rs.Exit()


if __name__ == "__main__":
    restart_rhino()
