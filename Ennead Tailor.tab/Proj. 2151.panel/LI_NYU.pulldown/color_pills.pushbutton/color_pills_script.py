__doc__ = "Colorize the diagram pills, requested by Gayatri"
__title__ = "Colorize Pills"

# from pyrevit import forms #
from pyrevit import script #
import os
import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # fastest DB
# from Autodesk.Revit import UI
try:
    doc = __revit__.ActiveUIDocument.Document
except:
    pass


COLOR_SCHEME_NAME = "[Areas]: Primary_Department Category"      

        
@EnneadTab.ERROR_HANDLE.try_catch_error
def color_pills(doc, show_log = False):
    
    solution = ColorizePills(doc)
    if not solution.is_valid:
        return
    # process each
    
    # get all special detail compnents in file
    special_detail_components = solution.get_all_special_detail_components()
    if show_log:
        print ("Found {} special detail components".format(len(special_detail_components)))
        print ("Processing...")
    
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    map(solution.process_pill, special_detail_components)
    t.Commit()

    
    if show_log:
        
        EnneadTab.NOTIFICATION.messenger(main_text = "Color pill color change done!")




class ColorizePills:
    
    def __init__(self, doc):
        self.is_valid = True
        self.doc = doc
        self.output = script.get_output()
        # self.OLD_get_color_map()
        self.get_color_scheme_data()
        if len(self.color_map) == 0:
            self.is_valid = False
            return 
        
        # prepare a hot pink for bad color
        self.bad_color = DB.Color(255, 0, 255)
        self.solid_pattern_id = EnneadTab.REVIT.REVIT_SELECTION.get_solid_fill_pattern(self.doc, return_id = True)
        
    
    def get_color_scheme_data(self):
        self.color_map = dict()
        self.pattern_map = dict()
        
        color_schemes = DB.FilteredElementCollector(self.doc).OfCategory(DB.BuiltInCategory.OST_ColorFillSchema).WhereElementIsNotElementType().ToElements()
        def scheme_name(x):
            cate_name = DB.Category.GetCategory(self.doc, x.CategoryId).Name
            return "[{}]: {}".format(cate_name, x.Name)
        color_schemes = filter(lambda x: scheme_name(x) == COLOR_SCHEME_NAME, color_schemes)
        if len(color_schemes)== 0:
            EnneadTab.NOTIFICATION.messenger(main_text = "Cannot find the color scheme [{}].\nMaybe you renamed your color scheme recently? Talk to SZ for update.".format(COLOR_SCHEME_NAME))
            return
        color_scheme = color_schemes[0]
        # print color_scheme
        
        
        for entry in color_scheme.GetEntries():
            self.color_map[ entry.GetStringValue()] = entry.Color
            self.pattern_map[ entry.GetStringValue()] = entry.FillPatternId 
            
    
    
    
    
    def OLD_get_color_map(self):
        # get script folder
        folder = os.path.dirname(os.path.realpath(__file__))
        # excel = "{}\\LI_NYU_COLOR_MAP.xlsx".format(folder)
        color_file = "{}\\color_scheme_dict.json".format(folder)
        
        # # print excel
        # # print EnneadTab.EXCEL.get_all_worksheets(excel)
        # sheet = "Color Scheme"
        # entries = EnneadTab.EXCEL.read_data_from_excel(excel, worksheet = sheet)
        # print color_file
        entries = EnneadTab.DATA_FILE.read_json_as_dict(color_file, use_encode = True)
        
        
        
        self.color_map = dict()
        for entry, value in entries.items():
            # if entry[3] == "Color R":
            #     continue
            
            
            # cate_name = entry[0]
            
            # try:
            #     R, G, B = int(entry[3]), int(entry[4]), int(entry[5])
            # except Exception as e:
            #     R, G, B = 200,10,10
            #     print entry
            #     print "Error reading color for {}: {}".format(cate_name, e)
            
            
            R, G, B = int(value[0]), int(value[1]), int(value[2])
            revit_color = DB.Color(R, G, B)
            self.color_map[entry] = revit_color
        
    
    def get_all_special_detail_components(self):
        # get all special detail components
        special_detail_components = DB.FilteredElementCollector(self.doc).OfCategory(DB.BuiltInCategory.OST_DetailComponents).WhereElementIsNotElementType().ToElements()
        special_detail_components = filter(lambda x: hasattr(x, "Symbol") and x.Symbol.FamilyName.lower().startswith( "DTL_Healthcare_Planning_Section Bubble".lower()), special_detail_components)
        
        return EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(special_detail_components)
         


    def process_pill(self, pill):
        # print "------------------"
        # get the view it is using
        owner_view_id = pill.OwnerViewId
        view = self.doc.GetElement(owner_view_id)
        if not EnneadTab.REVIT.REVIT_SELECTION.is_changable(view):
            print "View <{}> cannot be editted right now due to ownership by {}.".format(view.Name,view .LookupParameter("Edited by").AsString())
            return
        
        category_name = pill.LookupParameter("bubble_diagram_label").AsString()
        # print category_name
        
        category_name = str(category_name).replace("\r\n", " ").replace("\n"," ")
        # print category_name
        # for x in category_name:
        #     print ("*{}*, {}".format(x, type(x)))
        # print category_name.split(" ")
        
        # print category_name == "PROCEDURE PLATFORM  KEY ROOMS"
        
        # lookup tha color table
        color = self.color_map.get(category_name, None)
        pattern_id = self.pattern_map.get(category_name, None)
        if color is None:
            print "No color for <{}> found in color map. Check spelling....{}(Link only works while run from tailor tab)".format(category_name,
                                                                                      self.output.linkify(pill.Id, title="Select Pill Shape"))
            color = self.bad_color
            pattern_id = self.solid_pattern_id
         
        """   
        if pattern_id is None:
            print "No pattern for <{}> found in pattern map. Check spelling....{}(Link only works while run from tailor tab)".format(category_name,
                                                                                      self.output.linkify(pill.Id, title="Select Pill Shape"))
        """
        
        setting = DB.OverrideGraphicSettings ()
        setting.SetSurfaceForegroundPatternColor(color)
        setting.SetSurfaceForegroundPatternId(pattern_id)
        view.SetElementOverrides(pill.Id, setting)
        
        pass



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    color_pills(doc, show_log = True)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)










