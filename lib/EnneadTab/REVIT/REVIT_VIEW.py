

try:

    from Autodesk.Revit import DB
    from Autodesk.Revit import UI
    UIDOC = __revit__.ActiveUIDocument
    DOC = UIDOC.Document
    
    import REVIT_APPLICATION
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()

def get_view_by_name( view_name, doc = DOC):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
    
    for view in all_views:
        if view.Name == view_name:
            return view
    return None

def get_default_view_type(view_type, doc = DOC):

    mapper = {"3d":DB.ViewFamily.ThreeDimensional,
              "schedule":DB.ViewFamily.Schedule,
              "drafting":DB.ViewFamily.Drafting,
              "section": DB.ViewFamily.Section,
              "elevation": DB.ViewFamily.Elevation,
              "plan":DB.ViewFamily.FloorPlan}
    view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
    potential_types = filter(lambda x: x.ViewFamily == mapper[view_type], view_family_types)
    return potential_types[0]