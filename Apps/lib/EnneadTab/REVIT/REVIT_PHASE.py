# -*- coding: utf-8 -*-

try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = __revit__.ActiveUIDocument # pyright: ignore
    DOC = UIDOC.Document
    

    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()


def get_all_phases(doc = DOC, sort_by_name = True):
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
    filter = DB.ElementPhaseStatusFilter (phase.Id, DB.ElementOnPhaseStatus.Existing)
    all_elements = DB.FilteredElementCollector(doc).OfCategory(category).WherePasses(filter).WhereElementIsNotElementType().ToElements()
    return all_elements




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
