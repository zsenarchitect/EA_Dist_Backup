#!/usr/bin/python
# -*- coding: utf-8 -*-
import ENVIRONMENT

def list_to_system_list(list, type = "ElementId", use_IList = False):
    """convert python list to System collection List. 
    In many occasions there need a cast to get to a more strong type of List object

    Args:
        list (python list): _description_
        type (str, optional): the description for target data type. Defaults to "ElementId".
        use_IList (bool, optional): _description_. Defaults to False.

    Returns:
        System.Collections.Generic.List: _description_
    """

    import System
    if ENVIRONMENT.is_Revit_environment():
        from Autodesk.Revit import DB
    if ENVIRONMENT.is_Rhino_environment():
        import Rhino

    if use_IList:
        if type == "CurveLoop":
            return System.Collections.Generic.IList[DB.CurveLoop](list)

        if type == "TableCellCombinedParameterData":
            return System.Collections.Generic.IList[DB.TableCellCombinedParameterData](list)






        return System.Collections.Generic.IList[type](list)


    if type == "Point3d":
        return System.Collections.Generic.List[Rhino.Geometry.Point3d](list)
    if type == "ElementId":
        return System.Collections.Generic.List[DB.ElementId](list)
    if type == "CurveLoop":
        return System.Collections.Generic.List[DB.CurveLoop](list)
    if type == "Curve":
        return System.Collections.Generic.List[DB.Curve](list)
    if type == "TableCellCombinedParameterData":
        return System.Collections.Generic.List[DB.TableCellCombinedParameterData](list)


    if type == "XYZ":
        pts = System.Collections.Generic.List[DB.XYZ]()
        for pt in list:
            pts.Add(pt)
        return pts

    if type == "Double":
        values = System.Collections.Generic.List[System.Double]()
        for value in list:
            values.Add(value)
          
        return values

    return System.Collections.Generic.List[type](list)
    #print_note("Things are not right here...type = {}".format(type))

    return False


#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")