__doc__ = "Help you get started with a new family by adding many useful parameter quickly."
__title__ = "Family Parameter\nCreation In Current Family"

from pyrevit import forms, DB, revit, script

def ft_to_mm(dist):
    return (dist/3.28084)*1000
def mm_to_ft(dist):
    return (dist/1000)*3.28084

def add_yes_no():

    para_name = "no"
    para_group = DB.BuiltInParameterGroup.PG_GENERAL
    para_type = DB.ParameterType.YesNo
    is_instance = False
    try:
        para = family_manager.AddParameter(para_name,\
                                        para_group,\
                                        para_type,\
                                        is_instance)

        family_manager.SetFormula(para, "1>2")
        family_manager.SetDescription(para, "You can use this in your formula:\nif(condition,yes,no)")
    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))


    para_name = "yes"
    para_group = DB.BuiltInParameterGroup.PG_GENERAL
    para_type = DB.ParameterType.YesNo
    is_instance = False
    try:
        para = family_manager.AddParameter(para_name,\
                                    para_group,\
                                    para_type,\
                                    is_instance)

        family_manager.SetFormula(para, None)
        family_manager.SetFormula(para, "not(no)")
        family_manager.SetDescription(para, "You can use this in your formula:\nif(condition,yes,no)")
    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))

def add_tower_podium():

    para_name = "is_tower"
    para_group = DB.BuiltInParameterGroup.PG_GENERAL
    para_type = DB.ParameterType.YesNo
    is_instance = True
    try:
        para = family_manager.AddParameter(para_name,\
                                        para_group,\
                                        para_type,\
                                        is_instance)



    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))


    para_name = "is_podium"
    para_group = DB.BuiltInParameterGroup.PG_GENERAL
    para_type = DB.ParameterType.YesNo
    is_instance = True
    try:
        para = family_manager.AddParameter(para_name,\
                                    para_group,\
                                    para_type,\
                                    is_instance)

        family_manager.SetFormula(para, None)
        family_manager.SetFormula(para, "not(is_tower)")

    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))

def add_content_background():

    para_name = "show_content"
    para_group = DB.BuiltInParameterGroup.PG_GENERAL
    para_type = DB.ParameterType.YesNo
    is_instance = False
    try:
        para = family_manager.AddParameter(para_name,\
                                        para_group,\
                                        para_type,\
                                        is_instance)



    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))


    para_name = "show_background"
    para_group = DB.BuiltInParameterGroup.PG_GENERAL
    para_type = DB.ParameterType.YesNo
    is_instance = False
    try:
        para = family_manager.AddParameter(para_name,\
                                    para_group,\
                                    para_type,\
                                    is_instance)

        family_manager.SetFormula(para, None)
        family_manager.SetFormula(para, "not(show_content)")

    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))

def add_show_IGU():

    para_name = "show_IGU glass_desire"
    para_group = DB.BuiltInParameterGroup.PG_GENERAL
    para_type = DB.ParameterType.YesNo
    is_instance = True
    try:
        para = family_manager.AddParameter(para_name,\
                                        para_group,\
                                        para_type,\
                                        is_instance)



    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))


    family_manager.Set(para, True)

    para_name = "show_IGU glass_act"
    para_group = DB.BuiltInParameterGroup.PG_GENERAL
    para_type = DB.ParameterType.YesNo
    is_instance = True
    try:
        para = family_manager.AddParameter(para_name,\
                                        para_group,\
                                        para_type,\
                                        is_instance)



    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))



    family_manager.SetFormula(para, "and(show_content, show_IGU glass_desire)")


def add_yes_no_type_para(name, tooltip):

    para_name = name
    para_group = DB.BuiltInParameterGroup.PG_VISIBILITY
    para_type = DB.ParameterType.YesNo
    is_instance = True


    try:
        para = family_manager.AddParameter(para_name,\
                                        para_group,\
                                        para_type,\
                                        is_instance)
        try:
            family_manager.Set(para, False)
        except:
            pass
        family_manager.SetDescription(para, tooltip)
    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))

