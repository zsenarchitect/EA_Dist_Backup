import REVIT_APPLICATION

try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()



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
    definition = schedule_view.Definition
    doc = schedule_view.Document
    for schedulable_field in definition.GetSchedulableFields():
        if schedulable_field.GetName(doc) == name:
            return schedulable_field
    return None

def get_field_by_name(schedule_view, name):
    definition = schedule_view.Definition
    doc = schedule_view.Document
    for index in range(definition.GetFieldCount()):
        field = definition.GetField(index)
        if field.GetName() == name:
            return field
    return None


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
