#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Batch rename Revit families by replacing '_INT' and '_EXT' suffixes with company suffix.

Key Features:
- Processes all families in the current document
- Handles naming conflicts automatically
- Provides detailed progress feedback
- Logs failed rename operations
"""
__title__ = "Rename All Fam"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ENVIRONMENT, ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def rename_all_fam(doc):
    """Rename all families in the document replacing INT/EXT with company suffix.
    
    Args:
        doc: Current Revit document
        
    Returns:
        None
    """
    failed_log = []
    families = list(DB.FilteredElementCollector(doc).OfClass(DB.Family))
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    for i, family in enumerate(families):
        original_name = family.Name
        new_name = original_name
        
        if "_INT" in original_name:
            new_name = original_name.replace("_INT", "_" + ENVIRONMENT.PLUGIN_ABBR)
        elif "_EXT" in original_name:
            new_name = original_name.replace("_EXT", "_" + ENVIRONMENT.PLUGIN_ABBR)
            
        if new_name != original_name:
            count = 0
            while count < 5:
                try:
                    family.Name = new_name
                    print("{}/{}: {} ---> {}".format(i+1, len(families), original_name, new_name))
                    break
                except Exception as e:
                    count += 1
                    new_name = "{}_{}".format(new_name, count)
            else:
                failed_log.append("Failed to rename {} to {}".format(original_name, new_name))
    t.Commit()
        
    if failed_log:
        print("\nFailed to rename the following families:")
        print("\n".join(failed_log))



################## main code below #####################
if __name__ == "__main__":
    rename_all_fam(DOC)







