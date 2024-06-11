from pyrevit import revit, DB


__title__ = "Make hard schedule"
__doc__ = 'make a direct scehdule from data, update/create keyschedule'



#GetValidCategoriesForKeySchedule Method.Gets a list of categories that can be used for a key schedule.


'''
try DB.builtInCategory.OST_xxx and get id
'''
category_id = DB.ElementId(-2001340)# Topogrphic category, no one schedukle this hopefully
with revit.Transaction('Make Hard Schedule'):
    try:
        main_schedule = DB.ViewSchedule.CreateKeySchedule(revit.doc,category_id)
        main_schedule.Name = "Blank S"
        main_schedule.KeyScheduleParameterName = "P"
    except:#this schedule is there already
        main_schedule = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewSchedule).WhereElementIsNotElementType().ToElements()

    for i in range(5):
        main_schedule.GetTableData().GetSectionData(1).InsertRow(1)

'''see exaxmple here:for insertrow action and set setcelltext:
https://www.revitapidocs.com/2015/e14a7a0f-0a5c-c010-7cc2-a83cb1a9da8c.htm
'''

'''
syncgrinize with central method---used to pushback updated score to central
get username
get current score time
smart button to toggle between run score on startup---application class, document opening event
'''
