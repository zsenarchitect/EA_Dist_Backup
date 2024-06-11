# -*- coding: utf-8 -*-
__doc__ = "Try the all-in-one Rhino2Revit UI window."
__title__ = "Force Convert Solid Dwg To Revit(Legacy)"


import clr
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
import RHINO2REVIT_UTILITY
import time
from EA_UTILITY import dialogue, show_toast, get_file_name_from_path, is_SZ
# import EA_UTILITY
import EnneadTab

def clean_import_object_style():

    categories = revit.doc.Settings.Categories
    import_OSTs = filter(lambda x: "Imports in Families"  in x.Name, categories)
    if len(import_OSTs) == 0:
        return
    import_OSTs = list(import_OSTs[0].SubCategories)
    import_OSTs.sort(key = lambda x: x.Name)

    selected_categories = forms.SelectFromList.show(import_OSTs, title = "Better to not bring DWG category to project. Only bring the model category.", name_attr = "Name", multiselect = True, button_name = "Delete selected imported object style from DWG overload.")
    #selected_categories = import_OSTs
    t = DB.Transaction(revit.doc, "clean up imported OST")
    t.Start()
    for category in selected_categories:
        print("--deleting imported DWG SubC: " + category.Name)
        revit.doc.Delete(category.Id)
    t.Commit()

    print("\n\nCleaning finish.")
    pass

######################################################
output = script.get_output()
output.close_others()

if not is_SZ():
    dialogue(main_text = "Only use this function if the default Rhino2Revit fails after you have tried EVERYTHING in the 'how to...' instruction, including....",sub_text = "\n\t-Select and fix invalid geomtry in Rhino\n\t-Done non-manifold edge and naked edge check in Rhino.\n\t-Curvature anaylise show no warping color on flat surface")

logger = script.get_logger()




# make sure active document is a family
forms.check_familydoc(exitscript=True)

start_time = time.time()
exisiting_cads = DB.FilteredElementCollector(revit.doc).OfClass(DB.ImportInstance).ToElements()
t = DB.Transaction(revit.doc, "import DWG")
t.Start()
with forms.WarningBar(title = "You can pick .dwg file"):
    source_file = forms.pick_file(file_ext = "dwg")
options = DB.DWGImportOptions()
cad_import_id = clr.StrongBox[DB.ElementId]()
revit.doc.Import(source_file, options,revit.doc.ActiveView, cad_import_id)
t.Commit()
current_cad_imports = DB.FilteredElementCollector(revit.doc).OfClass(DB.ImportInstance).ToElements()
# cad_import = revit.doc.GetElement(list(cad_import_id))
for cad_import in current_cad_imports:
    if cad_import not in exisiting_cads:
        break
#cad_import


"""
script.exit()
selection = revit.get_selection()

cad_import = selection.first
print(cad_import)
"""




cad_trans = cad_import.GetTransform()
cad_type = cad_import.Document.GetElement(cad_import.GetTypeId())
cad_name = revit.query.get_name(cad_type)

family_cat = revit.doc.OwnerFamily.FamilyCategory

geo_elem = cad_import.get_Geometry(DB.Options())
geo_elements = []
for geo in geo_elem:
    logger.debug(geo)
    if isinstance(geo, DB.GeometryInstance):
        geo_elements.extend([x for x in geo.GetSymbolGeometry()])

solids = []
for gel in geo_elements:
    logger.debug(gel)
    if isinstance(gel, DB.Solid):
        #print "found solid"
        # if hasattr(gel, 'Volume') and gel.Volume > 0.0:
        solids.append(gel)
    elif isinstance(gel, DB.Mesh):
        print("found mesh, trying to convert: {}".format(gel))
        RHINO2REVIT_UTILITY.mesh_convert(gel, cad_trans,family_cat,cad_name)

    else:
        print("Other geo found: {}, will ignore...".format(gel))




# create freeform from solids
converted_els = []
with revit.Transaction("Convert CAD Import to FreeFrom/DirectShape"):
    for solid in solids:
        converted_els.append(DB.FreeFormElement.Create(revit.doc, solid))
    cad_import.Pinned = False
    revit.doc.Delete(cad_import.Id)

time_span = time.time() - start_time
show_toast(title = "{} import finished!!".format(get_file_name_from_path(source_file)),
            message = "Import used {} seconds = {} mins".format(time_span, time_span/60))


RHINO2REVIT_UTILITY.assign_subC(converted_els,source_file)

try:
    clean_import_object_style()
except Exception as e:
    print("fail to clean up imported category SubC becasue " + str(e))


import ENNEAD_LOG
ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = "Rhino2Revit_Force Import", show_toast = True)
