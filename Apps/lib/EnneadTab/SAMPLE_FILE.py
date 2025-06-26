"""used to retrive sample file in rhino, reivt and excel.
Good the sharing template"""

import os
import ENVIRONMENT
import NOTIFICATION

def get_file(file_name):
        
    path = os.path.join(ENVIRONMENT.DOCUMENT_FOLDER, ENVIRONMENT.get_app_name(), file_name)

    if ENVIRONMENT.get_app_name() == "revit":
        from EnneadTab.REVIT import REVIT_APPLICATION
        path = os.path.join(ENVIRONMENT.DOCUMENT_FOLDER, 
                            ENVIRONMENT.get_app_name(), 
                            str(REVIT_APPLICATION.get_revit_version()), 
                            file_name)
    if os.path.exists(path):
        return path
    NOTIFICATION.messenger("Cannot find [{}]".format(file_name))
    print ("cannot find [{}]".format(path))
    return None


if __name__ == "__main__":
    print (get_file("LifeSafetyCalculator.rfa"))