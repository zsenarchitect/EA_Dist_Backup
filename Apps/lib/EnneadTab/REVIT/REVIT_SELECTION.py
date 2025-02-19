#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import DATA_CONVERSION #pyright: ignore
import NOTIFICATION #pyright: ignore
import REVIT_APPLICATION, REVIT_CATEGORY
try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()

    from pyrevit import forms
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()


DETAIL_FAMILY_PLACEMENT_TYPES = [
    DB.FamilyPlacementType.ViewBased,
    DB.FamilyPlacementType.CurveBasedDetail
    ]

def pick_linestyle(doc, filledregion_friendly=False, return_style=False,title="Pick Line Style"):
    from pyrevit import forms
    if filledregion_friendly:
        all_linestyles = [doc.GetElement(x) for x in DB.FilledRegion.GetValidLineStyleIdsForFilledRegion (doc)]
    else:
        all_linestyles = get_all_linestyles(doc, return_name=False)

    # if doc.IsFamilyDocument:
    #     for cate in doc.Settings.Categories:
    
    #         if cate.Name == "Detail Items":
    #             break
    #     all_linestyles.append(cate)
    #     all_linestyles.extend(list(cate.SubCategories ))
    #-----> cannot set in family doc, so abodon this method

        
    res = forms.SelectFromList.show(all_linestyles,
                                    name_attr='Name',
                                    title=title,
                                    multiselect = False)
    
    # return style can be used to set detail curve
    if return_style:
        return res.GetGraphicsStyle(DB.GraphicsStyleType.Projection)
    
    # return as category, this will not be able to use to set detail curve, but good for setting filled region border
    return res

def get_linestyle(doc, linestyle_name, creation_data_if_not_exsit=None):
    line_category = doc.Settings.Categories.get_Item(
        DB.BuiltInCategory.OST_Lines)
    line_subcs = line_category.SubCategories
    for line_style in line_subcs:
        # print line_style.Name
        if line_style.Name == linestyle_name:
            return line_style.GetGraphicsStyle(DB.GraphicsStyleType.Projection)

    if creation_data_if_not_exsit:
        create_linestyle(linestyle_name, 
                         doc, 
                         creation_data_if_not_exsit)
        return get_linestyle(doc, linestyle_name)
    return None

def create_linestyle(linestyle_name, doc=DOC, creation_data=None):
    """_summary_

    Args:
        linestyle_name (_type_): _description_
        doc (_type_, optional): _description_. Defaults to DOC.
        creation_data (dict, optional): something like {"line_weight": int, "color":(int, int, int)}. Defaults to None.
    """
    if not creation_data:
        # i want to allow partial definition of new style, do not define anything here
        creation_data = dict()

    line_weight = creation_data.get("line_weight", 5)
    color = creation_data.get("color", (255,0,0))

    line_category = doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    can_transaction=not doc.IsModifiable
    if can_transaction:
        
        t = DB.Transaction(doc, "Make new LineStyle")
        t.Start()
    new_linestyle_category = doc.Settings.Categories.NewSubcategory(line_category, linestyle_name)
    new_linestyle_category.SetLineWeight( line_weight, DB.GraphicsStyleType.Projection )
    new_linestyle_category.LineColor = DB.Color(color[0],
                                                color[1],
                                                color[2])

    solid_pattern_id = DB.LinePatternElement.GetSolidPatternId()
    new_linestyle_category.SetLinePatternId(solid_pattern_id,DB.GraphicsStyleType.Projection )
    if can_transaction:
        t.Commit()
  


def get_all_linestyles(doc, return_name=True):
    line_category = doc.Settings.Categories.get_Item(
        DB.BuiltInCategory.OST_Lines)
    line_subcs = line_category.SubCategories
    if return_name:
        names = [x.Name for x in line_subcs]
        names.sort()
        return names
    line_subcs = list(line_subcs)
    line_subcs.sort(key=lambda x: x.Name)
    return line_subcs

def get_solid_fill_pattern(doc = DOC, return_id = False):
    fill_patterns = DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement).WhereElementIsNotElementType().ToElements()
    for fill_pattern in fill_patterns:
        if fill_pattern.GetFillPattern().IsSolidFill:
            if return_id:
                return fill_pattern.Id
            return fill_pattern
    return None

