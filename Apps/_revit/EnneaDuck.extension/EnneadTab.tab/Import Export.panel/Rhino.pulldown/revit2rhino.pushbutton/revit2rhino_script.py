#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ ="""
Script for exporting Revit Family Instances to Rhino.
It converts each FamilyInstance's geometry into a Rhino block containing all its Breps
(or fallback Meshes). The block definition is annotated with 'RevitElementID'.

GEOMETRY EXTRACTION METHODS:
1. First tries GetSymbolGeometry() - Returns untransformed geometry in family coordinate system.
   This is ideal for block definitions as it's in the symbol's local coordinate space.

2. If that fails, uses GetInstanceGeometry() - Returns geometry that includes the instance
   transformation and is already in the project coordinate system.
   For this case, we untransform the geometry before creating the block definition.

Block names in Rhino follow the format: "FamilyName_TypeName"
Each export includes a timestamp in the filename.
"""

__title__ = "Revit2Rhino"

import clr  # pyright: ignore
import os
import time
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

from pyrevit import forms
from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, UI, ENVIRONMENT, USER
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_UNIT, REVIT_RHINO, REVIT_FORMS
from Autodesk.Revit import DB  # pyright: ignore

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

# get_family_instances_from_view function has been moved to the UI module

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
