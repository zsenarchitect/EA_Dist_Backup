"""VERY IMPORTANT:
everything here should have ZERO dependency becasue this is the foundation of many location finder"""


import os
import sys


IS_PY3 = sys.version.startswith("3")
IS_PY2 = not IS_PY3


# this is prepared for future where each user can pull git to local computer, this can make thing run faster, as well version control.
ECOSYSTEM_FOLDER = "{}\\EnneadTab Ecosystem".format("{}\Documents".format(os.environ["USERPROFILE"]))
if not os.path.exists(ECOSYSTEM_FOLDER):
    os.makedirs(ECOSYSTEM_FOLDER)

OS_DIST = "{}\\EA_Dist".format(ECOSYSTEM_FOLDER)
IS_LOCAL_OS = os.path.exists(OS_DIST)
OS_RHINO = "{}\\_rhino".format(OS_DIST)
OS_REVIT = "{}\\_revit".format(OS_DIST)
OS_LIB = "{}\\ENNEAD.extension\\lib".format(OS_REVIT)
OS_CORE_FOLDER = "{}\\EnneadTab".format(OS_LIB)
OS_EXE_FOLDER = "{}\\EXE\\EXE_PRODUCTS".format(OS_CORE_FOLDER)
OS_CORE_IMAGES_FOLDER = "{}\\images".format(OS_CORE_FOLDER)


# the big gfolder below are being phased out as to transition to local folder.

HOSTER_FOLDER = "L:\\4b_Applied Computing" # if in future the entire roject is reloacated, change this HOSTER FOLDER
IS_L_DRIVE_ACCESSIBLE = os.path.exists(HOSTER_FOLDER)


# this is needed becasue some remapper function cannot take None to remap, so lets assume this is the starting point
GITHUB_FOLDER = "C:\\Users\\szhang\\github" 



ARCHIVE_FOLDER_FOR_RHINO = "{}\\03_Rhino\\xx_EnneadTab for Rhino_Archives".format(HOSTER_FOLDER)
PUBLIC_L_EXE_FOLDER = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe".format(HOSTER_FOLDER)
MISC_FOLDER = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Misc".format(HOSTER_FOLDER)
SHARED_DATA_DUMP_FOLDER = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Shared Data Dump".format(HOSTER_FOLDER)


RHINO_SCRIPT_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) + "\\Toolbar"


RHINO_USER_LOG_FOLDER = "{}\\03_Rhino\\12_EnneadTab for Rhino\\LOG".format(HOSTER_FOLDER)
REVIT_USER_LOG_FOLDER = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\LOG".format(HOSTER_FOLDER)


PUBLISH_FOLDER_FOR_REVIT = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Published".format(HOSTER_FOLDER)
PUBLISH_BETA_FOLDER_FOR_REVIT = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Published_Beta_Version".format(HOSTER_FOLDER)
CORE_MODULE_FOLDER_FOR_PUBLISHED_REVIT = "{}\\ENNEAD.extension\\lib\\EnneadTab".format(PUBLISH_FOLDER_FOR_REVIT)
CORE_MODULE_FOLDER_FOR_PUBLISHED_BETA_REVIT = "{}\\ENNEAD.extension\\lib\\EnneadTab".format(PUBLISH_BETA_FOLDER_FOR_REVIT)
CORE_RESOURCES_FOLDER_FOR_PUBLISHED_REVIT = "{}\\sources".format(CORE_MODULE_FOLDER_FOR_PUBLISHED_REVIT)
CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT = "{}\\images".format(CORE_MODULE_FOLDER_FOR_PUBLISHED_REVIT)
CORE_AUDIOS_FOLDER_FOR_PUBLISHED_REVIT = "{}\\audios".format(CORE_MODULE_FOLDER_FOR_PUBLISHED_REVIT)



PUBLISH_FOLDER_FOR_RHINO = "{}\\03_Rhino\\12_EnneadTab for Rhino".format(HOSTER_FOLDER)
CORE_MODULE_FOLDER_FOR_PUBLISHED_RHINO = "{}\\Source Codes\\lib\\EnneadTab".format(PUBLISH_FOLDER_FOR_RHINO)


DEPENDENCY_FOLDER = DEPENDENCY_FOLDER_LEGACY = "{}\\03_Rhino\\12_EnneadTab for Rhino\\Dependency Modules".format(HOSTER_FOLDER)
DEPENDENCY_FOLDER_PY2 = "{}\Dependency\PY2".format(PUBLISH_FOLDER_FOR_RHINO)
DEPENDENCY_FOLDER_PY3 = "{}\Dependency\PY3".format(PUBLISH_FOLDER_FOR_RHINO)


LIMITED_REVIT_PROJECTS = ["some gov project name that want to limit enenadtab access"]

REVIT_HOST_FOLDER = PUBLISH_FOLDER_FOR_REVIT # the direct subfolder has .extension folders
RHINO_HOST_FOLDER = PUBLISH_FOLDER_FOR_RHINO
if IS_LOCAL_OS:
    REVIT_HOST_FOLDER = OS_REVIT
    RHINO_HOST_FOLDER = OS_RHINO
if os.path.exists("{}\\EnneadTab-for-Revit".format(GITHUB_FOLDER)):
    REVIT_HOST_FOLDER = "{}\\EnneadTab-for-Revit".format(GITHUB_FOLDER)
if os.path.exists("{}\\EnneadTab-for-Rhino".format(GITHUB_FOLDER)):
    RHINO_HOST_FOLDER = "{}\\EnneadTab-for-Rhino".format(GITHUB_FOLDER)

EXE_FOLDER = PUBLIC_L_EXE_FOLDER
if os.path.exists(OS_EXE_FOLDER):
    EXE_FOLDER = OS_EXE_FOLDER


def is_Rhino_environment():
    """Check if current environment is Rhino.

    Returns:
        bool: True if current environment is Rhino.
    """
    try:
        import rhinoscriptsyntax
        return True
    except:
        return False

def is_Grasshopper_environment():
    try:
        import Grasshopper # pyright: ignore
        return True
    except:
        return False

def is_Revit_environment():
    """Check if current environment is Revit.

    Returns:
        bool: True if current environment is Revit.
    """
    try:
        from Autodesk.Revit import DB # pyright: ignore
        return True
    except:
        return False

def is_RhinoInsideRevit_environment():
    import clr # pyright: ignore
    try:
        clr.AddReference('RhinoCommon')
        clr.AddReference('RhinoInside.Revit')
        return True
    except:
        return False

def is_Revit_limited():
    """Many of the project has restriction requirement to 
accessibility, usually government sentitive projects.

So here are project names that has such limitation, and 
i will make sure it is not trying to connect to L drive."""
    if not is_Revit_environment():
        return False


    import REVIT
    doc = REVIT.REVIT_APPLICATION.get_doc()
    return doc.Title in LIMITED_REVIT_PROJECTS if doc else False

def is_terminal_environment():
    return not is_Rhino_environment() and not is_Revit_environment()



def unit_test():
    import inspect
    # get all the global varibales in the current script

    for i, x in enumerate(sorted(globals())):
        content = globals()[x]
        
        if inspect.ismodule(content):
            continue
        
        if not x.startswith("_") and not callable(content):
            print(x, " = ", content)

            
            if isinstance(content, bool):
                continue
            
            if not isinstance(content, list):
                content = [content]

            for item in content:
                if "\\" in item:
                    is_ok = os.path.exists(item) or os.path.isdir(item)
                    assert is_ok
          


###############
if __name__ == "__main__":
    unit_test()
