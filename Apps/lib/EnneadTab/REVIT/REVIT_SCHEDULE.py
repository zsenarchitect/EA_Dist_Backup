import REVIT_APPLICATION
import ERROR_HANDLE
import DATA_CONVERSION
import traceback
try:
    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()

def create_schedule(doc, schedule_name, field_names, built_in_category, is_itemized=False, is_filtered_by_sheet=True):
    """Create a new schedule view.
    
    Args:
        doc (DB.Document): Revit document
        schedule_name (str): Name of the schedule
        field_names (list): List of field names to include
        built_in_category (DB.BuiltInCategory): Category for the schedule
        is_itemized (bool, optional): Whether to itemize. Defaults to False
        is_filtered_by_sheet (bool, optional): Whether to filter by sheet. Defaults to True
    
    Returns:
        DB.ViewSchedule: Created schedule view
    """
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
    """Get possible field, but not necessarily added to this schedule.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
        name (str): Field name to find
    
    Returns:
        DB.SchedulableField: Found field or None
    """
    definition = schedule_view.Definition
    doc = schedule_view.Document
    for schedulable_field in definition.GetSchedulableFields():
        if schedulable_field.GetName(doc) == name:
            return schedulable_field
    return None

def get_field_by_name(schedule_view, name):
    """Get added field by name.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
        name (str): Field name to find
    
    Returns:
        DB.ScheduleField: Found field or None
    """
    definition = schedule_view.Definition
    for index in range(definition.GetFieldCount()):
        field = definition.GetField(index)
        if field.GetName() == name:
            return field
    return None

def hide_fields_in_schedule(schedule_view, field_name_or_names):
    """Hide specified fields in schedule.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
        field_name_or_names (str|list): Field name(s) to hide
    """
    if isinstance(field_name_or_names, str):
        field_name_or_names = [field_name_or_names]
    for field_name in field_name_or_names:
        field = get_field_by_name(schedule_view, field_name)
        if field is None:
            print("Field [{}] not found".format(field_name))
            continue
        if "calc_" in field_name.lower():
            print("calc_ keyword found in field name [{}], this will be preserved.".format(field_name))
            field.IsHidden = False
            continue
        field.IsHidden = True

def add_fields_to_schedule(schedule_view, field_names):
    """Add fields to schedule if they are not already added.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
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

def sort_fields_in_schedule(schedule_view, field_names):
    """Sort fields in schedule by specified order.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
        field_names (list): List of field names in desired order
    """
    field_ids = []
    for para_name in field_names:
        field = get_field_by_name(schedule_view, para_name)
        if field:
            field_ids.append(field.FieldId)

    if field_ids:
        schedule_view.Definition.SetFieldOrder(DATA_CONVERSION.list_to_system_list(field_ids, 
                                                                                   type=DB.ScheduleFieldId, 
                                                                                   use_IList=False))

def set_group_order(schedule_view, field_name, descending=True):
    """Set group order for schedule.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
        field_name (str): Field name to group by
        descending (bool, optional): Sort order. Defaults to True
    """
    sort_group_field = DB.ScheduleSortGroupField()
    sort_group_field.FieldId = get_field_by_name(schedule_view, field_name).FieldId
    sort_group_field.SortOrder = DB.ScheduleSortOrder.Descending if descending else DB.ScheduleSortOrder.Ascending
    schedule_view.Definition.SetSortGroupFields(DATA_CONVERSION.list_to_system_list([sort_group_field], 
                                                                                    type=DB.ScheduleSortGroupField, 
                                                                                    use_IList=False))

def add_filter_to_schedule(schedule_view, field_name, filter_type, filter_value):
    """Add filter to schedule.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
        field_name (str): Field name to filter
        filter_type (DB.ScheduleFilterType): Type of filter
        filter_value: Value to filter by
    """
    field = get_field_by_name(schedule_view, field_name)
    if field is None:
        print("Field [{}] not found".format(field_name))
        return

    schedule_filter = DB.ScheduleFilter(field.FieldId, filter_type, filter_value)
    schedule_view.Definition.AddFilter(schedule_filter)

def format_numeric_fields(schedule_view, field_names, rounding_value=10):
    """Format numeric fields in schedule.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
        field_names (list): List of field names to format
        rounding_value (int, optional): Rounding value. Defaults to 10
    """
    definition = schedule_view.Definition
    for field_name in field_names:
        field = get_field_by_name(schedule_view, field_name)
        if field is None:
            print("Field [{}] not found".format(field_name))
            continue
        try:
            # Always set right alignment regardless of unit type
            style = field.GetStyle()
            override_options = style.GetCellStyleOverrideOptions()
            override_options.HorizontalAlignment = DB.HorizontalAlign.Right
            style.SetCellStyleOverrideOptions(override_options)
            field.SetStyle(style)
        except Exception as e:
            ERROR_HANDLE.print_note("Cannot set horizontal alignment for field [{}]".format(field_name))
            ERROR_HANDLE.print_note(traceback.format_exc())
            continue


        try:
            # Get the field's spec type
            spec_type = field.GetSpecTypeId()
            
            # Format if field has a spec type (numeric or area)
            if spec_type:
                format_options = DB.FormatOptions()
                format_options.UseDefault = False
                format_options.Accuracy = rounding_value
                format_options.UseDigitGrouping = True
                format_options.RoundingMethod = DB.RoundingMethod.Nearest
                
                # Get valid display units for this field type
                unit_type = DB.UnitUtils.GetUnitType(spec_type)
                valid_units = DB.UnitUtils.GetValidDisplayUnits(unit_type)
                
                # For area fields, use square feet
                if unit_type == DB.UnitType.UT_Area:
                    format_options.DisplayUnits = DB.DisplayUnitType.DUT_SQUARE_FEET
                elif valid_units:
                    # For other numeric fields, use the first valid display unit
                    format_options.DisplayUnits = valid_units[0]
                
                field.SetFormatOptions(format_options)
                
        except Exception as e:
            continue

def shade_cells_by_field(schedule_view, color_dict):
    """Shade cells in schedule based on field names and colors.
    
    Args:
        schedule_view (DB.ViewSchedule): Schedule view
        color_dict (dict): Dictionary mapping field names to color tuples (R,G,B)
    """
    definition = schedule_view.Definition
    for index in range(definition.GetFieldCount()):
        field = definition.GetField(index)
        field_name = field.GetName()
        
        if field_name in color_dict:
            try:
                r, g, b = color_dict[field_name]
                style = field.GetStyle()
                override_options = style.GetCellStyleOverrideOptions()
                override_options.BackgroundColor = True
                style.BackgroundColor = DB.Color(r, g, b)
                style.SetCellStyleOverrideOptions(override_options)
                field.SetStyle(style)
            except Exception as e:
                ERROR_HANDLE.print_note("Cannot shade field [{}]: {}".format(field_name, str(e)))
                continue
