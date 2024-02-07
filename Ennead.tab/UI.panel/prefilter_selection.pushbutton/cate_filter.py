
from Autodesk.Revit import DB 
from Autodesk.Revit import UI


CATE_MAPPING = {
    "areas": DB.BuiltInCategory.OST_Areas,
    "areatags": DB.BuiltInCategory.OST_AreaTags,
    "xxx": DB.BuiltInCategory.OST_AreaSchemeLines,
    "xxx": DB.BuiltInCategory.OST_Columns,
    "xxx": DB.BuiltInCategory.OST_StructuralColumns,
    "dimensions": DB.BuiltInCategory.OST_Dimensions,
    "curtainpanels": DB.BuiltInCategory.OST_CurtainWallPanels,
    "curtaingrids": DB.BuiltInCategory.OST_CurtainGrids,
    "xxx": DB.BuiltInCategory.OST_Doors,
    "floors": DB.BuiltInCategory.OST_Floors,
    "xxx": DB.BuiltInCategory.OST_StructuralFraming,
    "xxx": DB.BuiltInCategory.OST_Furniture,
    "grids": DB.BuiltInCategory.OST_Grids,
    "rooms": DB.BuiltInCategory.OST_Rooms,
    "roomtags": DB.BuiltInCategory.OST_RoomTags,
    "xxx": DB.BuiltInCategory.OST_Truss,
    "xxx": DB.BuiltInCategory.OST_Walls,
    "xxx": DB.BuiltInCategory.OST_Windows,
    "xxx": DB.BuiltInCategory.OST_Ceilings,
    "xxx": DB.BuiltInCategory.OST_SectionBox,
    "xxx": DB.BuiltInCategory.OST_ElevationMarks,
    "xxx": DB.BuiltInCategory.OST_Parking
}



class CateFilter(UI.Selection.ISelectionFilter):
    """Selection filter implementation"""
    def __init__(self, selection_cate_setting):
        for key in selection_cate_setting:
            if key not in CATE_MAPPING:
                raise Exception("Invalid category name: {}".format(key))
        self.allowed_cates = [DB.ElementId(CATE_MAPPING[key]) for key, value in selection_cate_setting.items() if value]
       

    def AllowElement(self, element):
        """Is element allowed to be selected?"""
        if not element.Category:
            return
        return element.Category.Id in self.allowed_cates


    def AllowReference(self, refer, point): 
        """Not used for selection"""
        return False


if __name__ == "__main__":
    pass