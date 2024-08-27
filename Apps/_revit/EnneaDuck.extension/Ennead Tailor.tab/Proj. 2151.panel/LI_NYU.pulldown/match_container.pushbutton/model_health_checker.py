
from Autodesk.Revit import DB # pyright: ignore 



class ModelHealthChecker:
    def __init__(self, doc):
        self.doc = doc

    def check(self):
        self.check_warnings()
        self.check_in_place_family()


    def check_warnings(self):
        pass

    def check_in_place_family(self):
        all_families = DB.FilteredElementCollector(self.doc).OfClass(DB.Family).ToElements()
        in_place_families = [x for x in all_families if x.IsInPlace]
        if in_place_families:
            print("In-place families found:")
            for family in in_place_families:
                print(family.Name)
     