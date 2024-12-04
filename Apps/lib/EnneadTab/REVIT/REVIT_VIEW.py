# -*- coding: utf-8 -*-

import ENVIRONMENT, NOTIFICATION, DATA_FILE, ERROR_HANDLE
from pyrevit.coreutils import envvars
import REVIT_SELECTION
import traceback


try:
    from Autodesk.Revit import DB #pyright: ignore
    import REVIT_APPLICATION  # Level 2: Import our module

    DOC = REVIT_APPLICATION.get_doc()


        
except Exception as e:
    globals()["DOC"] = None
    ERROR_HANDLE.print_note("REVIT_VIEW.py: Failed to import modules")
    ERROR_HANDLE.print_note(traceback.format_exc())

def get_view_by_name( view_name, doc = DOC):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
    
    for view in all_views:
        if view.Name == view_name:
            return view
    return None


def create_drafting_view(doc, view_name, scale = 1):
    view = DB.ViewDrafting.Create(doc, 
                                  get_default_view_type("drafting").Id)
    view.Name = view_name
    view.Scale = scale
    return view


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


def view_ids_to_views(elements, doc=DOC):
    if not hasattr(doc, "GetElement"): return []
    
    elements = list(elements) # in case the input were NET LIST from filterelementcollector
    if not isinstance(elements, list): elements = [elements]
    if not elements: return []
    return list(map(lambda x: doc.GetElement(x), elements))

def filter_archi_views(views):
    out = []
    for view in views:
        if view is None:
            continue
        if not isinstance(view, DB.View):
            continue
        if view.IsTemplate:
            continue
        if view.ViewType.ToString() in ["Legend", "Schedule"]:
            continue
        out.append(view)
    return out



class ViewFilter:
    def __init__(self, views_or_view_ids = None, doc=DOC):
        
        self.doc = doc
        if views_or_view_ids is None:
            views_or_view_ids = list(DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements())
        if len(views_or_view_ids) == 0: 
            self.views = []
            return
        if isinstance(views_or_view_ids[0], DB.ElementId):
            self.views = view_ids_to_views(views_or_view_ids, doc)
        else:
            self.views = views_or_view_ids

    def filter_archi_views(self):
        self.views = filter_archi_views(self.views)
        return self

    def filter_non_template_views(self):
        self.views = filter(lambda x: not x.IsTemplate, self.views)
        return self
    
    def to_view_ids(self):
        return list(map(lambda x: x.Id, self.views))

    def to_views(self):
        return self.views

    def to_count(self):
        return len(self.views)


def set_active_view_by_name(view_name, doc = DOC):

    view = get_view_by_name(view_name, doc)
    if view:
        set_active_view(view, doc)
    else:
        NOTIFICATION.messenger("<{}> does not exist...".format(view_name))

def set_active_view(view, doc = DOC):
    try:
        REVIT_APPLICATION.get_uidoc().ActiveView = view
    except Exception as e:
        NOTIFICATION.messenger(str(e))


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
        if open_view and open_view.Name == "EnneadTab Quick Sync":
            open_ui_view.Close()




def get_view_title(view):
    return view.Parameter[DB.BuiltInParameter.VIEW_DESCRIPTION].AsString()

def set_view_title(view, title):
    view.Parameter[DB.BuiltInParameter.VIEW_DESCRIPTION].Set(title)

def get_detail_number(view):
    return view.Parameter[DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER].AsString()

def set_detail_number(view, detail_number):
    view.Parameter[DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER].Set(detail_number)





"""the resiter of the server happen during startup"""
class GraphicDataItem:

    def __init__(self, location, additional_info = {}, image = None):
        self.location = location
        self.additional_info = additional_info
        self.image = image or "{}\\warning_duck.bmp".format(ENVIRONMENT.IMAGE_FOLDER)

        
