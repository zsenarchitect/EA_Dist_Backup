#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Convert between a typical imperial family and metric family by setting up unit."
__title__ = "Change Family Unit"
__tip__ = True
import proDUCKtion  # pyright: ignore
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS, REVIT_UNIT
from Autodesk.Revit import DB  # pyright: ignore

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

# Global dictionary for unit conversion IDs
UNIT_IDS = {
    "metric": {
        "length": "millimeters",
        "area": "squareMeters"
    },
    "imperial": {
        "length": "feetFractionalInches",
        "area": "squareFeet"
    }
}

# Function to change document units
def change_document_units(doc, to_metric):
    # Start a transaction
    t = DB.Transaction(doc, 'Convert Units')
    t.Start()

    # Get current document units
    project_units = doc.GetUnits()

    # Determine the conversion mode
    unit_system = "metric" if to_metric else "imperial"

    # List of unit types to convert (length, area)
    unit_types = ["length", "area"]

    # Loop through the unit types and convert each one
    for unit_type in unit_types:
        unit_id = UNIT_IDS[unit_system][unit_type]
        new_format_options = DB.FormatOptions(REVIT_UNIT.lookup_unit_id(unit_id))
        project_units.SetFormatOptions(REVIT_UNIT.lookup_unit_spec_id(unit_type), new_format_options)

    # Apply the updated units to the document
    doc.SetUnits(project_units)

    # Commit the transaction
    t.Commit()

    print("Units conversion completed.")

# Function to process nested families
def process_nested_families(doc, to_metric=True):
    # Collect all family instances in the document
    families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()

    for family in families:
        if family is not None and not family.IsSystemFamily:
            # Get the family document
            family_doc = doc.EditFamily(family)
            # Change units in the nested family
            change_document_units(family_doc, to_metric)
            # Save and close the family
            family_doc.Save()
            family_doc.Close()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def change_family_unit():
    # User input: choose to convert to Metric or Imperial
    to_metric = True  # Default conversion is to Metric

    # Options for user selection
    ops = ["Convert To Imperial", "Convert To Metric"]
    res = REVIT_FORMS.dialogue(main_text="Choose the unit conversion mode:", options=ops)

    if res is None:
        return

    if res == ops[0]:
        to_metric = False
    elif res == ops[1]:
        to_metric = True

    # Process the current document
    change_document_units(DOC, to_metric)

################## main code below #####################
if __name__ == "__main__":
    change_family_unit()
