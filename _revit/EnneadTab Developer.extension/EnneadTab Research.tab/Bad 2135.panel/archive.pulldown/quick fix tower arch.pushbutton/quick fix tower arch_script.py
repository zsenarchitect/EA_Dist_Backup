__doc__ = "DO NOT USE, feature not needed."
__title__ = "quick fix tower arch"

from pyrevit import forms, DB, revit, script



from pyrevit import forms, DB, revit, script

def find_similar_panels(type_id):

    family_name = type_id.split("}:")[0].replace("{","")
    type_name = type_id.split("}:")[1]

    def is_match_panel(x):
        try:
            if family_name == x.Symbol.FamilyName and type_name == x.Symbol.LookupParameter("Type Name").AsString():
                return True
            else:
                return False
        except Exception as e:
            if "has no attribute" in str(e):
                return False
            else:
                print (e)
                print(x.Id)
                return False

    all_panels = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()
    panels = filter(lambda x: is_match_panel(x), all_panels)

    return panels

def find_panel_host_wall_radius(panel):

    radius = panel.Host.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_ARC_RADIUS).AsDouble()
    if radius == 0.0:
        print("Panel {} should be in curved wall.{}".format(panel.Id, output.linkify(panel.Id,title = "Click to zoom to panel")))
        global error_panel_found
        error_panel_found = True

    return radius


################## main code below #####################
output = script.get_output()
output.close_others()

error_panel_found = False

opts = ["{Bili_Flat_Main}:Flat"]

types = opts
"""
types = forms.SelectFromList.show(opts,
                                multiselect = True,
                                button_name='Select Panel Type')
"""


panels = []
for type in types:
    panels.extend(find_similar_panels(type))



with revit.Transaction("quick fix arch"):
    for panel in panels:
        if panel.LookupParameter("#is_bm").AsInteger():
            try:
                panel.LookupParameter("is_arch lower").Set(1)
            except:
                pass

        if panel.LookupParameter("#is_parapet").AsInteger():
            try:
                panel.LookupParameter("is_arch upper").Set(1)
            except:
                pass


        if panel.LookupParameter("#is_arch B").AsInteger():
            if panel.LookupParameter("#is_triface pier casing").AsInteger():
                if panel.LookupParameter("#is_flip casing").AsInteger():
                    try:
                        panel.LookupParameter("is_arch lower").Set(1)
                    except:
                        pass