def show_in_convas_graphic(graphic_datas, doc = DOC, view = None):
    
    """
    args:
        graphic_datas: list of GraphicDataItem
        doc: revit document
        view: revit view



    note: make it 64x64
    open in MS paint and save as 16 bit color bmp
    background 0,128,128

    if view is not provided, it will show in all views
    """

    if not isinstance(graphic_datas, list):
        graphic_datas = [graphic_datas]


    manager = DB.TemporaryGraphicsManager.GetTemporaryGraphicsManager(doc)
    
    manager.Clear()

    

    temp_data = {}
    for graphic_data_item in graphic_datas:
        location = graphic_data_item.location
        image_path = graphic_data_item.image
        data = DB.InCanvasControlData (image_path, location)

        if not view:
            index = manager.AddControl(data, DB.ElementId.InvalidElementId)
        else:
            index = manager.AddControl(data, view.Id)

        temp_data[index] = {
            "location":[location.X, location.Y, location.Z], 
             "view":view.UniqueId if view else None, 
             "additional_info": graphic_data_item.additional_info
             }

    # should not use shared data record because the index is locally created persession.
    with DATA_FILE.update_data("CANVAS_TEMP_GRAPHIC_DATA_{}.sexyDuck".format(doc.Title), is_local=True) as temp_graphic_data:
        temp_graphic_data.update(temp_data)



def show_warnings_in_view(view, doc):
    # redo inmport becasue the isolated func need structure.....
    # from EnneadTab import NOTIFICATION
    # from EnneadTab.REVIT import REVIT_VIEW
    # from Autodesk.Revit import DB # pyright: ignore 


    all_warnings = doc.GetWarnings()
    all_view_element_ids = DB.FilteredElementCollector(doc, view.Id).ToElementIds()


    description_dict = {}
    for warning in all_warnings:
        for id in warning.GetFailingElements():

            description_dict[id] = warning.GetDescriptionText()
    in_view_bad_element_ids = set(description_dict.keys()).intersection(set(all_view_element_ids))

    if not in_view_bad_element_ids:
        NOTIFICATION.messenger("No warnings in this view!")
        return

    graphic_datas = []
    for element_id in in_view_bad_element_ids:
        element = doc.GetElement(element_id)
        bbox_source_element = element.get_BoundingBox(view)
        bbox_source_center = bbox_source_element.Max - bbox_source_element.Min
        description = description_dict[element_id]
        graphic_datas.append(GraphicDataItem(bbox_source_center, additional_info = {"description": description}))

        
    show_in_convas_graphic(graphic_datas, view = view)
    NOTIFICATION.messenger("Warnings marked!")

def get_link_action_map(link_instance):
    return {"link instance override": link_instance.Id, "link type override": link_instance.Document.GetElement(link_instance.GetTypeId()).Id}