def add_dim_type_para(name, tooltip):

    para_name = name
    para_group = DB.BuiltInParameterGroup.PG_ADSK_MODEL_PROPERTIES
    para_type = DB.ParameterType.Length
    is_instance = True
    try:
        para = family_manager.AddParameter(para_name,\
                                        para_group,\
                                        para_type,\
                                        is_instance)
        family_manager.Set(para, mm_to_ft(1500))
        family_manager.SetDescription(para, tooltip)
    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))






################## main code below #####################
if revit.doc.IsFamilyDocument != True:
    forms.alert("This tool is only appliable when you are in family document.")
    script.exit()
#print revit.doc.Title
family_manager = revit.doc.FamilyManager
#print family_manager


options = ["YesNo--> Yes/No",\
            "YesNo(Multiple)--> As Type In",\
            "YesNo--> ##placeholder1",\
            "YesNo--> ##placeholder2",\
            "YesNo--> ##placeholder3",\
            "YesNo--> is_terminal panel_start",\
            "YesNo--> is_terminal panel_end",\
            "YesNo--> is_corner",\
            "YesNo--> is_top",\
            "YesNo--> is_bm",\
            "YesNo--> is_terrace",\
            "YesNo--> is_ground",\
            "YesNo--> is_operable",\
            "YesNo--> is_tower/podium",\
            "YesNo--> is_louver",\
            "YesNo--> is_louver upper",\
            "YesNo--> is_louver lower",\
            "YesNo--> is_FRW",\
            "YesNo--> is_full clear",\
            "YesNo--> is_double pane clear",\
            "YesNo--> is_double pane spandrel",\
            "YesNo--> is_full spandrel",\
            "YesNo--> is_door",\
            "YesNo--> is_louver lower",\
            "YesNo--> is_louver upper",\
            "YesNo--> show_mullion FRW",\
            "YesNo--> show_coping",\
            "YesNo--> show_backpan",\
            "YesNo--> show_louver",\
            "YesNo--> show_glass vision",\
            "YesNo--> show_glass spandrel",\
            "YesNo--> show_railing",\
            "YesNo--> show_mullion spandrel",\
            "YesNo--> show_content/background",\
            "YesNo--> show_IGU glass desire/act",\
            "Length--> Geo_L_desired",\
            "Length--> Geo_L_act",\
            "Length--> FRW mullion_H",\
            "Length--> Spandrel_H"]

sels = forms.SelectFromList.show(options,
                                multiselect=True,
                                title = "Let's do those action to the family.",
                                button_name= "Let's go!"
                                )

if sels == None:
    script.exit()
with revit.Transaction("Add parameter"):

    for sel in sels:
        para_name = sel.split("--> ")[-1]
        para_type = sel.split("--> ")[0]
        if para_type == "YesNo":
            if "Yes/No" in para_name:
                add_yes_no()

            elif "is_top" in para_name:
                add_yes_no_type_para(para_name,"You can use this to mark a top conditon such as parapet.")

            elif "is_corner" in para_name:
                add_yes_no_type_para(para_name, "You can use this to mark a corner conditon and trigger corner void trim.")

            elif "is_tower/podium" in para_name:
                add_tower_podium()

            elif "show_content/background" in para_name:
                add_content_background()
            elif "show_IGU glass" in para_name:
                add_show_IGU()
            else:
                add_yes_no_type_para(para_name,"")


        elif para_type == "Length":
            add_dim_type_para(para_name,"")

        elif para_type == "YesNo(Multiple)":
            while True:
                para_name = forms.ask_for_string(prompt="Type below the name of the parameter,\nleave it blank if you want to exit", title="Name of the parameter")
                if len(para_name) == 0:
                    break
                add_yes_no_type_para(para_name,"")
        else:
            pass
