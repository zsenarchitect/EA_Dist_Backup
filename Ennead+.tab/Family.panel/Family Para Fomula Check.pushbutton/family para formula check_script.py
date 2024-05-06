__doc__ = "Help you check if a to-be-deleted parameter is being used in any formula."
__title__ = "Family Parameter\nUsage Check"

from pyrevit import forms, script
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
doc = __revit__.ActiveUIDocument.Document


def check_label(my_para):
    # get all dimensions

    dims = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Dimensions).WhereElementIsNotElementType().ToElements()


    # filter dimens with family label that match para
    dims = filter(lambda x: x.FamilyLabel is not None, dims)
    dims = filter(lambda x: x.FamilyLabel.Definition.Name == my_para.Definition.Name, dims)

    if len(dims) == 0:
        return "not used"


    # list all ops and print linkify to label

    class label_option(forms.TemplateListItem):
        @property
        def name(self):
            return "Dim Label [{}] = {}".format(self.item.FamilyLabel.Definition.Name, self.item.ValueString)

    dims = [label_option(x) for x in dims]

    sels = forms.SelectFromList.show(dims,
                                    multiselect = True,
                                    button_name = 'Selected Dims',
                                    title = "Dimension label that used parameter [{}], it might include partial-string.".format(my_para.Definition.Name),
                                    width = 1200)

    if sels is None:
        return "no selection"

    print("\n\nInspecting dimension label for [{}]".format(my_para.Definition.Name))
    for dim in sels:

        print("\t\tDimension ---> {}".format(output.linkify(dim.Id, title = "Go To Element")))

    return "checked"

def check_formula(my_para):

    #all_formulas_data = get_all_formulas()
    used_formula = []
    for para in doc.FamilyManager.Parameters:
        if para.Formula is None:
            continue
        if my_para.Definition.Name in para.Formula:
            used_formula.append(para)



    class formula_option(forms.TemplateListItem):
        @property
        def name(self):
            return "Parameter [{}] = {}".format(self.item.Definition.Name, self.item.Formula)

    if len(used_formula) == 0:
        return  "not used"

    used_formula = [formula_option(x) for x in used_formula]
    sels = forms.SelectFromList.show(used_formula,
                                    multiselect = True,
                                    button_name = 'Edit selected formula',
                                    title = "formulas that used parameter [{}], it might include partial-string.".format(my_para.Definition.Name),
                                    width = 1200)

    if sels is None:
        return "no selection"

    t = DB.Transaction(doc, "fix formula")
    t.Start()
    for para in sels:
        for i in range(5):
            new_formula = forms.ask_for_string(default = para.Formula, prompt = "Edit below for para [{}], attamp #{}. Or accept as-it to avoid modifying".format(my_para.Definition.Name, i + 1), width = 1200)
            try:
                doc.FamilyManager.SetFormula(para, new_formula)
                break
            except:
                EA_UTILITY.dialogue(main_text = "Formula is invalid.\n{} attemps remain".format(5 - (i + 1) ))
    t.Commit()

    return "checked"

def check_link_para(my_para):


    class linked_para_option(forms.TemplateListItem):
        @property
        def name(self):
            #print my_para.Definition.Name + "*********" + str(self.item.Element)
            if isinstance(self.item.Element, DB.GeomCombination):
                ##print "A"
                elements = self.item.Element.AllMembers
                types = set()
                for item in elements:
                    types.add( item.GetType())
                return "Family Element[{}]'s parameter: {}".format(list(types), self.item.Definition.Name)
            if isinstance(self.item.Element, DB.FamilyInstance):
                #print "B"
                return "Family Instance[{}]'s parameter: {}".format(self.item.Element.Symbol.FamilyName, self.item.Definition.Name)
            #print "C"
            return "Family Element[{}]'s parameter: {}".format(self.item.Element.GetType(), self.item.Definition.Name)





    linked_paras = [linked_para_option(x) for x in my_para.AssociatedParameters]
    if len(linked_paras) == 0:
        return "not used"
    sels = forms.SelectFromList.show(linked_paras,
                                    multiselect = True,
                                    button_name = 'Inspect associated parameters',
                                    width = 1200,
                                    title = "Other element parameter that used [{}]".format(my_para.Definition.Name))
    if sels is None:
        return "no selection"

    print("\n\nInspecting associated parameters for [{}]".format(my_para.Definition.Name))
    for para in sels:
        if isinstance(para.Element, DB.FamilyInstance):
            print("\t\tFamily Instance [{}] , associated parameter = [{}] ---> {}".format(para.Element.Symbol.FamilyName,
                                                                                        para.Definition.Name,
                                                                                        output.linkify(para.Element.Id, title = "Go To Element")))
        else:
            print("\t\tFamily Element [{}] , associated parameter = [{}] ---> {}".format(para.Element.GetType(),
                                                                                        para.Definition.Name,
                                                                                        output.linkify(para.Element.Id, title = "Go To Element")))
    return "checked"



def process_para(my_para):

    if check_link_para(my_para) == "not used" and check_label(my_para) == "not used" and check_formula(my_para) == "not used":
        print("Parameter [{}] not in use by formula or other elements or dimension labels".format(my_para.Definition.Name))
################## main code below #####################
output = script.get_output()
output.close_others()
if __name__ == "__main__":

    if doc.IsFamilyDocument != True:
        forms.alert("This tool is only appliable when you are in family document.")
        script.exit()
    #print revit.doc.Title
    family_manager = doc.FamilyManager
    #print family_manager

    paras = list(family_manager.Parameters)
    paras.sort(key = lambda x: x.Definition.Name)
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "[{}] {}".format(self.item.Definition.ParameterType, self.item.Definition.Name)
    ops = [MyOption(x) for x in paras]

    sels = forms.SelectFromList.show(ops,
                                    title = "inspect parameters",
                                    multiselect = True,
                                    button_name = 'Select para')
    if sels == None:
        script.exit()

    for para in sels:
        process_para(para)
