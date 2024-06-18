
from pyrevit import  EXEC_PARAMS, script

import EnneadTab
from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 
uiapp = UI.UIApplication(doc.Application)

"""to try this:
make a before exc for new section
"""
@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():
    
    if not EnneadTab.USER.is_SZ():
   
        return
    is_hook_on_hold = EnneadTab.ENVIRONMENT.get_environment_variable("is_hook_on_hold", default_value = "False")

    is_hook_on_hold = is_hook_on_hold == "True"
    is_hook_on_hold = not is_hook_on_hold
    
    
    EnneadTab.ENVIRONMENT.set_environment_variable("is_hook_on_hold", str(is_hook_on_hold))
    
    if is_hook_on_hold:
        return

    options = ["Yes",
               "No"]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue(main_text = "Do you want to open view afterward?",
                                                sub_text = "",
                                                options = options)
    is_post_opening = False
    if res == options[0]:
        is_post_opening = True
        
        
    if is_post_opening:
        original_views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
        original_views = [v.Name for v in original_views if v.IsTemplate == False]
        
 
    command_id = UI.RevitCommandId.LookupPostableCommandId(UI.PostableCommand.Section)
    uiapp.PostCommand(command_id)
  
    
    if is_post_opening:
        current_views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
        current_views = [v.Name for v in current_views if v.IsTemplate == False]
        
        print (len(original_views))
        print (len(current_views))
        # new_view = list(set(original_views) - set(current_views))[0]
        # print (new_view.Name)
        # UI.UIDocument(doc).ActiveView = new_view

        
    print(1)
    
############################
# output = script.get_output()
# output.close_others()


if __name__ == '__main__':
    main()