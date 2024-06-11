
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
import RHINO2REVIT_UTILITY
from EA_UTILITY import dialogue, show_toast, get_file_name_from_path

import time
__doc__ = "Try the all-in-one Rhino2Revit UI window."
__title__ = "Rhino2Revit Converter(Legacy)"

output = script.get_output()
output.self_destruct(60)



###########################################################################



if revit.doc.IsFamilyDocument == False:
    dialogue(main_text = "It needs to be a family document environment.\n\nIn-place family in project is not accepted.")
    script.exit()


with forms.WarningBar(title = "You can pick .3dm(Rhino) file"):
    source_file = forms.pick_file(file_ext = "3dm")
    #, title = "Please pick a Rhino file or .SAT file here."

if not source_file:
    script.exit()

bad_geo_found = False
start_time = time.time()
with revit.Transaction("Rhino2Revit"):
    converted_els = []
    geos =  DB.ShapeImporter().Convert(revit.doc, source_file)
    for geo in geos:
        try:
            converted_els.append(DB.FreeFormElement.Create(revit.doc, geo))
        except Exception as e:
            print("-----Cannot import this part of file, skipping: {}".format(geo))
            print (e)
            print("-----")
            bad_geo_found = True
            #mesh_convert(geo)
            #converted_els.append(DB.FreeFormElement.Create(revit.doc, geo.GetSymbolGeometry()))
time_span = time.time() - start_time
show_toast(title = "{} import finished!!".format(get_file_name_from_path(source_file)),
            message = "Import used {} seconds = {} mins".format(time_span, time_span/60))


RHINO2REVIT_UTILITY.assign_subC(converted_els, source_file)


import ENNEAD_LOG
ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = "Rhino2Revit", show_toast = True)
