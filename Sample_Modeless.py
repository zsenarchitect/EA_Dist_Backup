from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException

from pyrevit.forms import WPFWindow
# from pyrevit import forms #



# from Autodesk.Revit import UI

import traceback
from pyrevit import forms, script
from Autodesk.Revit import DB
from Autodesk.Revit import UI
import os.path as op
import EA_UTILITY
import EnneadTab
import time
from pyrevit.coreutils import envvars
"""
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
"""

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Template\nModeless Form"
__persistentengine__ = True


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

# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """


    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.func_name = do_this.__name__
        self.kwargs = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                self.OUT = self.do_this(self.kwargs)
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"




# A simple WPF form used to call the ExternalEvent
class SampleDockable(forms.WPFPanel):


    def __init__(self):
        xaml_file_name = "Sample_Dockable.xaml"
        WPFWindow.__init__(self, xaml_file_name)
        self.note.Text = "Curently pointing to doc: {}".format("some doc")
        self.funcs = [sample_func_1, sample_func_2]
        self.ext_events = [register_event(x) for x in self.funcs]
        self.Title = "Sample Modeless."
        self.Width = 600


        self.Show()

    """
        if function is None:
            self.primary_button.Visibility = self.hidden_obj.Visibility
        self.func = function
    """







    def primary_button_Clicked(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        print("primary button clicked")
        kwargs = "to be replaced by any thing"
        func_name = "sample_func_1"
        self.generic_click(func_name, kwargs)

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




def register_event(func):
    print("registering new func")
    # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
    # different functions using different handler class instances
    simple_event_handler = SimpleEventHandler(func)
    #simple_event_handler = SimpleEventHandler(sample_func)

    # We now need to create the ExternalEvent
    ext_event = ExternalEvent.Create(simple_event_handler)
    #ext_event.Raise()
    print("registering finished")
    return ext_event
