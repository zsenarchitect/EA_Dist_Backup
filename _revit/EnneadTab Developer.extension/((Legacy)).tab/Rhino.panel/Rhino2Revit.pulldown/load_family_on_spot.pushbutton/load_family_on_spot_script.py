#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "NOT IN USE"
__title__ = "Load Family On Internal Origin(NOT IN USE)"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
family_doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument

class FamilyOption(DB.IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues = True# true means use project value
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        overwriteParameterValues = True
        source = DB.FamilySource.Family
        return True



def load_family_to_docs(doc, family_doc):

    try:
        family_doc.LoadFamily(doc, FamilyOption())
    except Exception as e:
        print("cannot load family")





def load_family_on_spot():

    # pick doc to load into
    doc = EA_UTILITY.select_top_level_docs(select_multiple = False)
    load_family_to_docs(doc, family_doc)



    # activate the doc,
    views = DB.FilteredElementCollector(doc).OfClass(DB.View3D).WhereElementIsNotElementType().ToElements()
    for view in views:
        print(view.Name)
    uiviews = uidoc.GetOpenUIViews()
    for uiview in uiviews:
        print(uiview.ViewId)
    uidoc.RequestViewChange(view)

    # place new instance at origin and pin

    # pick a level that has close internal absolute 0 high, create one if needed.


    # set elevation offset as 0

    print("over")
    pass
    """
    t = DB.Transaction(doc, "Link into link doc view for this dummy")
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """


    """

    import selected object style from project or family
    """
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    load_family_on_spot()
