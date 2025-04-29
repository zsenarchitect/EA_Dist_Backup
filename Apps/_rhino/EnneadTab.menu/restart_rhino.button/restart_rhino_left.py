__title__ = "RestartRhino"
__doc__ = """Restart Rhino to apply core updates.

Key Features:
- Safe application restart
- Update implementation
- Session state preservation
- Automatic core reloading
- System verification"""


from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
import rhinoscriptsyntax as rs
import os

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def restart_rhino():
    rhino_exe = "C:\\Program Files\\Rhino {}\\System\\Rhino.exe".format(rs.ExeVersion())
    if os.path.exists(rhino_exe):
        os.startfile(rhino_exe)
        rs.Exit()
    else:
        NOTIFICATION.messenger("Rhino executable not found at: {}".format(rhino_exe))


if __name__ == "__main__":
    restart_rhino()
