__title__ = "ViewToggle"

KEY = "F4"

__doc__ = """Toggles between Top and Perspective views.
Left click to switch between views.
Useful for quick view navigation during modeling.

Also assign a keyboard shortcut: {}""".format(KEY)


from EnneadTab import ERROR_HANDLE, LOG
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def view_toggle():

    
    # Toggle between Top and Perspective views
    if rs.IsViewPerspective(rs.CurrentView()):  # Check if current view is Perspective
        rs.CurrentView("Top")
    else:
        rs.CurrentView("Perspective")


    keyboard_setting = Rhino.ApplicationSettings.ShortcutKeySettings
    keyboard_setting.SetMacro(Rhino.ApplicationSettings.ShortcutKey[KEY], "EA_{}".format(__title__))

    
if __name__ == "__main__":
    view_toggle()
