#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """Batch adding shared parameters to multiple project files. 
This can reduce mistake during manual operation of repeating task.

If this shared parameter has been added before, it will not add again.
Note that for Revit, the spelling is not important, the GUID is important."""
__title__ = "Proj. Parameter\nBatch Adding"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_APPLICATION, REVIT_PARAMETER
from EnneadTab import ERROR_HANDLE, LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()
            

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def parameter_manager(doc):
    definitions = REVIT_SELECTION.pick_shared_para_definition(doc, select_multiple = True)

    if not definitions:
        return
    docs = REVIT_SELECTION.pick_top_level_docs()
    if not docs:
        return
    
    cates = REVIT_SELECTION.pick_category(doc)
  
    for doc in docs:
        t = DB.Transaction(doc, __title__)
        t.Start()
        for definition in definitions:
            REVIT_PARAMETER.add_shared_parameter_to_project_doc(doc,
                                                                definition,
                                                                "Data",
                                                                cates,
                                                                is_instance_parameter=True)

            print ("new shared parameter [{}] added to doc [{}]".format(definition.Name, doc.Title))
        t.Commit()

    print ("\n\nTool Finish!!!!")

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    parameter_manager(DOC)
