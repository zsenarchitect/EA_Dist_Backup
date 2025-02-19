from pyrevit import forms
from Autodesk.Revit import DB # pyright:ignore

def pick_category(doc):
    """Displays UI for selecting Revit categories from a predefined list.
    
    Args:
        doc (Document): The Revit document to query categories from
        
    Returns:
        list: Collection of selected Category objects, or None if selection canceled
    """
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
    """Wrapper class for Revit Category objects providing enhanced functionality.
    
    Args:
        category (Category): The Revit Category object to wrap
    """
    
    def __init__(self, category):
        self.category = category

    @property
    def sub_category(self):
        """Gets the sub-category if the category is nested.
        
        Returns:
            Category: The sub-category object if present, None otherwise
        """
        if self.category.Parent:
            return self.category
        return None
    
    @property
    def sub_category_name(self):
        """Gets the name of the sub-category.
        
        Returns:
            str: Name of the sub-category if present, empty string otherwise
        """
        if self.sub_category:
            return self.sub_category.Name
        return ""
    
    @property
    def root_category(self):
        """Gets the root category, traversing up the parent hierarchy.
        
        Returns:
            Category: The root category object
        """
        if self.category.Parent:
            return self.category.Parent
        return self.category

    @property
    def root_category_name(self):
        """Gets the name of the root category.
        
        Returns:
            str: Name of the root category
        """
        return self.root_category.Name

    @property
    def pretty_name(self):
        """Formats a human-readable category name including hierarchy.
        
        Returns:
            str: Formatted string showing root and sub-category if present
        """
        if not self.sub_category:
            return "[{}]".format(self.root_category_name)
        
        return "[{}]: {}".format(self.root_category_name, self.sub_category_name)