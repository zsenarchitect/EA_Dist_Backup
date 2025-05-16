#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ ="""
Script for exporting Revit Family Instances to Rhino.
It converts each FamilyInstance's geometry into a Rhino block containing all its Breps
(or fallback Meshes). 

Block names in Rhino follow the format: "FamilyName_TypeName"
Each export includes a timestamp in the filename.
"""

__title__ = "Revit2Rhino"

import clr  # pyright: ignore
import logging

# Configure logging
logger = logging.getLogger("Revit2Rhino")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def enable_debug_logging():
    logger.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.DEBUG)
    logger.debug("Debug logging enabled")

try:
    import System  # pyright: ignore
    clr.AddReference('RhinoCommon')
    import Rhino  # pyright: ignore
    clr.AddReference('RhinoInside.Revit')
    from RhinoInside.Revit.Convert.Geometry import GeometryDecoder as RIR_DECODER  # pyright: ignore
    IMPORT_OK = True
except:
    IMPORT_OK = False


import proDUCKtion  # pyright: ignore
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, USER
from EnneadTab.REVIT import REVIT_APPLICATION

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def revit2rhino(doc):
    """Main entry point for Revit to Rhino export."""
    # Check if Rhino.Inside is available
    if not IMPORT_OK:
        NOTIFICATION.messenger("Please initiate [Rhino.Inside] First")
        return
    
    # Enable debug logging for developers
    if USER.IS_DEVELOPER:
        enable_debug_logging()
    
    # Launch the UI - everything else is handled by the UI
    import revit2rhino_UI
    revit2rhino_UI.show_dialog()


if __name__ == "__main__":
    revit2rhino(DOC)
