from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException

from pyrevit.forms import WPFWindow
# from pyrevit import forms #



# from Autodesk.Revit import UI # pyright: ignore

import traceback
from pyrevit import forms, script
from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
import os.path as op
import EA_UTILITY
import EnneadTab
import time
from pyrevit.coreutils import envvars

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Template\nModeless Form"
__persistentengine__ = True

def try_catch_error(func):

    def wrapper(*args, **kwargs):

        EA_UTILITY.print_note ("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
            EA_UTILITY.print_note ( "Wrapper func for EA Log -- Finish:")
            return out
        except Exception as e:
            EA_UTILITY.print_note ( str(e))
            EA_UTILITY.print_note (  "Wrapper func for EA Log -- Error: " + str(e)  )
            error = traceback.format_exc()
            error_file = "{}\error_log.txt".format(EA_UTILITY.get_user_folder())
            with open(error_file, "w") as f:
                f.write(error)
            EA_UTILITY.open_file_in_default_application(error_file)
    return wrapper



def sample_func_1(count):
    print("##sample func 1 begin")
    for i in range(count):
        print(i)
    print("## sample func 1 end")


def sample_func_2(count):
    print("##sample func 2 begin")
    for i in range(count):
        print(i * i)
    print("## sample func 2 end")




# A simple WPF form used to call the ExternalEvent
class SampleDockable(forms.WPFPanel):
    panel_title = "Sample DockPane"
    panel_id = "3110e336-f81c-4927-87da-4e0d30d4d641"
    panel_source = op.join(op.dirname(__file__), "Sample_Dockable.xaml")
    #self.update_UI()

    def update_UI(self):
        self.note.Text = "Curently pointing to doc: {}".format("some doc")
        self.funcs = [sample_func_1, sample_func_2]
        #self.funcs = [sample_func_1]
        #self.ext_events = [register_event(x) for x in self.funcs]
        self.Title = "Sample Dockpane."
        self.Width = 300

    @try_catch_error
    def primary_button_Clicked(self, sender, e):
        self.update_UI()
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        print("primary button clicked")
        sample_func_1(50)

    def generic_click(self, func_name, keyword):
        #print "Clicking " + keyword
        self.simple_event_handler.kwargs = keyword
        for ext_event in self.ext_events:
            if ext_event.func_name == func_name:
                ext_event.Raise()
                break
        res = self.simple_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"
        return res






def register_sample_dockpane():
    if not forms.is_registered_dockable_panel(SampleDockable):
        forms.register_dockable_panel(SampleDockable, default_visible = EA_UTILITY.is_SZ())
        if EA_UTILITY.is_SZ():
            EA_UTILITY.show_toast(message = "Open it in dim text",title = "Sample Dock regiesterd")
    else:
        EA_UTILITY.print_note( "Skipped registering dockable pane. Already exists.")
