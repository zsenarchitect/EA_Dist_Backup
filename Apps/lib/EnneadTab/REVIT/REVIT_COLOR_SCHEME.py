#!/usr/bin/python
# -*- coding: utf-8 -*-


import NOTIFICATION, COLOR, OUTPUT
import REVIT_SELECTION
import REVIT_APPLICATION
try:
    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
    from pyrevit import script
except:
    pass



class ColorSchemeUpdater:
    """Manages updates to Revit color schemes from external template data.
    
    Args:
        doc (Document): The Revit document containing color schemes
        naming_map (dict): Mapping between excel data keys and Revit scheme names
        excel_path (str): Path to the excel template file
        is_remove_unused (bool): Whether to remove unused entries. Defaults to False
    """
    
    def __init__(self, doc, naming_map, excel_path, is_remove_unused = False):
        self.doc = doc
        self.naming_map = naming_map
        self.excel_path = excel_path
        self.is_remove_unused = is_remove_unused
        self.output = script.get_output()
    
    def load_color_template_from_excel(self):
        """Updates color schemes using data from template excel file.
        
        Loads color data from excel and updates or creates color scheme entries
        accordingly. Notifies user upon completion.
        """
        # Load data from color excel
        data = COLOR.get_color_template_data(self.excel_path)

        # Update color scheme, create if not exist, update color if exist
        t = DB.Transaction(self.doc, "Update Color Scheme")
        t.Start()
        for key, value in self.naming_map.items():
            if isinstance(value, str):
                value = [value]
            for color_scheme_name in value:
                self.update_color_scheme(data, key, color_scheme_name)
        t.Commit()
        
        NOTIFICATION.messenger(main_text="Color Scheme Updated!")
        print ("Finish updating Color Scheme")
        OUTPUT.display_output_on_browser()

    def update_color_scheme(self, data, lookup_key, color_scheme_name):
        """Updates a specific color scheme with template data.
        
        Args:
            data (dict): Color template data from excel
            lookup_key (str): Key to find matching data in template
            color_scheme_name (str): Name of the color scheme to update
        """
        if not color_scheme_name:
            return
        color_scheme = get_color_scheme_by_name(color_scheme_name)
        if not color_scheme:
            print ("cannot find color scheme {}".format(color_scheme_name))
            NOTIFICATION.messenger(main_text="Color Scheme [{}] not found!\nCheck spelling".format(color_scheme_name))
            return
        
        self.output.print_md("#Working on color scheme [{}]".format(color_scheme.Name))

        is_abbr = False
        if "abbr" in lookup_key:
            lookup_key = lookup_key.replace("_abbr", "")
            is_abbr = True
            
        department_data = data[lookup_key]

        #  is abbr, then use abbr as the driver key
        if is_abbr:
            temp_data = {}
            for key, value in department_data.items():
                abbr = value["abbr"]
                temp_data[abbr] = value
            department_data = temp_data
        

        
        try:
            sample_entry = list(color_scheme.GetEntries())[0]
        except:
            NOTIFICATION.messenger("Please at least have one placeholder entry in the color scheme...")
            return
        storage_type = sample_entry.StorageType

        current_entry_names = [x.GetStringValue() for x in color_scheme.GetEntries()]
        if self.is_remove_unused:
            self.remove_non_used_entry(color_scheme)
        self.add_missing_entry(color_scheme, department_data, current_entry_names, storage_type)
        self.update_entry_color(color_scheme, department_data)

    @staticmethod
    def markdown_text(text, colorRGB):
        """Formats text with color for markdown output.
        
        Args:
            text (str): Text to format
            colorRGB (tuple): RGB color values
            
        Returns:
            str: HTML formatted text with color
        """
        return '<span style="color:rgb{};">{}</span>'.format(str(colorRGB), text)


    def remove_non_used_entry(self, color_scheme):
        """Removes unused entries from color scheme.
        
        Args:
            color_scheme (ColorFillScheme): The color scheme to clean up
        """
        for existing_entry in color_scheme.GetEntries():
            if color_scheme.CanRemoveEntry (existing_entry):
                color_scheme.RemoveEntry(existing_entry)
                entry_title = existing_entry.GetStringValue()
                self.output.print_md("**---** entry [{}] removed{}".format(entry_title, ", not used" if existing_entry.IsInUse else ""))

    def add_missing_entry(self, color_scheme, department_data, current_entry_names, storage_type):
        """Adds new entries to color scheme that exist in template but not in Revit.
        
        Args:
            color_scheme (ColorFillScheme): Target color scheme
            department_data (dict): Template data for departments
            current_entry_names (list): Existing entry names
            storage_type (StorageType): Storage type for new entries
        """
        for department in department_data.keys():
            if department not in current_entry_names:
                entry = DB.ColorFillSchemeEntry(storage_type)
                entry.Color = COLOR.tuple_to_color(department_data[department]["color"])
                entry.SetStringValue(department)
                entry.FillPatternId = REVIT_SELECTION.get_solid_fill_pattern_id(self.doc)
                color_scheme.AddEntry(entry)
                self.output.print_md("**+++** entry [{}] added with **{}**".format(department, 
                                                                                   self.markdown_text("COLOR RGB={}".format(department_data[department]["color"]), department_data[department]["color"])))

    def update_entry_color(self, color_scheme, department_data):
        """Updates colors of existing entries to match template.
        
        Args:
            color_scheme (ColorFillScheme): Color scheme to update
            department_data (dict): Template color data
        """
        for existing_entry in color_scheme.GetEntries():
            entry_title = existing_entry.GetStringValue()
            existing_color = existing_entry.Color
            
            lookup_data = department_data.get(entry_title, None)
            if not lookup_data:
                
                self.output.print_md("###  ??? entry [{}] in current area scheme not found in template excel. Are you defining a new entry? Or the spelling is different?\nThis entry is skipped for now.\n".format(entry_title))
                print ("\n")
                continue
            
            lookup_color = COLOR.tuple_to_color(lookup_data["color"])
            
            if COLOR.is_same_color(existing_color, lookup_color):
                continue
            
            old_color = (existing_entry.Color.Red, existing_entry.Color.Green, existing_entry.Color.Blue)
            existing_entry.Color = lookup_color
            color_scheme.UpdateEntry(existing_entry)
            self.output.print_md("**$$$** entry [{}] updated from **{}** to **{}**".format(entry_title, 
                                                                                           self.markdown_text("OLD COLOR RGB={}".format(old_color), old_color), 
                                                                                           self.markdown_text("NEW COLOR RGB={}".format(lookup_data["color"]), lookup_data["color"])))