def get_solid_fill_pattern_id(doc = DOC):
    return get_solid_fill_pattern(doc, return_id = True)

def get_filledregion_type(doc, type_name, color_if_not_exist = None):
    """
    color_if_not_exist: if not exist, create a new one with this color tuple (r,g,b)
    """
    types = DB.FilteredElementCollector(doc).OfClass(
        DB.FilledRegionType).ToElements()
    for type in types:
        if type.LookupParameter("Type Name").AsString() == type_name:
            return type
    if color_if_not_exist:
        new_type = type.Duplicate(type_name)
        new_type.ForegroundPatternColor = DB.Color(color_if_not_exist[0], color_if_not_exist[1], color_if_not_exist[2])
        new_type.ForegroundPatternId = get_solid_fill_pattern_id(doc)
        return new_type
    return None


def get_all_filledregion_types(doc, return_name=True):
    types = DB.FilteredElementCollector(doc).OfClass(
        DB.FilledRegionType).ToElements()
    if return_name:
        names = [x.LookupParameter("Type Name").AsString() for x in types]
        names.sort()
        return names
    types = list(types)
    types.sort(key=lambda x: x.LookupParameter("Type Name").AsString())
    return types


def get_all_textnote_types(doc=DOC, return_name=True):

    types = DB.FilteredElementCollector(doc).OfClass(
        DB.TextNoteType).ToElements()
    if return_name:
        names = [x.LookupParameter("Type Name").AsString() for x in types]
        names.sort()
        return names
    types = list(types)
    types.sort(key=lambda x: x.LookupParameter("Type Name").AsString())
    return types

def get_subc(doc, subc_name, in_cate=None):
    """
    in_cate = Detail Items,
    """
    for subc in get_all_subcs(doc, in_cate):
        if subc.Name == subc_name:
            return subc
    return None


def get_all_subcs(doc, in_cate=None):
    OUT = []
    for cate in doc.Settings.Categories:
        if in_cate and cate.Name not in in_cate:
            continue
        for subc in cate.SubCategories:
            OUT.append(subc)
    return OUT


def get_detail_groups_by_name(doc, group_name):
    all_groups = DB.FilteredElementCollector(doc).OfClass(
        DB.Group).WhereElementIsNotElementType().ToElements()

    def is_good_type(x):
        if not x.GroupType:
            return False

        if x.GroupType.LookupParameter("Type Name").AsString() == group_name:
            return True
        return False
    groups = filter(is_good_type, all_groups)
    return groups


def get_workset_by_name(doc, name):
    """to-do: inherate from REVIT_WORKSET, but keep this func"""
    for workset in get_all_userworkset(doc):
        if workset.Name == name:
            return workset


def get_all_userworkset(doc):
    """to-do: inherate from REVIT_WORKSET, but keep this func"""
    all_worksets = DB.FilteredWorksetCollector(doc).ToWorksets()
    user_worksets = [x for x in all_worksets if x.Kind.ToString()
                     == "UserWorkset"]
    user_worksets.sort(key=lambda x: x.Name)
    return user_worksets


def get_all_phase(doc):
    all_phase_ids = DB.FilteredElementCollector(
        doc).OfClass(DB.Phase).ToElementIds()
    return sorted([doc.GetElement(phase_id) for phase_id in all_phase_ids], key=lambda x: x.Name)


def get_phase_by_name(doc=DOC, phase_name=None):
    if phase_name is not None:
        for phase in get_all_phase(doc):
            if phase.Name == phase_name:
                return phase

    all_phases = get_all_phase(doc)
    if len(all_phases) == 1:
        return all_phases[0]

    selected = forms.SelectFromList.show(all_phases,
                                         multiselect=False,
                                         name_attr='Name',
                                         title="Pick a phase to process.",
                                         button_name='Select Phase to Inspect')
    return selected