def process_link(doc, mapping_dict, print_link_view_names = False, total_reset = False):
    """sample_mapping_dict = {
    "title": "2151_A_EA_NYULI_Hospital_EXT",
    "level_maps": {
        "level_name_1": "link view name 1",
        "level_name_2": "link view name 2",
    },
    # use view map for more detailed control such as context and phasing
    "view_maps": {
        "my view_1": "link view_1",
        "my view_2": "link view_2",
    },
    # ignore views from host file to prevent modifying
    "ignore_views": [
        "view_name_to_ignore_1", 
        "view_name_to_ignore_2"
        ]
}


    Args:
        doc (_type_): _description_
        mapping_dict (_type_): _description_
        print_link_view_names (bool, optional): _description_. Defaults to False.
        total_reset (bool, optional): Destroy all local overrides, Dangerous. Defaults to False.
    """
    from pyrevit import script
    output = script.get_output()
    # do not process link for self, this makes no sense
    if doc.Title == mapping_dict["title"]:
        return

    
    link_doc = REVIT_SELECTION.get_revit_link_doc_by_name(mapping_dict["title"], doc)
    if not link_doc:
        print ("Link doc [{}] not found".format(mapping_dict["title"]))
        return

    
    if print_link_view_names:
        linked_views = DB.FilteredElementCollector(link_doc).OfCategory(DB.BuiltInCategory.OST_Views).ToElements()
        linked_views = sorted(list(linked_views), key=lambda x: (str(x.ViewType),x.Name))
        for linked_view in linked_views:
            print("{}:[{}] {}".format(link_doc.Title, linked_view.ViewType, linked_view.Name))
        
    link_instance = REVIT_SELECTION.get_revit_link_instance_by_name(link_doc.Title, doc)
    output.print_md("## Processing Link: [{}]".format(link_doc.Title))

    def reset_link_view_overrides(view):
        try:
            map = get_link_action_map(link_instance)
            view.RemoveLinkOverrides  (map["link type override"])
            view.RemoveLinkOverrides  (map["link instance override"])  
        except:
            pass

        
    setting = DB.RevitLinkGraphicsSettings ()
    setting.LinkVisibilityType = DB.LinkVisibility.ByLinkView

    all_views = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Views).ToElements()
    for view in all_views:
        if total_reset:
            reset_link_view_overrides(view)
            continue
        
        # ignore views from host file to prevent modifying
        if view.Name in mapping_dict.get("ignore_views", []):
            continue
        
        # Check view maps first for direct view mapping
        if view.Name in mapping_dict.get("view_maps", {}):
            linked_view_name = mapping_dict["view_maps"][view.Name]
            
        # Otherwise try to map by level
        elif hasattr(view, "GenLevel") and view.GenLevel and \
             view.GenLevel.Name in mapping_dict.get("level_maps", {}):
            linked_view_name = mapping_dict["level_maps"][view.GenLevel.Name]
            
        else:
            continue



        linked_view = get_view_by_name(linked_view_name, doc = link_doc)


        if not linked_view:
            print("Linked view [{}] not found".format(linked_view_name))
            continue
        setting.LinkedViewId = linked_view.Id
        try:
            map = get_link_action_map(link_instance)
            view.SetLinkOverrides (map["link type override"], setting)
            print("Set link view overrides for view [{}] using [{}][{}]".format(output.linkify(view.Id, title=view.Name), link_doc.Title, linked_view.Name))
        except Exception as e:
            print("Error setting link viewoverrides for view [{}]: {}".format(output.linkify(view.Id, title=view.Name), e))


def check_linked_views(doc):
    from pyrevit import script
    output = script.get_output()

    link_instances = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance).ToElements()
    if len(link_instances) == 0:
        print ("No link instances found in the project.")
        return
    
    all_views = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
    count = 0
    def can_support_link_view(view, link_instance):
        """Check if a view has link overrides for a given link instance"""
        try:
            _ = view.GetLinkOverrides(link_instance.Id)
            return True
        except:
            return False



    for view in sorted(all_views, key=lambda x: x.Name):
        if view.IsTemplate:
            continue
        if not can_support_link_view(view, link_instances[0]):
            continue

        for link_instance in link_instances:
            
            for action, action_id in get_link_action_map(link_instance).items():
                link_override_settings = view.GetLinkOverrides(action_id)
        
                if not link_override_settings:
                  
                    continue
                if link_override_settings.LinkVisibilityType == DB.LinkVisibility.ByHostView:
          
                    continue
                elif link_override_settings.LinkVisibilityType == DB.LinkVisibility.ByLinkView:
                    additional_info = ""
                else:
                    additional_info = "(ByLinkView With Custom Settings)"
                linked_doc = link_instance.GetLinkDocument()
                linked_view = linked_doc.GetElement(link_override_settings.LinkedViewId)
                if not linked_view:
                    continue
                print("{}. [{}] has linked view [{}] from [{}]. Setting using [{}] {}".format(count + 1, output.linkify(view.Id, title=view.Name), linked_view.Name, linked_doc.Title, action, additional_info))
                count += 1

    print ("\n\nDone. {} views have linked views.".format(count))

def unit_test():
    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        if not isinstance(DOC, object):
            switch_to_sync_draft_view(DOC)
