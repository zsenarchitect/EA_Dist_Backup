__doc__ = "Load many shared parameter into current family document."
__title__ = "Batch Load\nShared Para"

from pyrevit import forms, DB, revit, script


def add_para(para):

    para_name = para.Name
    para_group = DB.BuiltInParameterGroup.PG_ADSK_MODEL_PROPERTIES
    para_type = para.ParameterType
    is_instance_sel = forms.alert(msg = "Add '{}' as instance or type parameter?".format(para_name), options = ["Instance", "Type"])
    is_instance = True if is_instance_sel == "Instance" else False
    try:
        para = family_manager.AddParameter(para_name,\
                                        para_group,\
                                        para_type,\
                                        is_instance)
    except:
        forms.alert("There is a '{}' parameter already. Skipping creating same parameter name.".format(para_name))

class MyOption(forms.TemplateListItem):
    @property
    def name(self):
        return "{} : {} ({})".format(self.item[0], \
                                    self.item[1].Name, \
                                    self.item[1].ParameterType)




################## main code below #####################
if __name__ == "__main__":
    
    if revit.doc.IsFamilyDocument != True:
        forms.alert("This tool is only appliable when you are in family document.")
        script.exit()
    #print revit.doc.Title
    family_manager = revit.doc.FamilyManager
    #print family_manager

    output = script.get_output()
    output.close_others()
    shared_para_file = revit.doc.Application.OpenSharedParameterFile()
    options = []
    for definition_group in shared_para_file.Groups:
        #print "*"*10
        #print definition_group.Name
        for definition in definition_group.Definitions:
            '''
            print "\t{} -- {} -- {}".format(definition.Name, \
                                        definition.ParameterType, \
                                        definition.UnitType)
            '''
            options.append(MyOption((definition_group.Name, definition)))



    sels = forms.SelectFromList.show(options,
                                    multiselect=True,
                                    title = "Let's do those action to the family.",
                                    button_name= "Let's go!"
                                    )

    if sels == None:
        script.exit()
    with revit.Transaction("Add parameter"):

        for sel in sels:
            #para_name = sel.split("--> ")[-1]
            #para_type = sel.split("--> ")[0]
            #add_para(para_name, para_type, "")
            add_para(sel[1])



