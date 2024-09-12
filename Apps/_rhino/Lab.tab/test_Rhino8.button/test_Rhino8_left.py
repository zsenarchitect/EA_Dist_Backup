
__title__ = "TestRhino8"
__doc__ = "This button does TestRhino8 when left click"

import traceback
from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT
from EnneadTab import ERROR_HANDLE
from EnneadTab import VERSION_CONTROL, NOTIFICATION, LOG,ERROR_HANDLE
from EnneadTab.RHINO import RHINO_RUI, RHINO_ALIAS

def test_Rhino8():
    print ("Placeholder func <{}> that does this:{}".format(__title__, __doc__))
    print ("This is a test for Rhino8")
    print (ENVIRONMENT.DUMP_FOLDER)
    print (ENVIRONMENT)

    VERSION_CONTROL.update_EA_dist()
    # RHINO_RUI.update_my_rui()
    # RHINO_ALIAS.register_alias_set()


    
if __name__ == "__main__":
    test_Rhino8()
