
from Autodesk.Revit import DB # pyright: ignore 

from data_holder import SentenceDataHolder, ListDataHolder

class ModelHealthChecker:
    def __init__(self, doc):
        self.doc = doc
        self.report = []

    def check(self):
        self.check_warnings()
        self.check_in_place_family()

        for data_holder in self.report:
            data_holder.print_data()


    def check_warnings(self):
        all_warnings = self.doc.GetWarnings()
        self.report.append(SentenceDataHolder("There are {} warnings in [{}]".format(len(all_warnings), self.doc.Title)))
        
        

    def check_in_place_family(self):
        all_families = DB.FilteredElementCollector(self.doc).OfClass(DB.Family).ToElements()
        in_place_family_names = [x.Name for x in all_families if x.IsInPlace]
        if in_place_family_names:
            self.report.append(ListDataHolder(in_place_family_names, title="There are {} in-place families in [{}]".format(len(in_place_family_names), self.doc.Title)))

        
     