__doc__ = "Help you get started with many families by adding many useful parameter quickly."
__title__ = "Family Parameter\nBatch Creation"

from pyrevit import forms, script
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_UNIT, REVIT_APPLICATION
from EnneadTab import SOUND, ERROR_HANDLE, LOG
from Autodesk.Revit import DB # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
import re



class FamilyParameterManager:
    def __init__(self, docs):
        self.docs = docs if isinstance(docs, list) else [docs]
        self.options = ["---End Tool Now---",
                "YesNo--> Yes/No",
                "YesNo--> <Type In><Default False>",
                "YesNo--> <Type In><Default Value><Default Formula>",
                "Length--> <Type In><Default Value>",
                "Length--> Spandrel_H",
                "YesNo--> is_corner",
                "YesNo--> is_top",
                "YesNo--> is_bm",
                "YesNo--> is_operable",
                "YesNo--> is_louver",
                "YesNo--> is_FRW",
                "YesNo--> is_full_clear",
                "YesNo--> is_full_spandrel",
                "YesNo--> is_double_pane_clear",
                "YesNo--> is_double_pane_spandrel",
                "YesNo--> show_mullion_FRW",
                "YesNo--> show_coping",
                "YesNo--> show_backpan",
                "YesNo--> show_louver",
                "YesNo--> show_glass_vision",
                "YesNo--> show_glass_spandrel",
                "YesNo--> show_railing",
                "YesNo--> show_mullion_spandrel"]
        
    def add_parameter(self, name, para_type, tooltip="", default_value=None, default_formula=""):
        """Generic method to add parameters to family documents"""
        for doc in self.docs:
            family_manager = doc.FamilyManager
            
            try:
                # Handle 2023+ API changes
                try:
                    para_group = DB.BuiltInParameterGroup.PG_GENERAL
                    parameter_type = DB.ParameterType.YesNo if para_type == "YesNo" else DB.ParameterType.Length
                except:
                    para_group = DB.GroupTypeId.General
                    parameter_type = REVIT_UNIT.lookup_unit_spec_id(para_type.lower())

                t = DB.Transaction(doc, "Add parameter")
                t.Start()
                
                para = family_manager.AddParameter(name, para_group, parameter_type, True)
                
                if default_value is not None:
                    try:
                        family_manager.Set(para, default_value)
                    except:
                        print("Cannot set default value")
                        
                if default_formula:
                    try:
                        family_manager.SetFormula(para, default_formula)
                    except:
                        print("Cannot set formula")
                        
                family_manager.SetDescription(para, tooltip)
                
                log_msg = "\n<{}> added as {} parameter in [{}]".format(
                    name, para_type, doc.Title
                )
                if default_value is not None:
                    log_msg += ", default as {}".format(default_value)
                if default_formula:
                    log_msg += ", formula as {}".format(default_formula)
                print(log_msg)
                
                t.Commit()
                
            except Exception as e:
                REVIT_FORMS.dialogue(
                    main_text="<{}> parameter cannot be created because {}.".format(name, e)
                )

    def add_yes_no(self):
        """Add standard yes/no parameters"""
        self.add_parameter("no", "YesNo", 
                          tooltip="You can use this in your formula:\nif(condition,yes,no)",
                          default_value=False, 
                          default_formula="1>2")
        self.add_parameter("yes", "YesNo",
                          tooltip="You can use this in your formula:\nif(condition,yes,no)",
                          default_value=False,
                          default_formula="not(no)")

    def pick_para(self):
        """Let user pick parameter type and handle creation"""
        sel = forms.SelectFromList.show(self.options,
                                    multiselect = False,
                                    title = "Let's do those action to the family.",
                                    button_name= "Let's go!"
                                    )

        if sel == None or sel == self.options[0]:
            return False

        self.process_selection(sel)
        SOUND.play_sound("sound_effect_popup_msg3.wav")
        return True

    def process_selection(self, selection):
        """Process the selected parameter type and create it"""
        para_name = selection.split("--> ")[-1]
        para_type = selection.split("--> ")[0]

        if para_type == "YesNo":
            if "Yes/No" in para_name:
                self.add_yes_no()
                return True

            if "<Type In><Default False>" in para_name:
                template_string = "Type in para name here."
                user_input = forms.ask_for_string(
                    default=template_string, 
                    prompt="Type below the name of the parameter\nleave it blank if you want to exit.", 
                    title="Name and default value of the parameter", 
                    width=1000
                )
                if not user_input or user_input == "":
                    return False
                self.add_parameter(user_input, "YesNo", default_value=False)
                return True

            if "<Type In><Default Value><Default Formula>" in para_name:
                template_string = "<Para><True/False><No_Formula>"
                while True:
                    user_input = forms.ask_for_string(
                        default=template_string, 
                        prompt="Type below the name of the parameter\nleave it blank if you want to exit.", 
                        title="Name, default T/F and formula of the parameter", 
                        width=1000
                    )
                    if not user_input or user_input == "":
                        return False
                    try:
                        match = re.search(r"<(.+)><(.+)><(.+)>", user_input)
                        para_name, default_value, default_formula = match.group(1), match.group(2), match.group(3)
                        if default_value not in ["True", "False"]:
                            REVIT_FORMS.dialogue(main_text="Default_Value need to be either 'True' or 'False'")
                            continue
                        default_value = default_value == "True"
                        if default_formula == "No_Formula":
                            default_formula = ""
                        break
                    except Exception as e:
                        print(str(e))

                self.add_parameter(para_name, "YesNo", 
                                          default_value=default_value, 
                                          default_formula=default_formula)
                return True

            # Default YesNo parameter
            self.add_parameter(para_name, "YesNo", default_value=False)
            return True

        elif para_type == "Length":
            if "<Type In><Default Value>" in para_name:
                template_string = "<Para><Default_Length_in_Ft>"
                while True:
                    user_input = forms.ask_for_string(
                        default=template_string, 
                        prompt="Type below the name of the parameter,\nleave it blank if you want to exit.", 
                        title="Name and default length of the parameter", 
                        width=1000
                    )
                    if not user_input or user_input == "":
                        return False
                    try:
                        match = re.search(r"<(.+)><(.+)>", user_input)
                        para_name, default_value = match.group(1), float(match.group(2))
                        break
                    except Exception as e:
                        print(str(e))

                self.add_parameter(para_name, "Length", default_value=default_value)
                return True

            # Default Length parameter
            self.add_parameter(para_name, "Length", default_value=1)
            return True

        return True

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def create_paras():
    working_docs = REVIT_APPLICATION.select_family_docs(select_multiple=True, including_current_doc=True)
    if not working_docs:
        return
        
    print("Working on those families:")
    for doc in working_docs:
        print("- " + doc.Title)
    print("#"*50)
    
    param_manager = FamilyParameterManager(working_docs)
    while True:
        if not param_manager.pick_para():
            SOUND.play_sound("sound_effect_popup_msg3.wav")
            return

################## main code below #####################
output = script.get_output()
output.close_others()
if __name__ == "__main__":
    create_paras()
