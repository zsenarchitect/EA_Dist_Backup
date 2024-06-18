
from pyrevit import EXEC_PARAMS


"""
this hook conlflict with rank family tool
"""
#IMPERIAL or METRIC
doc = EXEC_PARAMS.event_args.Document

if doc.IsFamilyDocument:

    from pyrevit import forms,DB,script
    output = script.get_output()
    output.self_destruct(5)

    output.print_md("#work in progress to convert imperial and metric when new fa ily doucment create so we only need one template for the office.\n#this will close in 5 seconds")

    print("This is family doc.")
    print(doc.DisplayUnitSystem)
    current_unit = DB.Units( DB.UnitSystem.Metric )
    #print DB.Units.GetDisplayUnitType()  this method is missing from API
    print(DB.Units.GetFormatOptions(current_unit, DB.UnitType.UT_Length).DisplayUnits)
    print(DB.Units.GetFormatOptions(current_unit, DB.UnitType.UT_Area).DisplayUnits)

    #new_format =
    #DB.Units.SetFormatOptions(current_unit, DB.UnitType.UT_Length).


    print(doc.DisplayUnitSystem)
