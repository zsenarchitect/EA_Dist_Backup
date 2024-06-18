__doc__ = "Help you get started with a new family by adding many subCategories quickly."
__title__ = "Family SubC\nCreation"
"""
Family panel

Assign element by creating subC
From sample list xxx_vison glass then ask for prefix. This can be sequenced multiple creation.
Or manual input completely.
Or by existing
"""

from pyrevit import forms, DB, revit, script
import EA_UTILITY
import EnneadTab


def create_subC(subC_name):

    if "<keep typing>" == subC_name.lower():
        while True:
            new_subc = forms.ask_for_string(prompt = "Keep typing and creating subC. Leave empty to exit tool.", default = "XXX")
            if new_subc == "":
                break
            create_subC(new_subc)




    try:
        revit.doc.Settings.Categories.NewSubcategory(_ParentCategory, subC_name)
        success_list.append(subC_name)
    except:
        EA_UTILITY.dialogue(main_text = "SubCategory '{}' exists in this family.".format(subC_name))
################## main code below #####################
if __name__ == "__main__":
    if revit.doc.IsFamilyDocument != True:
        EA_UTILITY.dialogue(main_text = "This tool is only appliable when you are in family document.")
        script.exit()




    subC_name_prefix = forms.ask_for_string( default = "SubC Name Prefix", prompt = "[SubC Name Prefix]_[Selected SubCategory]\nPrefix can be used to distinct seperated buildings on same plot.\nDelete text or leave as default to NOT add prefix.", title = "Add a prefix?")

    options_raw = ["<Keep Typing>",\
                "$$2Dtl_Center line",\
                "$$2Dtl_Center line_grey",\
                "$$2Dtl_Cut but not profile",\
                "$$2Dtl_Hidden",\
                "$$2Dtl_Profile Exterior",\
                "$$2Dtl_Profile Interior",\
                "$$2Dtl_See but important",\
                "$$2Dtl_See but not important",\
                "$$2Dtl_WaterProof",\
                "$$2Dtl_Steel Frame Center",\
                "$$2Dtl_Ceiling Finish",\
                "$$2Dtl_Column Precut_Inner",\
                "$$2Dtl_Column Precut_Outter",\
                "$$2Dtl_Slab",\
                "$$2Dtl_Wall",\
                "$$2Dtl_Beam",\
                "Glass Vision",\
                "Glass Spandrel",\
                "Mullion V.",\
                "Mullion V. Cap",\
                "Mullion H.",\
                "Mullion Header",\
                "Mullion Spandrel",\
                "Mullion Sill",\
                "Mullion Silicon",\
                "Mullion FRW",\
                "Railing",\
                "Swing Symbolic",\
                "Backpan",\
                "Insulation",\
                "Spandrel Cover",\
                "Coping",\
                "Louver Blade",\
                "Canopy",\
                "Louver Coarse Display",\
                "FRW Symbol",\
                "Pier"]
    if subC_name_prefix in [None, "", "SubC Name Prefix"]:
        options = options_raw
    else:
        options = ["{}_{}".format(subC_name_prefix, x) for x in options_raw]

    sels = forms.SelectFromList.show(options,
                                    multiselect=True,
                                    title = "Let's add those subC to the family.",
                                    button_name= "Let's go!",
                                    height = 800
                                    )

    if sels == None:
        script.exit()


    with revit.Transaction("Add subCs"):
        _ParentCategory = revit.doc.OwnerFamily.FamilyCategory
        success_list = []
        for sel in sels:
            create_subC(sel)
        if len(success_list) > 0:
            sub_msg = ""
            for name in success_list:
                sub_msg += "\t{}\n".format(name)
            EA_UTILITY.dialogue(main_text = "Those SubCategories have been added to your family.", sub_text = sub_msg)
