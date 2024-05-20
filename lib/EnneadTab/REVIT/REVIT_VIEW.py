# -*- coding: utf-8 -*-

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
        # UIDOC.RequestViewChange(view)
        try:
            REVIT_APPLICATION.get_uidoc().ActiveView = view
        except Exception as e:
            NOTIFICATION.messenger(str(e))
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
                           'Confucius Says:\n"Syncing over drafting view is quicker."\n⎛ -᷄ ᴥ -᷅ ⎞೯', 
                           REVIT_SELECTION.get_all_textnote_types(doc = doc, return_name=False)[0].Id)

        t.Commit()


    t = DB.Transaction(doc, "Sync Quicker...")
    t.Start()
    try:
        view.LookupParameter("Views_$Group").Set("Ennead")
        view.LookupParameter("Views_$Series").Set(u"Sync Monitor  ◔.̮◔✧")
    except:
        pass
    t.Commit()

    
    envvars.set_pyrevit_env_var("LAST_VIEW_BEFORE_SYNC", REVIT_APPLICATION.get_uidoc().ActiveView.Name)
    set_active_view_by_name("EnneadTab Quick Sync")

def switch_from_sync_draft_view():
    last_view_name = envvars.get_pyrevit_env_var("LAST_VIEW_BEFORE_SYNC")
    if not last_view_name:
        return

    set_active_view_by_name(last_view_name)

    for open_ui_view in REVIT_APPLICATION.get_uidoc().GetOpenUIViews():
        open_view = DOC.GetElement(open_ui_view.ViewId)

        if open_view.Name == "EnneadTab Quick Sync":
            open_ui_view.Close()




def get_view_title(view):
    return view.Parameter[DB.BuiltInParameter.VIEW_DESCRIPTION].AsString()

def set_view_title(view, title):
    view.Parameter[DB.BuiltInParameter.VIEW_DESCRIPTION].Set(title)

def get_detail_number(view):
    return view.Parameter[DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER].AsString()

def set_detail_number(view, detail_number):
    view.Parameter[DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER].Set(detail_number)