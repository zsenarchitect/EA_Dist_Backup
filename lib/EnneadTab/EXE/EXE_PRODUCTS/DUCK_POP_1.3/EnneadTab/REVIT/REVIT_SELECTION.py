#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    import sys
    import os
    import DATA_CONVERSION
    from Autodesk.Revit import DB
    from Autodesk.Revit import UI
    uidoc = __revit__.ActiveUIDocument
    
    import REVIT_APPLICATION

except:
    pass

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


def pick_linestyle(doc, filledregion_friendly=False):
    from pyrevit import forms
    if filledregion_friendly:
        all_linestyles = [doc.GetElement(x) for x in DB.FilledRegion.GetValidLineStyleIdsForFilledRegion (doc)]
    else:
        all_linestyles = get_all_linestyles(doc, return_name=False)
    res = forms.SelectFromList.show(all_linestyles,
                                    name_attr='Name',
                                    title="Pick Line Style",
                                    multiselect = False)
    return res

def get_linestyle(doc, linestyle_name):
    line_category = doc.Settings.Categories.get_Item(
        DB.BuiltInCategory.OST_Lines)
    line_subcs = line_category.SubCategories
    for line_style in line_subcs:
        # print line_style.Name
        if line_style.Name == linestyle_name:
            return line_style.GetGraphicsStyle(DB.GraphicsStyleType.Projection)
    return None


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

def get_solid_fill_pattern(doc, return_id = False):
    fill_patterns = DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement).WhereElementIsNotElementType().ToElements()
    for fill_pattern in fill_patterns:
        if fill_pattern.GetFillPattern().IsSolidFill:
            if return_id:
                return fill_pattern.Id
            return fill_pattern
    return None

def get_solid_fill_pattern_id(doc):
    return get_solid_fill_pattern(doc, return_id = True)

def get_filledregion_type(doc, type_name):
    types = DB.FilteredElementCollector(doc).OfClass(
        DB.FilledRegionType).ToElements()
    for type in types:
        if type.LookupParameter("Type Name").AsString() == type_name:
            return type
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
    for workset in get_all_userworkset(doc):
        if workset.Name == name:
            return workset


def get_all_userworkset(doc):

    all_worksets = DB.FilteredWorksetCollector(doc).ToWorksets()
    user_worksets = [x for x in all_worksets if x.Kind.ToString()
                     == "UserWorkset"]
    user_worksets.sort(key=lambda x: x.Name)
    return user_worksets


def get_all_phase(doc):
    all_phase_ids = DB.FilteredElementCollector(
        doc).OfClass(DB.Phase).ToElementIds()
    return sorted([doc.GetElement(phase_id) for phase_id in all_phase_ids], key=lambda x: x.Name)


def get_phase_by_name(doc, phase_name=None):
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


def pick_family(doc):

    families = DB.FilteredElementCollector(doc).OfClass(
        DB.Family).WhereElementIsNotElementType().ToElements()
    families = sorted(families, key=lambda x: x.Name.lower())

    from pyrevit import forms
    family = forms.SelectFromList.show(families,
                                       multiselect=False,
                                       name_attr='Name',
                                       width=1000,
                                       title="Pick family",
                                       button_name='Select Family')
    return family


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


def pick_system_type(doc, system_type, type_name=None):
    if system_type == "floor":
        type = DB.BuiltInCategory.OST_Floors

    types = DB.FilteredElementCollector(doc).OfCategory(
        type).WhereElementIsElementType().ToElements()

    types = sorted(types, key=lambda x: x.Name)
    if type_name:
        return [x for x in types if x.Name == type_name][0]

    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{}".format(self.Name)
    types = [MyOption(x) for x in types]
    my_type = forms.SelectFromList.show(types,
                                        multiselect=False,

                                        width=1000,
                                        title="Pick type from {}".format(
                                            system_type),
                                        button_name='Select Type')
    return my_type



def pick_shared_para_definition(doc):
    from pyrevit import forms
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{} : {} ({})".format(self.item[0], \
                                        self.item[1].Name, \
                                        self.item[1].ParameterType)


    shared_para_file = doc.Application.OpenSharedParameterFile()
    options = []
    for definition_group in shared_para_file.Groups:
        #print "*"*10
        #print definition_group.Name
        for definition in definition_group.Definitions:

            options.append(MyOption((definition_group.Name, definition)))


    options.sort(key = lambda x:x.name)
    sel = forms.SelectFromList.show(options,
                                    multiselect = False,
                                    title = "Pick shared parameter.",
                                    button_name= "Let's go!"
                                    )
    if not sel:
        return None
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

    doc = uidoc.Document
    objs = uidoc.Selection.PickObjects(UI.Selection.ObjectType.Element, prompt)
    objs = [doc.GetElement(x) for x in objs]
    return objs


def pick_subelements(prompt='Pick SubElements'):

    doc = uidoc.Document
    sub_objs = uidoc.Selection.PickObjects(
        UI.Selection.ObjectType.Subelement, prompt)
    sub_objs = [doc.GetElement(x) for x in sub_objs]
    return sub_objs


def get_selection():

    selection_ids = uidoc.Selection.GetElementIds()
    selection = [doc.GetElement(x) for x in selection_ids]
    return selection


def set_selection(elements):
    if not isinstance(elements, list):
        elements = [elements]

    uidoc.Selection.SetElementIds(
        DATA_CONVERSION.list_to_system_list([x.Id for x in elements]))


def zoom_selection(elements):
    if isinstance(elements, list):
        elements = DATA_CONVERSION.list_to_system_list(
            [x.Id for x in elements])

    uidoc.ShowElements(elements)
    set_selection(elements)


def get_tooltip_info(doc, element):
    info = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, element.Id)
    return "Created by : {}\nLast Edit by: {}\nCurrently owned by: {}".format(info.Creator, info.LastChangedBy, info.Owner)
    # return info.Creator, info.LastChangedBy , info.Owner

def is_changable(x):
    current_owner = x.LookupParameter("Edited by").AsString()
    #print current_owner
    if current_owner == "":
        return True
    if current_owner == x.Document.Application.Username:
        return True
    #print "not changeable"
    return False

def filter_elements_changable(elements):
    return filter(is_changable, elements)


def get_export_setting(doc, setting_name=None, return_name=False):

    def pick_from_setting():
        from pyrevit import forms

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
