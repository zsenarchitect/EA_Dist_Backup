__title__ = "TimeTravel"
__doc__ = """Selective undo tool for Rhino objects.

Features:
- Undo history for selected objects only
- Maintains other objects' current state
- Precise history control for specific elements"""
import rhinoscriptsyntax as rs
from EnneadTab import NOTIFICATION
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def time_travel():
    if len(rs.SelectedObjects()) == 0:
        NOTIFICATION.messenger(sub_text = "Time travel begin!",
                                    main_text = "Select objects to go back in time.")
    rs.Command("_UndoSelected")




if __name__ == "__main__":
    time_travel()