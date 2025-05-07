#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Load family from linked revit file without open those links. Non-editable families (in-place and system) will be skipped."
__title__ = "Load Family\nFrom Link"
__tip__ = True
__is_popular__ = True
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, UI
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_FAMILY, REVIT_APPLICATION
from pyrevit.revit import ErrorSwallower
from collections import defaultdict
from Autodesk.Revit.DB import CategoryType, BuiltInCategory

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def load_family_from_link():
    link_doc = REVIT_SELECTION.pick_revit_link_docs(select_multiple=False)
    if not link_doc:
        return

    families = REVIT_SELECTION.pick_family(link_doc, 
                                         multi_select=True)
    if not families:
        return

    # Track skipped families and their reasons
    skipped_families = defaultdict(list)

    def get_system_family_type(family):
        """Get detailed system family type information."""
        if not family.FamilyCategory:
            return "Unknown"
            
        category_name = family.FamilyCategory.Name
        if category_name == "Walls":
            if hasattr(family, "Kind"):
                return "Wall ({})".format(family.Kind)
            return "Wall"
        elif category_name == "Floors":
            return "Floor"
        elif category_name == "Roofs":
            if hasattr(family, "FamilyName"):
                return "Roof ({})".format(family.FamilyName)
            return "Roof"
        elif "Column" in category_name:
            return "Column"
        elif category_name == "Stairs":
            return "Stair"
        return "System Family ({})".format(category_name)

    def loader(family, doc):
        try:
            with ErrorSwallower() as swallower:
                # Check if family is editable
                if not family.IsEditable:
                    reason = "Non-editable"
                    if family.IsInPlace:
                        reason = "In-place family"
                    elif family.FamilyCategory.CategoryType == CategoryType.Model:
                        reason = get_system_family_type(family)
                    skipped_families[reason].append(family.Name)
                    print("Skipping {}: {}".format(reason.lower(), family.Name))
                    return
                    
                family_doc = link_doc.EditFamily(family)
                REVIT_FAMILY.load_family(family_doc, doc)
                family_doc.Close(False)
        except Exception as e:
            skipped_families["Error"].append("{}: {}".format(family.Name, str(e)))
            print("Failed to load family {}: {}".format(family.Name, str(e)))

            
    UI.progress_bar(families, 
                    lambda x:loader(x, DOC), 
                    label_func=lambda x: "Loading Family [{}]".format(x.Name), 
                    title="Loading Families")

    # Print summary of skipped families
    if skipped_families:
        print("\n=== Skipped Families Summary ===")
        for reason, names in skipped_families.items():
            print("\n{}:".format(reason))
            for name in sorted(names):
                print("  - {}".format(name))


################## main code below #####################
if __name__ == "__main__":
    load_family_from_link()







