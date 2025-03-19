
__title__ = "RegisterMirror"
__doc__ = "Help Jazzy to register mirror command shortcut with and without copy"


from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.RHINO import RHINO_ALIAS

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def register_mirror():

    RHINO_ALIAS.register_shortcut("F1", "_mirror _copy=Yes ")
    RHINO_ALIAS.register_shortcut("F2", "_mirror _copy=No ")
    NOTIFICATION.messenger("You have registered the shortcut \"F1\" to mirror with copy and \"F2\" for mirror without copy")

    
if __name__ == "__main__":
    register_mirror()