def get_color_scheme_by_name(scheme_name, doc = DOC):
    """Retrieves a color scheme by its name.
    
    Args:
        scheme_name (str): Name of the color scheme to find
        doc (Document): The Revit document to query. Defaults to active document
        
    Returns:
        ColorFillScheme: The matching color scheme, or None if not found
    """
    color_schemes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ColorFillSchema).WhereElementIsNotElementType().ToElements()
    color_schemes = filter(lambda x: x.Name == scheme_name, color_schemes)
    if len(color_schemes)== 0:
        NOTIFICATION.messenger(main_text = "Cannot find the color scheme [{}].\nMaybe you renamed your color scheme recently? Talk to SZ for update.".format(scheme_name))
        return
    if len(color_schemes) > 1:
        NOTIFICATION.messenger(main_text = "Found more than one color scheme with the name [{}].\nNeed better naming.".format(scheme_name))
        return
    return color_schemes[0]

def pick_color_scheme(doc = DOC, title = "Select the color scheme", button_name = "Select", multiselect = False):
    """Displays UI for selecting color schemes.
    
    Args:
        doc (Document): The Revit document to query. Defaults to active document
        title (str): Dialog title. Defaults to "Select the color scheme"
        button_name (str): Button text. Defaults to "Select"
        multiselect (bool): Allow multiple selection. Defaults to False
        
    Returns:
        str/list: Selected scheme name(s) or None if canceled
    """
    from pyrevit import forms
    color_schemes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ColorFillSchema).WhereElementIsNotElementType().ToElements()
    return forms.SelectFromList.show([x.Name for x in color_schemes], multiselect=multiselect, title=title, button_name=button_name)

def pick_color_schemes(doc = DOC, title = "Select the color scheme", button_name = "Select"):
    """Wrapper for picking multiple color schemes.
    
    Args:
        doc (Document): The Revit document to query. Defaults to active document
        title (str): Dialog title. Defaults to "Select the color scheme"
        button_name (str): Button text. Defaults to "Select"
        
    Returns:
        list: Selected scheme names or None if canceled
    """
    return pick_color_scheme(doc, title, button_name, True)

def load_color_template(doc, naming_map, excel_path, is_remove_unused = False):
    """Updates color schemes from office template excel file.
    
    Excel Requirements:
    - Save as .xls format (not .xlsx)
    - Column headers must be:
        A: Department
        B: Department Abbr.
        C: Department Color
        D: Program
        E: Program Abbr.
        F: Program Color
    
    Args:
        doc (Document): The Revit document to update
        naming_map (dict): Maps excel sections to Revit scheme names
        excel_path (str): Path to template excel file
        is_remove_unused (bool): Remove unused entries. Defaults to False
        
    Example:
        naming_map = {
            "department_color_map": "Primary_Department Category",
            "program_color_map": "Primary_Department Program Type"
        }
    """
    updater = ColorSchemeUpdater(doc, naming_map, excel_path, is_remove_unused)
    updater.load_color_template_from_excel()