from update_parking_data_script import FAMILY_DATA

from EnneadTab.REVIT import REVIT_TAG
from Autodesk.Revit import DB # pyright: ignore

def manage_parking_tags(doc, show_log = False):
    good_host_family_names = FAMILY_DATA.keys()

    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    all_parking_families = [x for x in all_families if x.FamilyCategory.Name == "Parking"]
    bad_host_family_names = [x.Name for x in all_parking_families if x.Name not in good_host_family_names]
    if show_log:
        print ("bad host family names: {}".format(bad_host_family_names))


    t = DB.Transaction(doc, "Manage Parking Tags")
    t.Start()
    REVIT_TAG.purge_tags(bad_host_family_names, tag_category=DB.BuiltInCategory.OST_ParkingTags, doc=doc)
    t.Commit()