def get_rooms_in_phase(doc, phase):

    phase_provider = DB.ParameterValueProvider(
        DB.ElementId(DB.BuiltInParameter.ROOM_PHASE))
    phase_rule = DB.FilterElementIdRule(
        phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WherePasses(
        phase_filter).WhereElementIsNotElementType().ToElements()
    return all_rooms


def pick_family(doc=DOC, multi_select = False, include_2D = True, include_3D = True, exclude_categories = []):

    families = DB.FilteredElementCollector(doc).OfClass(
        DB.Family).WhereElementIsNotElementType().ToElements()


    if include_2D and include_3D:
        pass
    elif not include_2D and not include_3D:
        raise ValueError("At least one of include_2D or include_3D must be True")
    elif include_2D:
        families = [x for x in families if x.FamilyPlacementType in DETAIL_FAMILY_PLACEMENT_TYPES]
    elif include_3D:
        families = [x for x in families if x.FamilyPlacementType not in DETAIL_FAMILY_PLACEMENT_TYPES]
        
    from pyrevit import forms
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            if hasattr(self, "FamilyCategory") and self.FamilyCategory :
                return "[{}] {}".format(self.FamilyCategory.Name, self.Name)
            else:
                print (self.item)
                return self.Name

    families = [f for f in families if f.FamilyCategory.Name not in exclude_categories]
    families = [MyOption(x) for x in families]
    families = sorted(families, key=lambda x: x.name)
    family = forms.SelectFromList.show(families,
                                       multiselect=multi_select,
                                       width=1000,
                                       title="Pick family",
                                       button_name='Select Family')
    return family


def pick_detail_componenet(doc = None, multi_select = False):
    doc = doc or DOC
    
    detail_componenet_types = DB.FilteredElementCollector(doc).OfCategory(
        DB.BuiltInCategory.OST_DetailComponents).WhereElementIsElementType().ToElements()
    def is_2d_family(_type):
        if hasattr(_type, "Family") and _type.Family.FamilyPlacementType in DETAIL_FAMILY_PLACEMENT_TYPES:
            return True
        return False
    familie_names = [x.FamilyName for x in detail_componenet_types if x.FamilyName != "Filled region" and is_2d_family(x)]
    familie_names = list(set(familie_names))  # remove duplicates
    familie_names.sort()
    from pyrevit import forms
    selected_names = forms.SelectFromList.show(familie_names,
                                       multiselect=multi_select,
                                       width=600,
                                       title="Pick 2D family",
                                       button_name='Select Family(s)')
    if not selected_names:
        return []
    families = DB.FilteredElementCollector(doc).OfClass(
        DB.Family).WhereElementIsNotElementType().ToElements()
    return [x for x in families if x.Name in selected_names]


def pick_type(family):

    if len(family.GetFamilySymbolIds()) == 0:
        return []
    from pyrevit import forms
    doc = family.Document
    types = [doc.GetElement(x) for x in family.GetFamilySymbolIds()]
    types = sorted(types, key=lambda x: x.LookupParameter(
        "Type Name").AsString())

    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{}".format(self.LookupParameter("Type Name").AsString())
    types = [MyOption(x) for x in types]
    my_type = forms.SelectFromList.show(types,
                                        multiselect=False,
                                        name_attr='Name',
                                        width=1000,
                                        title="Pick type from family {}".format(
                                            family.Name),
                                        button_name='Select Type')
    return my_type


def pick_system_type(doc, system_type, type_name=None, select_multiple = False):
    if system_type == "floor":
        type = DB.BuiltInCategory.OST_Floors
    elif system_type == "wall":
        type = DB.BuiltInCategory.OST_Walls
    elif system_type == "roof":
        type = DB.BuiltInCategory.OST_Roofs


    types = DB.FilteredElementCollector(doc).OfCategory(
        type).WhereElementIsElementType().ToElements()

    def get_name(x):
        try:
            return x.LookupParameter("Type Name").AsString()
        except:
            return x.Name

    types = sorted(types, key=get_name)
    if type_name:
        return [x for x in types if get_name(x) == type_name][0]

    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{}".format(get_name(self.item))
    types = [MyOption(x) for x in types]
    my_type = forms.SelectFromList.show(types,
                                        multiselect=select_multiple,

                                        width=1000,
                                        title="Pick type from {}".format(
                                            system_type),
                                        button_name='Select Type')
    return my_type

def pick_system_types(doc, system_type):
    return pick_system_type(doc, system_type, select_multiple=True)

def pick_wall_types(doc):
    all_wall_types = DB.FilteredElementCollector(doc).\
        OfCategory(DB.BuiltInCategory.OST_Walls).\
        WhereElementIsElementType().ToElements()

    class MyListItem(forms.SelectFromList.ListItem):
        def __init__(self, item):
            self.item = item
            self.name = item.LookupParameter("Type Name").AsString()

    

    return forms.SelectFromList.show([MyListItem(x) for x in all_wall_types], 
                                     multi_select=True)

def pick_shared_para_definition(doc, select_multiple = False):
    from pyrevit import forms
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            try:
                return "{} : {} ({})".format(self.item[0], \
                                            self.item[1].Name, \
                                            self.item[1].ParameterType) 
            except:
                import REVIT_UNIT #pyright: ignore
                return "{} : {} ({})".format(self.item[0], \
                            self.item[1].Name, \
                            REVIT_UNIT.get_unit_spec_name(self.item[1].GetDataType()))


    shared_para_file = doc.Application.OpenSharedParameterFile()
    if not shared_para_file:
        NOTIFICATION.messenger(main_text="There is no shared parameter file found.")
        return None
    options = []
    for definition_group in shared_para_file.Groups:
        for definition in definition_group.Definitions:

            options.append(MyOption((definition_group.Name, definition)))


    options.sort(key = lambda x:x.name)
    
    sel = forms.SelectFromList.show(options,
                                    multiselect = select_multiple,
                                    title = "Pick shared parameter.",
                                    button_name= "Let's go!"
                                    )
    if not sel:
        return None
 
    
    # options in sleection list is a tuple of (definition_group.Name, definition), so return only the good definition object
    if select_multiple:
        return [x[1] for x in sel]
    else:
        return sel[1]


def pick_revit_link_docs(select_multiple = True, 
                         including_current_doc = False, 
                         link_only = True):
    """warpper for older selection method

    Args:
        select_multiple (bool, optional): _description_. Defaults to True.
        including_current_doc (bool, optional): _description_. Defaults to False.
        link_only (bool, optional): _description_. Defaults to True.

    Returns:
        list of revit link docs: _description_
    """
    return REVIT_APPLICATION.select_revit_link_docs(select_multiple = select_multiple, 
                                                    including_current_doc = including_current_doc, 
                                                    link_only = link_only)

def pick_top_level_docs(select_multiple = True):
    """warpper for older pick main docs

    Args:
        select_multiple (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
        
    return REVIT_APPLICATION.select_top_level_docs(select_multiple=select_multiple)


def pick_family_docs(select_multiple = True, 
                     including_current_doc = False):
    """warpper for older pick family docs method

    Args:
        select_multiple (bool, optional): _description_. Defaults to True.
        including_current_doc (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    return REVIT_APPLICATION. select_family_docs(select_multiple = select_multiple, 
                                                 including_current_doc = including_current_doc)



def pick_elements(prompt='Pick Elements'):

    objs = UIDOC.Selection.PickObjects(UI.Selection.ObjectType.Element, prompt)
    objs = [DOC.GetElement(x) for x in objs]
    return objs


def pick_subelements(prompt='Pick SubElements'):

    sub_objs = UIDOC.Selection.PickObjects(
        UI.Selection.ObjectType.Subelement, prompt)
    sub_objs = [DOC.GetElement(x) for x in sub_objs]
    return sub_objs


def pick_textnote_type(doc=None):
    doc = doc or DOC


    from pyrevit import forms
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{}".format(self.LookupParameter("Type Name").AsString())
    types = [MyOption(x) for x in get_all_textnote_types(return_name=False)]
    my_type = forms.SelectFromList.show(types,
                                        multiselect=False,
                                        width=500,
                                        title="Pick TextNote Type",
                                        button_name='Select Type')
    return my_type

def get_selection(uidoc = UIDOC):
    doc = uidoc.Document
    selection_ids = uidoc.Selection.GetElementIds()
    selection = [doc.GetElement(x) for x in selection_ids]
    return selection


def set_selection(elements):
    if not isinstance(elements, list):
        elements = [elements]


    try:
        UIDOC.Selection.SetElementIds(DATA_CONVERSION.list_to_system_list([x.Id for x in elements]))
    except Exception as e:
        
        NOTIFICATION.messenger(main_text=str(e))
        print (e)
        


def zoom_selection(elements):
    if isinstance(elements, list):
        elements = DATA_CONVERSION.list_to_system_list(
            [x.Id for x in elements])

    UIDOC.ShowElements(elements)
    set_selection(elements)


def get_tooltip_info(doc, element):
    info = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, element.Id)
    return "Created by : {}\nLast Edit by: {}\nCurrently owned by: {}".format(info.Creator, info.LastChangedBy, info.Owner)
    # return info.Creator, info.LastChangedBy , info.Owner

def get_owner(x):
    if x.LookupParameter("Edited by"):
        return x.LookupParameter("Edited by").AsString()
    else:
        return ""

def is_changable(x):
    current_owner = get_owner(x)

    #print current_owner
    if current_owner == "":
        return True
    if current_owner.lower() == x.Document.Application.Username.lower():
        return True
    return False

def is_borrowed(x):
    current_owner = get_owner(x)
    return current_owner.lower() == x.Document.Application.Username.lower()
    

def filter_elements_changable(elements):
    return filter(is_changable, elements)

def is_outside_multi_group(element):
    if element.GroupId == DB.ElementId.InvalidElementId:
        return True
    if element.Document.GetElement(element.GroupId).GroupType.Groups.Size <= 1:
        return True
    return False

def filter_elements_outside_muti_group(elements):
    return filter(is_outside_multi_group, elements)

def get_export_setting(doc, setting_name=None, return_name=False):

    def pick_from_setting():
        from pyrevit import forms #pyright: ignore

        attempt = 0
        while True:
            if attempt > 5:
                break
            sel_setting = forms.SelectFromList.show(existing_dwg_settings,
                                                    name_attr="Name",
                                                    button_name='use setting with this name for this export job',
                                                    title="Select existing Export Setting.")
            if sel_setting is None:

                attempt += 1
            else:
                break

        return sel_setting

    existing_dwg_settings = DB.FilteredElementCollector(doc).OfClass(
        DB.ExportDWGSettings).WhereElementIsNotElementType().ToElements()

    if setting_name is None:  # trying to defin the setting for the first time
        sel_setting = pick_from_setting()
        if return_name:
            return sel_setting.Name
        return sel_setting
    else:
        for setting in existing_dwg_settings:
            if setting.Name == setting_name:
                if return_name:
                    return setting.Name
                return setting



def get_level_by_name(level_name, doc = DOC):
    all_levels = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    for level in all_levels:
        if level.Name == level_name:
            return level
    return None


def get_all_instances_of_type(type, active_view_only = False):

    if active_view_only:
        filtered_collector = DB.FilteredElementCollector(DOC, DOC.ActiveView.Id)
    else:
        filtered_collector = DB.FilteredElementCollector(DOC)

    type_filter = DB.FamilyInstanceFilter (DOC, type.Id)


    instances = list(filtered_collector.OfClass(DB.FamilyInstance).WherePasses (type_filter).ToElements())
    
    return instances


def get_panel_location_map(panels):
    """_summary_

    Args:
        panels (_type_): _description_
    
    
    Return:
        dict of panel location index: key:panel.Id, value: (U_index, V_index))
    """
    import clr # pyright: ignore
    
    wall_dict = dict()
    walls = list(set([x.Host for x in panels]))
    for wall in walls:
        temp_dict = {}
        
        temp_dict["u_order"] = [x.IntegerValue for x in wall.CurtainGrid.GetUGridLineIds()]
        temp_dict["v_order"] = [x.IntegerValue for x in wall.CurtainGrid.GetVGridLineIds()]
        wall_dict[wall.Id] = temp_dict
            
    
    panel_location_map = dict()

    for panel in panels:
        
        u_grid_id = clr.StrongBox[DB.ElementId](DB.ElementId(1))
        v_grid_id = clr.StrongBox[DB.ElementId](DB.ElementId(2))
        panel.GetRefGridLines (u_grid_id, v_grid_id)

        
        u_order = wall_dict[panel.Host.Id]["u_order"].index(u_grid_id.IntegerValue) + 1 if u_grid_id.IntegerValue != -1 else 0
        v_order = wall_dict[panel.Host.Id]["v_order"].index(v_grid_id.IntegerValue) + 1 if v_grid_id.IntegerValue != -1 else 0
        
        panel_location_map[panel.Id] = (u_order,v_order)
        
    return panel_location_map

def get_color_scheme_by_name(scheme_name, doc = DOC):
    import REVIT_COLOR_SCHEME #pyright: ignore
    return REVIT_COLOR_SCHEME.get_color_scheme_by_name(scheme_name, doc)

def pick_color_scheme(doc = DOC):
    import REVIT_COLOR_SCHEME #pyright: ignore
    return REVIT_COLOR_SCHEME.pick_color_scheme(doc)

def pick_category(doc=DOC):
    return REVIT_CATEGORY.pick_category(doc=doc)

def get_revit_link_instance_by_name(link_doc_name, doc=DOC):
    link_instances = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance).ToElements()
    for link_instance in link_instances:
        link_doc = link_instance.GetLinkDocument()
        if link_doc and link_doc.Title == link_doc_name:
            return link_instance
    return None


