from Autodesk.Revit import DB # pyright: ignore
import DATA_CONVERSION

def get_view_filter_by_name(doc, name):
    all_filters = DB.FilteredElementCollector(doc)\
             .OfClass(DB.ParameterFilterElement)\
             .ToElements()
    for filter in all_filters:
        if filter.Name == name:
            return filter
    return None

def add_view_filter_to_view(doc, view_or_template, filter_name):
    view_or_template.AddFilter(get_view_filter_by_name(doc, filter_name).Id)

def set_view_filter_overrides(doc, view_or_template, filter_name, overrides):
    filter = get_view_filter_by_name(doc, filter_name)
    view_or_template.SetFilterOverrides(filter.Id, overrides) 

def create_view_filter(doc, filter_name, categories):
    """categories: list of categories to apply filter to, [OST_xxx, OST_xxx, ...]"""

    categories = [DB.ElementId(x) for x in categories]
    categories = DATA_CONVERSION.list_to_system_list(categories)

    param_filter = DB.ParameterFilterElement.Create(doc, filter_name, categories)

    
    return param_filter 

"""    
    # Rule 1: Exterior walls (just like they did in the circus!)
    exterior_param_id = DB.ElementId(DB.BuiltInParameter.FUNCTION_PARAM)
    filter_rules.append(
        DB.ParameterFilterRuleFactory.CreateEqualsRule(
            exterior_param_id, 
            int(DB.WallFunction.Exterior)
        )
    )
        
        # Rule 2: Wall length > 28.0 (because normal walls are boring!)
        length_param_id = DB.ElementId(DB.BuiltInParameter.CURVE_ELEM_LENGTH)
        filter_rules.append(
            DB.ParameterFilterRuleFactory.CreateGreaterOrEqualRule(
                length_param_id, 
                28.0, 
                0.0001
            )
        )
        
        # Rule 3: Shared parameter check (if exists)
        sp_guid = Guid("96b00b61-7f5a-4f36-a828-5cd07890a02a")  # Same GUID as C# example
        wall = DB.FilteredElementCollector(doc)\
                 .OfClass(DB.Wall)\
                 .FirstElement()
        
        if wall:
            shared_param = wall.get_Parameter(sp_guid)
            if shared_param:
                filter_rules.append(
                    DB.ParameterFilterRuleFactory.CreateBeginsWithRule(
                        shared_param.Id, 
                        "15.", 
                        True
                    )
                )
        
        # Create and set element filter
        elem_filter = DB.LogicalAndFilter(
            [DB.ElementParameterFilter(rule) for rule in filter_rules]
        )
        param_filter.SetElementFilter(elem_filter)
        
        # Apply to view with a surprise - make it hot pink! 
        view.AddFilter(param_filter.Id)
        
        # Create some fun overrides
        override_settings = DB.OverrideGraphicSettings()
        override_settings.SetProjectionLineColor(DB.Color(255, 20, 147))  # Hot pink!
        override_settings.SetProjectionLineWeight(6)  # Extra thick lines
        
        view.SetFilterOverrides(param_filter.Id, override_settings)
        
        t.Commit()
        """