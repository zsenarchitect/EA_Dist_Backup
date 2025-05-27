import REVIT_APPLICATION
import ERROR_HANDLE
try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()

import DATA_CONVERSION

def create_schedule(doc, schedule_name, field_names, built_in_category, is_itemized = False, is_filtered_by_sheet = True):
    view = DB.ViewSchedule.CreateSchedule(doc, 
                                          DB.Category.GetCategory(doc, built_in_category).Id)   
    view.Name = schedule_name
    definition = view.Definition

    for field_name in field_names:
        field = get_schedulable_field_by_name(view, field_name)
        if field is None:
            print("Field [{}] not found".format(field_name))
            continue
        definition.AddField(field)

    definition.IsItemized = is_itemized
    definition.IsFilteredBySheet = is_filtered_by_sheet

    return view

def get_schedulable_field_by_name(schedule_view, name):
    """get possible field, but nessaryly added to this schedule"""
    definition = schedule_view.Definition
    doc = schedule_view.Document
    for schedulable_field in definition.GetSchedulableFields():
        if schedulable_field.GetName(doc) == name:
            return schedulable_field
    return None

def get_field_by_name(schedule_view, name):
    """get added field by name"""
    definition = schedule_view.Definition
    doc = schedule_view.Document
    for index in range(definition.GetFieldCount()):
        field = definition.GetField(index)
        if field.GetName() == name:
            return field
    return None

def hide_fields_in_schedule(schedule_view, field_name_or_names):
    if isinstance(field_name_or_names, str):
        field_name_or_names = [field_name_or_names]
    for field_name in field_name_or_names:
        field = get_field_by_name(schedule_view, field_name)
        if field is None:
            print("Field [{}] not found".format(field_name))
            continue
        if "calc_" in field_name.lower():
            print ("calc_ keyword found in field name [{}], this will be preserved.".format(field_name))
            field.IsHidden = False
            continue
        field.IsHidden = True

def add_fields_to_schedule(schedule_view, field_names):
    """Add fields to schedule if they are not already added.
    
    Args:
        schedule_view (DB.ViewSchedule): The schedule view to add fields to
        field_names (list): List of field names to add
    """
    definition = schedule_view.Definition
    
    for field_name in field_names:
        field = get_schedulable_field_by_name(schedule_view, field_name)
        if field is None:
            print("Field [{}] not found".format(field_name))
            continue
            
        try:
            definition.AddField(field)
            print("Adding field [{}] to schedule".format(field_name))
        except Exception as e:
            continue
            print("cannot add field [{}] to schedule because [{}]".format(field_name, e))

def sort_fields_in_schedule(schedule_view, field_names):
    # Sort fields and format double type fields
    field_ids = []
    for para_name in field_names:
        field = get_field_by_name(schedule_view, para_name)
        if field:
            field_ids.append(field.FieldId)

    if field_ids:
        schedule_view.Definition.SetFieldOrder(DATA_CONVERSION.list_to_system_list(field_ids, 
                                                                                   type=DB.ScheduleFieldId, 
                                                                                   use_IList=False))
def set_group_order(schedule_view, field_name, descending = True):
    sort_group_field = DB.ScheduleSortGroupField()
    sort_group_field.FieldId = get_field_by_name(schedule_view, field_name).FieldId
    sort_group_field.SortOrder = DB.ScheduleSortOrder.Descending if descending else DB.ScheduleSortOrder.Ascending
    schedule_view.Definition.SetSortGroupFields(DATA_CONVERSION.list_to_system_list([sort_group_field], type=DB.ScheduleSortGroupField, use_IList=False))


def add_filter_to_schedule(schedule_view, field_name, filter_type, filter_value):
    field = get_field_by_name(schedule_view, field_name)
    if field is None:
        print("Field [{}] not found".format(field_name))
        return

    schedule_filter = DB.ScheduleFilter(field.FieldId, filter_type, filter_value)
    schedule_view.Definition.AddFilter(schedule_filter)
    return
    schedule_filter = DB.ScheduleFilter()
    schedule_filter.FieldId = field.FieldId
    schedule_filter.FilterType = filter_type
    if isinstance(filter_value, DB.ElementId):
        schedule_filter.SetValue.OverLoads[DB.ElementId](filter_value)
    elif isinstance(filter_value, str):
        schedule_filter.SetValue.OverLoads[str](filter_value)
    elif isinstance(filter_value, int):
        schedule_filter.SetValue.OverLoads[int](filter_value)
    elif isinstance(filter_value, float):
        schedule_filter.SetValue.OverLoads[float](filter_value)
    else:
        print("Unsupported filter value type: {}".format(type(filter_value)))
        return
    print(schedule_filter)
    # definition.AddFilter(schedule_filter)

def format_numeric_fields(schedule_view, field_names, rounding_value=10):
    """Format numeric fields in a schedule with consistent formatting.
    
    Args:
        schedule_view (DB.ViewSchedule): The schedule view to format
        field_names (list): List of field names to format
        rounding_value (int, optional): Value to round to. Defaults to 10.
    """
    definition = schedule_view.Definition
    for index in range(definition.GetFieldCount()):
        field = definition.GetField(index)
        if field.GetName() in field_names:
            try:
                # Get format options
                format_options = field.GetFormatOptions()
                
                # Set rounding to nearest value
                format_options.RoundingMethod = DB.RoundingMethod.RoundToNearest
                format_options.RoundingValue = rounding_value
                
                # Enable digit grouping
                format_options.UseDigitGrouping = True
                
                # Set alignment to right
                style = field.GetStyle()
                style.HorizontalAlignment = DB.HorizontalAlignment.Right
                
                # Apply the format options
                field.SetFormatOptions(format_options)
            except Exception as e:
                ERROR_HANDLE.print_note("Cannot format field [{}] as numeric: {}".format(field.GetName(), str(e)))
                continue

def shade_cells_by_field(schedule_view, color_dict):
    """Shade cells in a schedule based on field names and colors.
    
    Args:
        schedule_view (DB.ViewSchedule): The schedule view to format
        color_dict (dict): Dictionary mapping field names to color tuples (R,G,B)
                          Example: {"GSF": (200,200,200), "BEDS": (150,150,150)}
    """
    definition = schedule_view.Definition
    for index in range(definition.GetFieldCount()):
        field = definition.GetField(index)
        field_name = field.GetName()
        
        if field_name in color_dict:
            try:
                # Get the color tuple for this field
                r, g, b = color_dict[field_name]
                
                # Get style and override options
                style = field.GetStyle()
                override_options = style.GetCellStyleOverrideOptions()
                
                # Enable background color override
                override_options.BackgroundColor = True
                
                # Set the background color
                style.BackgroundColor = DB.Color(r, g, b)
                
            except Exception as e:
                ERROR_HANDLE.print_note("Cannot shade field [{}]: {}".format(field_name, str(e)))
                continue
