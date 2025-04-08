#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Legacy, now do it in view panel"
__title__ = "64_3D workset views(Legacy)"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def get_all_userworkset():
    worksets = DB.FilteredWorksetCollector(doc).ToWorksets()
    return filter(lambda x: x.Kind .ToString() == "UserWorkset", worksets)


def make_3D_views_from_workset():
    worksets = get_all_userworkset()
    """
    for workset in worksets:
        print(workset.Name)
    """

    views = [create_view(x.Name) for x in worksets]
    for view, workset in zip(views, worksets):
        print("---working on setting workset visibility for view: " + view.Name)
        view.SetWorksetVisibility(workset.Id, DB.WorksetVisibility.Visible)
        for other_workset in worksets:
            if other_workset == workset:
                continue
            view.SetWorksetVisibility(other_workset.Id, DB.WorksetVisibility.Hidden)

        try:
            view.LookupParameter("Views_$Group").Set("00_EA's_Little Helper")
            view.LookupParameter("Views_$Series").Set("Workset Check")
        except:
            pass



def create_view(view_name):
    desired_name = "EnneadTab Workset View_" + view_name
    view = get_view_by_name(desired_name)
    if view is not None:
        return view
    print("####creating new axon view for " + view_name)
    view = DB.View3D.CreateIsometric (doc, get_threeD_view_type().Id)
    try:
        view.Name = desired_name
    except:
        pass
    return view

def get_view_by_name(name):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    for view in all_views:
        if name == view.Name:
            return view
    return None

def get_threeD_view_type():
    view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
    return filter(lambda x: x.ViewFamily == DB.ViewFamily.ThreeDimensional, view_family_types)[0]

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    t = DB.Transaction(doc, "create view from workset")
    t.Start()
    make_3D_views_from_workset()
    t.Commit()

