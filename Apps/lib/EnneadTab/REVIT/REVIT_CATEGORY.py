from pyrevit import forms
from Autodesk.Revit import DB # pyright:ignore

def pick_category(doc):
    cate_list = [("OST_Grids", "Grids"),
            ("OST_Levels", "Levels"),
            ("OST_Rooms", "Rooms"),
            ("OST_Areas", "Areas"),
            ("OST_Furniture", "Furniture"),
            ("OST_Parking", "Parking"),]
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return self.item[1]

    selected_cates = forms.SelectFromList.show([MyOption(cate) for cate in cate_list], 
                                      title = "Select Categorie(s) to bind", 
                                      multiselect = True)
    if not selected_cates:
        return
    
    selected_cate_ids = [getattr(DB.BuiltInCategory , cate[0]) for cate in selected_cates]
    selected_cates = [DB.Category.GetCategory(doc, cate_id) for cate_id in selected_cate_ids]


    return selected_cates
  


class RevitCategory:
    def __init__(self, category):
        self.category = category


    @property
    def sub_category(self):
        if self.category.Parent:
            return self.category
        return None
    
    @property
    def sub_category_name(self):
        if self.sub_category:
            return self.sub_category.Name
        return ""
    
    @property
    def root_category(self):
        if self.category.Parent:
            return self.category.Parent
        return self.category

    @property
    def root_category_name(self):
        return self.root_category.Name

    @property
    def pretty_name(self):
        if not self.sub_category:
            return "[{}]".format(self.root_category_name)
        
        return "[{}]: {}".format(self.root_category_name, self.sub_category_name)