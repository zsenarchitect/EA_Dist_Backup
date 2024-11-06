CALCULATOR_FAMILY_NAME = "Parking Calculator"
DEFAULT_PATH = "{}.rfa".format(CALCULATOR_FAMILY_NAME)
CALCULATOR_DUMP_VIEW_NAME = "EnneadTab_Parking Calculator Dump View"

SCHDEULE_SHEET_NUM = "T-002"
DIVIDER = "##"


import traceback

from EnneadTab.REVIT import REVIT_FAMILY, REVIT_VIEW, REVIT_SHEET, REVIT_PHASE, REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import script


class ParkingCalculator:
    def __init__(self, doc):
        """Initialize the ParkingCalculator with the given document."""
        self.doc = doc
        self.dump_view = REVIT_VIEW.get_view_by_name(CALCULATOR_DUMP_VIEW_NAME, doc=doc)
        if not self.dump_view:            
            self.dump_view = REVIT_VIEW.create_drafting_view(doc, CALCULATOR_DUMP_VIEW_NAME)
        self.calculator_family = REVIT_FAMILY.get_family_by_name(CALCULATOR_FAMILY_NAME, doc=doc, load_path_if_not_exist=DEFAULT_PATH)
        self.parking_families_detected = set()
        self.calculator_type_dict = {}
        self.output = script.get_output()
        self.print_all_doc_phases()

        self.master_phase_list = [x.Name for x in REVIT_PHASE.get_all_phases(self.doc)]
        print ("master phase list: {}".format(self.master_phase_list))
        print ("\n\n")
        REVIT_PHASE.pretty_print_phase_map(self.doc)
    def print_all_doc_phases(self):
        for doc in REVIT_APPLICATION.get_revit_link_docs(including_current_doc=True):
            self.output.print_md("#### doc [{}] has phases: {}".format(doc.Title, [x.Name for x in REVIT_PHASE.get_all_phases(doc)]))

    def update_parking_data(self):
        """Update parking data by processing all phases and calculator types."""
        all_phases = REVIT_PHASE.get_all_phases(self.doc)
        for phase in all_phases:
            self.record_phase(phase.Name)
        self.process_calculator_type_dict()
        self.purge_unused_calculator_types()
        self.print_parking_families_detected()

    def print_parking_families_detected(self):
        self.output.print_md("## Parking families detected:")
        for i, family in enumerate(self.parking_families_detected):
            print("{}. {}".format(i+1, family))

    def is_stall(self, parking_instance):
        family_name = parking_instance.Symbol.FamilyName
        return "stall" in family_name.lower()

    def record_phase(self, phase_name):
        """Record parking instances for a given phase."""
        parking_instances = []
        for doc in REVIT_APPLICATION.get_revit_link_docs(including_current_doc=True):
            self.output.print_md("### Getting parking instances from [{}], phase [{}]".format(doc.Title, phase_name))
            phase = REVIT_PHASE.get_phase_by_name(phase_name, doc=doc)
            if not phase:
                print ("phase [{}] not found in doc [{}], going to use last phase in doc".format(phase_name, doc.Title))
                phase = REVIT_PHASE.get_all_phases(doc)[-1]
                
                
            doc_instances = REVIT_PHASE.get_elements_in_phase(doc, phase, DB.BuiltInCategory.OST_Parking)
            doc_instances = filter(self.is_stall, doc_instances)
            print ("Find {} parking instances in phase [{}] of [{}]".format(len(doc_instances), phase_name, doc.Title))
            parking_instances.extend(doc_instances)

            
        map(lambda x: self.record_parking_instance(x, phase_name), parking_instances)
        self.record_sum_per_phase(phase_name, parking_instances)

    def record_sum_per_phase(self, phase_name, parking_instances):
        """Record the sum of parking instances per phase."""
        calculator_type_name = "Sum Per Phase_{}".format(phase_name)
        
        self.calculator_type_dict[calculator_type_name] = parking_instances

    def record_parking_instance(self, parking_instance, phase_name):
        """Record a single parking instance."""
        family_name = parking_instance.Symbol.FamilyName
        self.parking_families_detected.add(family_name)
        level_name = parking_instance.LookupParameter("ParkingLevel").AsString()
        zone_name = parking_instance.LookupParameter("ParkingZone").AsString()
        if zone_name == "" or zone_name is None:
            zone_name = "zone unknown"

        calculator_type_name = "{phase_name}{divider}{level_name}{divider}{zone_name}".format(phase_name=phase_name, level_name=level_name, zone_name=zone_name, divider=DIVIDER)
        if calculator_type_name not in self.calculator_type_dict:
            self.calculator_type_dict[calculator_type_name] = []
        self.calculator_type_dict[calculator_type_name].append(parking_instance)

    def process_calculator_type_dict(self):
        """Process each calculator type in the dictionary."""
        for calculator_type_name in sorted(self.calculator_type_dict.keys()):
            parking_instances = self.calculator_type_dict[calculator_type_name]
            print("- processing calculator type [{}]".format(calculator_type_name))
            try:
                if "sum" in calculator_type_name.lower():
                    self.process_sum_calculator_type(calculator_type_name, parking_instances)
                    self.check_duplicated_parking_markers(parking_instances)
                else:
                    self.process_regular_calculator_type(calculator_type_name, parking_instances)
            except Exception as e:
                print("--- error processing calculator type [{}]".format(calculator_type_name))
                print(traceback.format_exc())
                print ("\n\n")

    def check_duplicated_parking_markers(self, parking_instances):
        """Check duplicated parking instances with same markers."""
        marker_dict = {}
        for parking_instance in parking_instances:
            if not parking_instance.LookupParameter("ParkingMarker"):
                continue
            marker = parking_instance.LookupParameter("ParkingMarker").AsString()
            if marker in marker_dict:
                marker_dict[marker].append(parking_instance)
            else:
                marker_dict[marker] = [parking_instance]
        for marker in marker_dict:
            if len(marker_dict[marker]) > 1:
                self.output.print_md("<span style='color:red;'>### {} parking instances</span> with conflicting marker [{}] found:".format(len(marker_dict[marker]), marker))
  

    def process_sum_calculator_type(self, calculator_type_name, parking_instances):
        """Process a sum calculator type."""
        phase_name = calculator_type_name.split("_")[1]
        update_para_dict = {
            "Phase": phase_name,
            "Phase Order": self.master_phase_list.index(phase_name),
            "Level": "Total",
            "Zone": "Total Phase",
            "Total Count": len(parking_instances),
            "Standard Count": len(filter(lambda x: not self.is_ada(x), parking_instances)),
            "ADA Count": len(filter(self.is_ada, parking_instances)),
            "User Type": ""
        }
        REVIT_FAMILY.update_family_type(self.doc, CALCULATOR_FAMILY_NAME, calculator_type_name, update_para_dict, show_log=True)
        

    def process_regular_calculator_type(self, calculator_type_name, parking_instances):
        """Process a regular calculator type."""
        calculator_type = REVIT_FAMILY.get_family_type_by_name(CALCULATOR_FAMILY_NAME, calculator_type_name, doc=self.doc, create_if_not_exist=True)
        if not REVIT_SELECTION.is_changable(calculator_type):
            self.output.print_md("###calculator type<span style='color:blue;'> [{}] </span>is not editable, skipped".format(calculator_type_name))
            return
        self.place_parking_calculator_instance(calculator_type)

        user_types = set()
        for parking_instance in parking_instances:
            user_type = parking_instance.LookupParameter("ParkingUser")
            if user_type:
                if user_type.AsString() in ["", None]:
                    user_types.add("Unknown")
                else:
                    user_types.add(user_type.AsString()) 
                           

        update_para_dict = {
            "Phase": calculator_type_name.split(DIVIDER)[0],
            "Phase Order": self.master_phase_list.index(calculator_type_name.split(DIVIDER)[0]),
            "Level": calculator_type_name.split(DIVIDER)[1],
            "Zone": calculator_type_name.split(DIVIDER)[2],
            "Total Count": len(parking_instances),
            "Standard Count": len(filter(lambda x: not self.is_ada(x), parking_instances)),
            "ADA Count": len(filter(self.is_ada, parking_instances)),
            "User Type": "/ ".join(sorted(list(user_types)))
        }
        REVIT_FAMILY.update_family_type(self.doc, CALCULATOR_FAMILY_NAME, calculator_type_name, update_para_dict, show_log=True)

    def purge_unused_calculator_types(self):
        """Purge unused calculator types."""
        self.output.print_md("## Purging unused calculator types")
        delete_count = 0
        for calculator_type in REVIT_FAMILY.get_all_types_by_family_name(CALCULATOR_FAMILY_NAME, self.doc):
            if calculator_type.LookupParameter("Type Name").AsString() not in self.calculator_type_dict.keys():
                if REVIT_SELECTION.is_changable(calculator_type):
                    print("deleting extra type [{}]".format(calculator_type.LookupParameter("Type Name").AsString()))
                    self.doc.Delete(calculator_type.Id)
                    delete_count += 1
                    
        if delete_count > 0:
            self.output.print_md("Deleted {} unused calculator types".format(delete_count))
        else:
            self.output.print_md("No unused calculator types found")

    def place_parking_calculator_instance(self, calculator_type):
        """Place a parking calculator instance."""
        if not calculator_type.IsActive:
            calculator_type.Activate()
        type_name = calculator_type.LookupParameter("Type Name").AsString()
        unit_distant = 75
        index = self.calculator_type_dict.keys().index(type_name)
        row_count = 5
        x, y = index % row_count, index // row_count
        all_this_type_instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(CALCULATOR_FAMILY_NAME, type_name, doc=self.doc, editable_only=False)
        if len(all_this_type_instances) == 0:
            self.doc.Create.NewFamilyInstance(DB.XYZ(unit_distant * x, unit_distant * y, 0), calculator_type, REVIT_VIEW.get_view_by_name(CALCULATOR_DUMP_VIEW_NAME, doc=self.doc))
            return
        
        if len(all_this_type_instances) > 1:
            for x in all_this_type_instances[1:]:
                if REVIT_SELECTION.is_changable(x):
                    print("deleting extra type [{}]".format(x.Symbol.LookupParameter("Type Name").AsString()))
                    self.doc.Delete(x.Id)

    def is_ada(self, parking_instance):
        """Check if a parking instance is ADA compliant."""
        if not parking_instance.Symbol.LookupParameter("Type Comments"):
            return False
        return parking_instance.Symbol.LookupParameter("Type Comments").AsString() == "ADA"

def update_parking_data(doc):
    """Update parking data in the given document."""
    try:
        switch_to_sheet()
    except Exception as e:
        pass
        
    t = DB.Transaction(doc, "Update Parking Data")
    t.Start()
    try:
            calculator = ParkingCalculator(doc)
            calculator.update_parking_data()
            t.Commit()
    except Exception as e:
        t.RollBack()
        print(traceback.format_exc())

def switch_to_sheet():
    """Switch to the specified sheet."""
    sheet = REVIT_SHEET.get_sheet_by_sheet_num(SCHDEULE_SHEET_NUM)
    if sheet:
        REVIT_VIEW.set_active_view(sheet)