
from pyrevit import EXEC_PARAMS, script
from pyrevit import forms
import traceback
from pyrevit.coreutils import envvars
import EnneadTab


args = EXEC_PARAMS.event_args
from Autodesk.Revit import DB
from Autodesk.Revit import UI


from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException



def add_view_to_sheet(view):

    doc = view.Document
    sheet = forms.select_sheets(title = "Select sheet to add view to.", 
                                multiple=False, 
                                doc = doc)
    if not sheet:
        return
    
    t = DB.Transaction(doc, "Add view to sheet")
    t.Start()
    
    DB.Viewport.Create(doc, sheet.Id, view.Id, DB.XYZ(0,0,0))
    t.Commit()
    

    UI.UIDocument(doc).ActiveView = sheet


@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def rename_view(view):
    # print "changing view name"
    from pyrevit import forms
    doc = view.Document
    old_name = view.Name
    new_name = forms.ask_for_string(old_name, prompt="How do you want to rename this new view?",
                             title = "Find the new view.")
    t = DB.Transaction(doc, "change view name")
    t.Start()
    view.Name = new_name
    t.Commit()
    EnneadTab.NOTIFICATION.messenger(main_text = "View renamed:\n[{}]-->[{}]".format(old_name,view.Name))
       
       
    opts = ["Yes, add it to a sheet.",
            ["No, I am just doing study views.", "Will not add to any sheet."]]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue(main_text = "Add the view to a sheet?",
                                                options = opts)
    
    if res == opts[0]:
        add_view_to_sheet(view)
        return
    else:
        UI.UIDocument(doc).ActiveView = view
  


# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.kwargs = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                self.OUT = self.do_this(*self.kwargs)
            except Exception as e:
                # print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"
    
    
    
@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def check_new_view():
    if not envvars.get_pyrevit_env_var("IS_DOC_CHANGE_HOOK_ENABLED"):
        return

    view_filter = DB.ElementClassFilter (DB.View)
    added = args.GetAddedElementIds(view_filter)
    if len(added) == 0:
        return
    doc = EXEC_PARAMS.event_args.GetDocument ()
    added_views = [doc.GetElement(x) for x in added]
    # added_views = [x for x in added_views if hasattr(x,"ViewType") and x.ViewType in [DB.ViewType.Section,
    #                                                                             DB.ViewType.AreaPlan,
    #                                                                             DB.ViewType.Elevation,
    #                                                                             DB.ViewType.FloorPlan,
    #                                                                             DB.ViewType.DraftingView,
    #                                                                             DB.ViewType.Detail]]
    # print (added_views)

    
    simple_event_handler = SimpleEventHandler(rename_view)
    ext_event = ExternalEvent.Create(simple_event_handler)
  
    options = ["Yes, rename it!",
               "No, thank you"]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue(main_text = "Do you want to rename the newly created view(s)?",
                                                sub_text = "",
                                                options = options)

    if res != options[0]:
        return
        
    
    for view in added_views:

        simple_event_handler.kwargs = view,
        ext_event.Raise()


####################################################    
output = script.get_output()
output.close_others()
if __name__ == "__main__":
    check_new_view()