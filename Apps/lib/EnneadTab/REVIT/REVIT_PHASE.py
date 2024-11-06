# -*- coding: utf-8 -*-

from collections import OrderedDict
import REVIT_APPLICATION
try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
    import DATA_CONVERSION
    import REVIT_APPLICATION

    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()


def get_all_phases(doc = DOC, sort_by_name = False):
    phases = [phase for phase in doc.Phases]

    if sort_by_name:
        return sorted(phases, key = lambda x: x.Name)
    else:
        return phases

def get_phase_by_name(phase_name, doc = DOC):
    all_phases = get_all_phases(doc)
    for phase in all_phases:
        if phase.Name == phase_name:
            return phase
    return None



def get_elements_in_phase(doc, phase, category = DB.BuiltInCategory.OST_Rooms):
    status_collection = [DB.ElementOnPhaseStatus.Existing, DB.ElementOnPhaseStatus.New]
    status_collection = DATA_CONVERSION.list_to_system_list(status_collection, 
                                                            type=DB.ElementOnPhaseStatus, 
                                                            use_IList=False)
    filter = DB.ElementPhaseStatusFilter (phase.Id, status_collection)
    all_elements = DB.FilteredElementCollector(doc).OfCategory(category).WherePasses(filter).WhereElementIsNotElementType().ToElements()
    return all_elements


def get_phase_map(doc = DOC, return_name = False):
    phase_map = {}
    revit_links = list(DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance).ToElements())
    master_phases = get_all_phases(doc)
    master_phases_names = [x.Name for x in master_phases]
    for revit_link in revit_links:
        revit_link_type = doc.GetElement(revit_link.GetTypeId())
        if not DB.RevitLinkType.IsLoaded(doc, revit_link_type.Id):
            print ("Link type [{}] is not loaded".format(revit_link_type.LookupParameter("Type Name").AsString()))
            continue
        
        temp_map = OrderedDict()
        temp_phase_map = dict(revit_link_type.GetPhaseMap())
        
        for key in sorted(temp_phase_map.keys(), key=lambda x: master_phases_names.index(doc.GetElement(x).Name)):
            value = temp_phase_map[key]
            if return_name:
                temp_map[doc.GetElement(key).Name] = revit_link.GetLinkDocument().GetElement(value).Name
            else:
                temp_map[doc.GetElement(key)] = revit_link.GetLinkDocument().GetElement(value)
        phase_map[revit_link.GetLinkDocument().Title] = temp_map
    return phase_map

def pretty_print_phase_map(doc=DOC):
    """
    Pretty prints the phase map for all linked documents in the given Revit document.

    Args:
        doc (Document, optional): The Revit document. Defaults to DOC.

    Prints:
        The phase map for all linked documents, showing the mapping of phases between the master document and each linked document.
    """
    from pyrevit import script
    output = script.get_output()
    output.print_md("### Below is the phase map for all linked docs in [{}]".format(doc.Title))
    phase_map = get_phase_map(doc, return_name=True)
    for doc_name, value in phase_map.items():
        print("\n[{}] --> [{}]".format(doc.Title,doc_name))
        for key2, value2 in value.items():
            print("\t{}: {}".format(key2, value2))

def get_element_phase(element):
    return
    para_id = DB.BuiltInParameter.ROOM_PHASE
    phase = element.Parameter[para_id].AsString()
    print(phase)
    return
    for para in element.Parameters:
        print(para.Definition.Name)
        if "phase" in  para.Definition.Name.lower():
            print(para.Definition.Name)
            print(para.AsString())
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(element.LookupParameter("Phase").AsString())
    print("@@@")
    all_phase_ids = DB.FilteredElementCollector(doc).OfClass(DB.Phase).ToElementIds ()
    for phase_id in all_phase_ids:
        print(doc.GetElement(phase_id).Name)
        print(element.GetPhaseStatus(phase_id))
        if element.GetPhaseStatus(phase_id) == DB.ElementOnPhaseStatus.New:
            return "Phase = {}".format(doc.GetElement(phase_id).Name)
    return



    phase = doc.GetElement(element.CreatedPhaseId)
    if phase:
        phase_creation = phase.Name
    else:
        phase_creation = "N/A"


    phase = doc.GetElement(element.DemolishedPhaseId)
    if phase:
        phase_demolision = phase.Name
    else:
        phase_demolision = "N/A"

    if phase_creation == "N/A" and phase_demolision == "N/A":

        para_id = DB.BuiltInParameter.ROOM_PHASE
        phase = element.Parameter[para_id].AsString()
        print(element.Parameter[para_id].AsString())
        print(element.Parameter[para_id].ToString())
        if phase:
            return "Phase = {}".format(phase)
        else:
            return "Phase = N/A"
    return "Phase Created = {}, Phase Demolished = {}".format(phase_creation, phase_demolision)
