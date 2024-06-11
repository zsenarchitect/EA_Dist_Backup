# -*- coding: utf-8 -*-
"""Convert ACIS Solid to FreeForm Element.

Improved based on Frederic Beaupere's version.

creates FreeForm elements from your selected imported acis SAT
solid geometry, so you can turn it into Void/Solid apply materials
easily and get access to its shape handles.

"""
#pylint: disable=import-error,invalid-name,broad-except,superfluous-parens
from pyrevit.framework import Stopwatch
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script

logger = script.get_logger()


def verify_selection(selected_elems, doc):
    if doc.IsFamilyDocument:
        if all([isinstance(x, DB.DirectShape) for x in selected_elems]):
            return True
        else:
            forms.alert("More than one element is selected or selected "
                        "element is not an ACIS Solid.", exitscript=True)
    else:
        forms.alert("Please select one imported ACIS SAT DirectShape "
                    "while in Family Editor.", exitscript=True)
    return False


stopwatch = Stopwatch()
selection = revit.get_selection()


display_text = "#WIP: Do you want to include hidden objects in the file?"
options = ["Convert Visible Only.", "Convert Both Visible and Hidden."]
result = forms.alert(display_text, options = options)
#note to self, this might not work for external visiblity setting


if verify_selection(selection, revit.doc):
    stopwatch.Start()
    for sat_import in selection:
        geom_opts = DB.Options()

        if result == "Visible Only.":
            geom_opts.IncludeNonVisibleObjects = False
        else:
            geom_opts.IncludeNonVisibleObjects = True

        logger.debug('Converting: %s', sat_import)
        solids = []
        for geo in sat_import.Geometry[geom_opts]:
            if isinstance(geo, DB.Solid):
                if geo.Volume > 0.0:
                    solids.append(geo)
        # create freeform from solids
        with revit.Transaction("Convert SAT to Revit"):
            for solid in solids:
                DB.FreeFormElement.Create(revit.doc, solid)
            revit.doc.Delete(sat_import.Id)

logger.debug('Conversion completed in: %s', stopwatch.Elapsed)


##possible add:
#ask what subcaterfgory to put.
#ask layer information to take and assign? might not support....
#ask which rhino to import
