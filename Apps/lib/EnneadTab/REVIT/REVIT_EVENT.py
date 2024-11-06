
"""sometimessssss a exernal event does not need a modeless form, that is why this class is a seperated piece"""

import traceback
try:
    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    from pyrevit.coreutils import envvars


    from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent # pyright: ignore
    from Autodesk.Revit.Exceptions import InvalidOperationException # pyright: ignore
    REF_CLASS_IExternalEventHandler = IExternalEventHandler
except:
    REF_CLASS_IExternalEventHandler = object

EVENT_MARKER_KEY="ENNEADTAB_EVENT_MARKER" 
import ERROR_HANDLE


# Create a subclass of IExternalEventHandler
class SimpleEventHandler(REF_CLASS_IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.args = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                event_mark_start()
                self.OUT = self.do_this(*self.args)
                event_mark_end()

            except:
                print ("event runner failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"
    
    
    
class ExternalEventRunner:
    
    def __init__(self, *funcs):
        if len(funcs) == 0:
            print("here is no funcs")
            return
        for func in funcs:
            original_func = getattr(func, 'original_function', func)  # Use the original function if available
            handler = SimpleEventHandler(original_func)
            setattr(self, "simple_event_handler_{}".format(original_func.__name__), handler)
            setattr(self, "ext_event_{}".format(original_func.__name__), ExternalEvent.Create(handler))
            # print (original_func.__name__ + " has been regiested!!!!!!!!")
            
    @ERROR_HANDLE.try_catch_error(is_silent=True)
    def run(self, func_name, *args):
        event = getattr(self, "ext_event_{}".format(func_name))
        handler = getattr(self, "simple_event_handler_{}".format(func_name))
        
        
        handler.args = args
        event.Raise()
        
        wait_event()
        
        return handler.OUT





#TO-DO: the idea behinds those two mark funcs is to resolve the issue that modeless form func once passed cannot pass the res back.
def event_mark_start():
    return
    os. evn[MARKER] = True

def event_mark_end():
    return
    os. evn[MARKER] = False

def wait_event():
    return
    max_wait=15
    while True:
        if is_event_done():
            return 

        max_wait -= 1
        
        if max_wait<0:
            return 


def is_open_hook_disabled():
    return envvars.get_pyrevit_env_var("IS_OPEN_HOOK_DISABLED")


def set_open_hook_depressed(stage = True):
    envvars.set_pyrevit_env_var("IS_OPEN_HOOK_DISABLED", stage)


def is_L_drive_alert_hook_depressed():
    return envvars.get_pyrevit_env_var("IS_L_DRIVE_WORKING_ALARM_DISABLED")


def set_L_drive_alert_hook_depressed(stage = True):
    envvars.set_pyrevit_env_var("IS_L_DRIVE_WORKING_ALARM_DISABLED", stage)


    
def is_sync_queue_disabled():
    return envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED")


def set_sync_queue_enable_stage(stage = True):
    envvars.set_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED", not(stage))


def is_doc_change_hook_depressed():
    return envvars.get_pyrevit_env_var("IS_DOC_CHANGE_DISABLED")


def set_doc_change_hook_depressed(stage = True):
    envvars.set_pyrevit_env_var("IS_DOC_CHANGE_DISABLED", stage)


def is_sync_cancelled():
    return envvars.get_pyrevit_env_var("IS_SYNC_CANCELLED")


def set_sync_cancelled(stage = True):
    envvars.set_pyrevit_env_var("IS_SYNC_CANCELLED", stage)


def is_family_load_hook_enabled():
    return envvars.get_pyrevit_env_var("IS_FAMILY_LOAD_HOOK_ENABLED")


def set_family_load_hook_stage(stage = True):
    envvars.set_pyrevit_env_var("IS_FAMILY_LOAD_HOOK_ENABLED", stage)

def is_all_sync_closing():
    return envvars.get_pyrevit_env_var("IS_ALL_SYNC_CLOSING")

def set_all_sync_closing(stage = True):
    envvars.set_pyrevit_env_var("IS_ALL_SYNC_CLOSING", stage)

