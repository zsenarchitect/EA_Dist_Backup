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
from pyrevit import HOST_APP, framework
from pyrevit import routes

__persistentengine__ = True
PANEL_ID = "3510e336-f43c-4927-89aa-4e0d30d4d641"


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
    return "success"


def sample_func_2(count):
    print("##sample func 2 begin")
    for i in range(count):
        print(i * i)
    print("## sample func 2 end")



def old_attach_dock_to_event(cls):

    from System import EventHandler, Uri
    #from Autodesk.Revit.UI.Events import ViewActivatedEventArgs

    def event_handler_function(sender, args):
        EA_UTILITY.print_note( "inside the handler function: begin")
        try:

            cls.dock_doc = args.Document
            #self.note.Text = "Curently pointing to doc: {}".format(self.doc)

        except Exception as e:

            EA_UTILITY.print_note("ERROR: " + str(e))
            EA_UTILITY.print_note(traceback.format_exc())


        EA_UTILITY.print_note("inside the handler function: finish")


    #app = EA_UTILITY.get_application()
    print(UI.UIApplication)
    print(UI.UIApplication.ViewActivated)
    print(EventHandler)
    print(UI.Events.ViewActivatedEventArgs)
    try:
        UI.UIApplication.ViewActivated  += EventHandler[UI.Events.ViewActivatedEventArgs](event_handler_function)
        EA_UTILITY.speak("dock attached")
    except:
        EA_UTILITY.print_note(traceback.format_exc())
        error = traceback.format_exc()
        error_file = "{}\error_log.txt".format(EA_UTILITY.get_user_folder())
        with open(error_file, "w") as f:
            f.write(error)
        EA_UTILITY.open_file_in_default_application(error_file)

# A simple WPF form used to call the ExternalEvent
class RhinoDockable(forms.WPFPanel):
    panel_title = "EnneadTab Rhino DockPane"
    panel_id = PANEL_ID
    panel_source = op.join(op.dirname(__file__), "Rhino_Dockable.xaml")
    dock_doc = 123
    #
    # @property
    # def dock_doc(self):
    #     return HOST_APP.doc

    """
    from System import EventHandler, Uri
    def event_handler_function(sender, args):
        dock_doc = args.Document
    UI.UIApplication.ViewActivated  += EventHandler[UI.Events.ViewActivatedEventArgs](event_handler_function)
    """

    #self.update_UI()








    def odl_update_UI(self):

        """
        print(UI)
        print(UI.UIDocument)
        print("%%%%%%%%%")
        import pyrevit
        host_app = pyrevit._HostApplication
        print(host_app)
        app = host_app.app
        print(app)
        uiapp = host_app.uiapp
        print(uiapp)
        uidoc = host_app.uidoc
        print(uidoc)
        print("**********")
        print(__revit__)
        doc = __revit__.ActiveUIDocument.Document # pyright: ignore
        print(doc)
        uidoc = __revit__.ActiveUIDocument
        print(uidoc)
        print("#" * 20)

        """
        """getset_descriptor error happen because there is no instance, the attr are looking for a abstract class attr"""
        """
        try:
            doc = UI.UIDocument.Document #method 1
            print(doc)
            print(doc.Title)
            print("method 1")
        except Exception as e:
            print(str(e))
        print("%"*10)


        try:

            doc = UI.UIApplication.ActiveUIDocument.Document
            print(doc)
            print(doc.Title)
            print("method 2")
        except Exception as e:
            print(str(e))
        print("%"*10)


        try:
            doc = HOST_APP.doc
            print(doc)
            print(doc.Title)
            print("method 3")
        except Exception as e:
            print(str(e))
        print("%"*10)

        try:
            doc = UI.UIDocument.ActiveView.Document
            print(doc)
            print(doc.Title)
            print("method 3")
        except Exception as e:
            print(str(e))
        print("%"*10)

        """
        #self.note.Text = "Curently pointing to doc: {}".format(doc.Title)
        self.funcs = [sample_func_1, sample_func_2]
        #self.funcs = [sample_func_1]
        #self.ext_events = [register_event(x) for x in self.funcs]
        self.Title = "xxxxxx Dockpane."
        self.Width = 300


    def update_doc(self):

        for doc in  __revit__.Documents:
            #print doc.Title

            # only active doc has a active view
            if doc.ActiveView:
                self.doc = doc
                self.note.Text = "Current doc:\n{}".format(doc.Title)
                return

            #
            # try:
            #     print doc.ActiveView.Name
            # except:
            #     print "cannot get active view"


        # for item in dir(__revit__):
        #     print item
        # print "#########"
        # print __revit__.Documents[0].Title
    @try_catch_error
    def button_transfer_in_Clicked(self, sender, e):
        self.update_doc()
        #print (e).Document



        #print dir(RhinoDockable)
        #print RhinoDockable.dock_doc
        #self.update_UI()
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        #print "primary button clicked"


        import imp
        #C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Rhino.panel\Rhino2Revit.pulldown\open_rhino_dockpane.pushbutton\Rhino_DockPane.py
        #C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Rhino.panel\Rhino2Revit.pulldown\transfer_rhino_drafting.pushbutton\transfer_rhino_drafting_script.py
        key = "Rhino2Revit.pulldown"
        file_path = __file__.split(key)[0] + r"{}\transfer_rhino_drafting.pushbutton\transfer_rhino_drafting_script.py".format(key)
        ref_module = imp.load_source("transfer_from_rhino", file_path)
        ref_module.transfer_rhino_drafting(self.doc)
        self.debug_textbox.Text = "Finish"


    @try_catch_error
    def button_export_out_Clicked(self, sender, e):
        self.update_doc()
        import imp
        #C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Rhino.panel\Rhino2Revit.pulldown\open_rhino_dockpane.pushbutton\Rhino_DockPane.py
        #C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Rhino.panel\Rhino2Revit.pulldown\export_to_rhino_drafter.pushbutton\export_to_rhino_drafter_script.py
        key = "Rhino2Revit.pulldown"
        file_path = __file__.split(key)[0] + r"{}\export_to_rhino_drafter.pushbutton\export_to_rhino_drafter_script.py".format(key)
        ref_module = imp.load_source("export_to_rhino", file_path)
        ref_module.export_to_rhino_drafter(self.doc)
        self.debug_textbox.Text = "Finish"


    def button_refresh_Clicked(self, sender, e):
        self.update_doc()

    def old_generic_click(self, func_name, keyword):

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





@try_catch_error
def register_rhino_dockpane():
    if not forms.is_registered_dockable_panel(RhinoDockable):
        forms.register_dockable_panel(RhinoDockable, default_visible = EA_UTILITY.is_SZ())
        #attach_dock_to_event(RhinoDockable)
        if EA_UTILITY.is_SZ():
            EA_UTILITY.show_toast(message = "Open it in Rhino2Revit",title = "Rhino Dock Regiesterd")
    else:
        EA_UTILITY.print_note( "Skipped registering dockable pane. Already exists.")
