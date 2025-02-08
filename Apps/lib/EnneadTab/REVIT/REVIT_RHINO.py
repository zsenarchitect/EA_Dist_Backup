try:
    import clr  # pyright: ignore
    import System  # pyright: ignore
    clr.AddReference('RhinoCommon')
    import Rhino  # pyright: ignore
    clr.AddReference('RhinoInside.Revit')
    from RhinoInside.Revit.Convert.Geometry import GeometryDecoder as RIR_DECODER  # pyright: ignore
   
    IMPORT_OK = True
except:
    IMPORT_OK = False


import REVIT_UNIT

def setup_rhino_doc(revit_doc):
    rhino_doc = Rhino.RhinoDoc.CreateHeadless(None)


    revit_unit = REVIT_UNIT.get_doc_length_unit_name(revit_doc)
 
    

    revit_unit_dict = {
        "millimeters": 2,
        "feet": 9,
        "inches": 8,
        "feetFractionalInches": 9
    }

    rhino_unit = revit_unit_dict.get(revit_unit, 9)
    rhino_doc.AdjustModelUnitSystem (
        System.Enum.ToObject(Rhino.UnitSystem, rhino_unit), 
        False
    )

    

    return rhino_doc