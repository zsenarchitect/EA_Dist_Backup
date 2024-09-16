



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