def get_revit_link_doc_by_name(link_doc_name, doc=DOC):
    link_instance = get_revit_link_instance_by_name(link_doc_name, doc)
    if link_instance:
        return link_instance.GetLinkDocument()
    return None

def get_selected_elements(doc=DOC):
    """Retrieves currently selected elements in active view.
    
    Args:
        doc (Document): The Revit document to query. Defaults to active document
        
    Returns:
        list: Collection of selected Element objects
    """
    selection_ids = UIDOC.Selection.GetElementIds()
    selection = [doc.GetElement(x) for x in selection_ids]
    return selection

def get_selected_elements_and_verify(doc=DOC):
    """Retrieves and validates current selection.
    
    Args:
        doc (Document): The Revit document to query. Defaults to active document
        
    Returns:
        list: Collection of selected Element objects
        
    Raises:
        ValueError: If no elements are selected
    """
    selection_ids = UIDOC.Selection.GetElementIds()
    if not selection_ids:
        raise ValueError("No elements selected")
    selection = [DOC.GetElement(x) for x in selection_ids]
    return selection

def filter_elements_changable(elements):
    """Filters elements that can be modified.
    
    Args:
        elements (list): Collection of elements to filter
        
    Returns:
        list: Elements that are not read-only or locked
    """
    return filter(is_changable, elements)

def get_all_text_note_types(doc=DOC, return_name=True):
    """Retrieves all text note types from document.
    
    Args:
        doc (Document): The Revit document to query. Defaults to active document
        return_name (bool): Return names instead of objects. Defaults to True
        
    Returns:
        list: Text note type names or objects based on return_name parameter
    """
    types = DB.FilteredElementCollector(doc).OfClass(
        DB.TextNoteType).ToElements()
    if return_name:
        names = [x.LookupParameter("Type Name").AsString() for x in types]
        names.sort()
        return names
    types = list(types)
    types.sort(key=lambda x: x.LookupParameter("Type Name").AsString())
    return types

def pick_element_by_category(doc, category, message="Select an element"):
    """Prompts user to select an element of specified category.
    
    Args:
        doc (Document): Document to select from
        category (BuiltInCategory): Category to filter selection
        message (str): Prompt message. Defaults to "Select an element"
        
    Returns:
        Element: The selected element, or None if selection canceled
    """
    from pyrevit import forms
    filtered_elements = DB.FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
    if not filtered_elements:
        return None
    selected_element = forms.SelectFromList.show(filtered_elements,
                                              multiselect=False,
                                              width=500,
                                              title=message,
                                              button_name='Select Element')
    return selected_element
