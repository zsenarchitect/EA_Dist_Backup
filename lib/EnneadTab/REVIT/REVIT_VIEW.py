

from EnneadTab import NOTIFICATION


try:

    from Autodesk.Revit import DB
    from Autodesk.Revit import UI
    UIDOC = __revit__.ActiveUIDocument
    DOC = UIDOC.Document
    
    import REVIT_APPLICATION
    import REVIT_SELECTION
    from pyrevit.coreutils import envvars
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


def set_active_view_by_name(view_name, doc = DOC):
    view = get_view_by_name(view_name, doc)
    if view:
        REVIT_APPLICATION.get_uidoc().ActiveView = view
    else:
        NOTIFICATION.messenger("<{}> does not exist...".format(view_name))




def switch_to_sync_draft_view(doc):


    view = get_view_by_name("EnneadTab Quick Sync", doc)

    if not view:
        t = DB.Transaction(doc, "Create Drafting View")
        t.Start()
        view = DB.ViewDrafting.Create(doc, get_default_view_type("drafting", doc = doc).Id)
        view.Name = "EnneadTab Quick Sync"

        DB.TextNote.Create(doc, 
                           view.Id, 
                           DB.XYZ(0, 0, 0), 
                           'Confucius Says:\n"Syncing over drafting view is quicker."', 
                           REVIT_SELECTION.get_all_textnote_types(doc = doc, return_name=False)[0].Id)
        t.Commit()

    envvars.set_pyrevit_env_var("LAST_VIEW_BEFORE_SYNC", REVIT_APPLICATION.get_uidoc().ActiveView.Name)
    set_active_view_by_name("EnneadTab Quick Sync")

def switch_from_sync_draft_view():
    last_view_name = envvars.get_pyrevit_env_var("LAST_VIEW_BEFORE_SYNC")
    if not last_view_name:
        return

    set_active_view_by_name(last_view_name)

    for open_view in REVIT_APPLICATION.get_uidoc().GetOpenUIViews():
        
        if open_view.Name == "EnneadTab Quick Sync":
            open_view.Close()


