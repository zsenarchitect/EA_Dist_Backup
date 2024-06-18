import os

import sys
parrent_folder = os.path.dirname(__file__)
parrent_folder = os.path.dirname(parrent_folder)
sys.path.append('{}\lib'.format(parrent_folder))
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
import xml.dom.minidom
import xmltodict

# from PIL import Image
import base64
try:
    from PIL import Image as pil_image
except:
    pass
import glob

def OLD_documentation_lookup():
    
    rui_file = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\EnneadTab for Rhino\EnneadTab.rui"
    rui_file = r"C:\Users\szhang\github\EnneadTab-for-Rhino\Source Codes\research.rui"
    #print rui_file
    # xml_doc = xml.dom.minidom.parse(rui_file)
    # print xml_doc

    # see this explaining how to parse xml file
    # https://nanonets.com/blog/parse-xml-files-using-python/
    """
    # get all the package elements
    packages = xml_doc.getElementsByTagName('macros')
    # loop through the packages and extract the data
    for package in packages:
    package_id = package.getAttribute('Macro')
    description =   package.getElementsByTagName('description')[0].childNodes[0].data
    price = package.getElementsByTagName('price')[0].childNodes[0].data
    duration = package.getElementsByTagName('duration')[0].childNodes[0].data
    print('Package ID:', package_id)
    print('Description:', description)
    print('Price:', price)
    """
   # xml_doc = EnneadTab.DATA_FILE.read_txt_file_safely(rui_file)
    #print xml_doc
    print ("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    with open(rui_file) as fd:
        data = xmltodict.parse(fd.read())
        # import pprint
        # pprint.pprint(data)
        
        
    data = data['RhinoUI']
    # print_ordered_dict(data, "")
  
    #######################################
    tool_bars = data['tool_bars']
    print("\n\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    for tool_bar_dict in tool_bars.values():
        print_detail_toolbar(tool_bar_dict)
            
            
    
    print("\n\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    #######################################
    print_detail_macros(data)

        
        
    print("\n\n\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
  
    # small_bitmap_dict = data['bitmaps']['small_bitmap']
    # normal_bitmap_dict = data['bitmaps']['normal_bitmap']
    # large_bitmap_dict = data['bitmaps']['large_bitmap']
    
    print_detail_bitmaps(data)
    
    print ("\n\nDone!!")
    
def print_detail_bitmaps(data):
    detail_level_map = {"small_bitmap":16,
                     "normal_bitmap":24,
                     "large_bitmap":32}
    for detail_level in detail_level_map.keys():
        bitmap_dict = data['bitmaps'][detail_level]
        print ("\n\ndetail_level = {}".format(detail_level))
        # print bitmap_dict
        for i, macro_usage_map in enumerate(bitmap_dict['bitmap_item']):
            print ("macro usage id {} = {}".format(i, macro_usage_map["@guid"]))
        bitmap_data = bitmap_dict['bitmap']
        print ("bitmap_data = {}".format(bitmap_data))
        decoded_bitmap = base64.b64decode(bitmap_data)
        
        
            
        """save this to L drive directly and use silent Email to notify me if it is out of date or cannot find icon.
        somehow the ironpython PIL cannot use module correclty. Or can consider making this a exe....
        """
            
        
        # save the decoded bitmap to a file
        local_bmp = r"C:\Users\szhang\github\EnneadTab-for-Rhino\temp\decoded_bitmap_{}.bmp".format(detail_level)
        with open(local_bmp, "wb") as f:
            f.write(decoded_bitmap)
            
        

        # Load the 100x500 bitmap
        

        
        img = pil_image.open(local_bmp)
        # img = decoded_bitmap

        # Initialize coordinates for slicing
        square_size = detail_level_map[detail_level]
        x1, y1, x2, y2 = 0, 0, square_size, square_size

        # Loop through to create 5 slices
        for i in range(5):
            # Slice image
            slice_img = img.crop((x1, y1, x2, y2))
            
            # Save each slice
            slice_img.save(r"C:\Users\szhang\github\EnneadTab-for-Rhino\temp\{}_{}.png".format(bitmap_dict['bitmap_item'][i]['@guid'],detail_level))
            
            # Move y-coordinates for next slice
            y1 += square_size
            y2 += square_size


def print_detail_toolbar(tool_bar_dict):
    if isinstance(tool_bar_dict, list):
        for x in tool_bar_dict:
            print_detail_toolbar(x) 
        return
    
    print ("Toolbar Id = {}".format(tool_bar_dict['@guid']))
    print ("Toolbar Name = {}".format(tool_bar_dict['text']['locale_1033']))
    print ("Toolbar bitmap_id = {}".format(tool_bar_dict.get('@bitmap_id', None)))
    # print (toolbar_collections)
    for real_button_dict in tool_bar_dict['tool_bar_item']:
        print (real_button_dict)
        button_id = real_button_dict.get('@guid', None)
        # mystery_button_name = real_button_dict.get('text', {}).get('locale_1033', None)
        left_click_function = real_button_dict.get('left_macro_id', None)
        right_click_function = real_button_dict.get('right_macro_id', None)
        # print ("\n\nButton Name = {}".format(mystery_button_name))
        print ("\n\nButton Id = {}".format(button_id))
        print ("Left Click Func Macro Id = {}".format(left_click_function))
        print("Right Click Func Macro Id = {}".format(right_click_function))


def print_detail_macros(data):
    macro_items = data['macros']['macro_item']
    for macro_item in macro_items:
        # print (macro_item)
        maco_id = macro_item['@guid']
        print ("maco_id = {}".format(maco_id))
        button_name = macro_item['button_text']['locale_1033']
        print ("button_name = {}".format(button_name))
        tooltip = macro_item['tooltip']['locale_1033']
        print ("tooltip = {}".format(tooltip))
        script = macro_item['script']
        print ("script = {}".format(script))
        bitmap_id = macro_item['@bitmap_id']
        print ("bitmap_id = {}".format(bitmap_id))
        print ("\n\n\n")
#######################################
def print_ordered_dict(data, parent):
    i = 0
    for key,value in data.items():
        parent += key 
        parent = "*"
        print ("\n{}-----{}-----".format(parent, i))
        print("{}key = {}".format(parent,key))
        if isinstance(value, dict):
            print_ordered_dict(value, "{}+{}".format(parent, key))
        else:
            print("{}value = {}".format(parent,value))
        print ("{}----------\n".format(parent))
        i += 1
            # if i>10:
            #     break
    # value = OrderedDict([(u'macro_item', [OrderedDict([(u'@guid', u'0c964ab3-eeb7-4067-ad68-217a3a3e4b31'), (u'@bitmap_id', u'63dc5647-d881-41dc-a0c7-11e307c5a105'), (u'text', OrderedDict([(u'locale_1033', u'Macro')])), (u'tooltip', OrderedDict([(u'locale_1033', u'tooltipper')])), (u'help_text', OrderedDict([(u'locale_1033', None)])), (u'button_text', OrderedDict([(u'locale_1033', u'tester')])), (u'menu_text', OrderedDict([(u'locale_1033', None)])), (u'script', u'_Show')]), 
    #                                       OrderedDict([(u'@guid', u'fee1ea02-6fc1-4156-a5c9-c3633051f172'), (u'@bitmap_id', u'5600dbcf-4215-49b6-8aeb-ce1a43befe35'), (u'text', OrderedDict([(u'locale_1033', u'Macro 00')])), (u'tooltip', OrderedDict([(u'locale_1033', u'tool tipper 2')])), (u'help_text', OrderedDict([(u'locale_1033', None)])), (u'button_text', OrderedDict([(u'locale_1033', u'tester 2')])), (u'menu_text', OrderedDict([(u'locale_1033', None)])), (u'script', u'_Hide')])])])
    # OUT = ""
    
    # for key, value in data.items():

    #     OUT += key + ": " + str(value) + "\n"
    # rs.TextOut(OUT)
    #data = xmltodict.parse(xml_doc, process_namespaces=True)

    #print data


@EnneadTab.ERROR_HANDLE.try_catch_error
def documentation_lookup():
    if EnneadTab.USER.is_SZ():
        rui_file_main = r"C:\Users\szhang\github\EnneadTab-for-Rhino\Working\EnneadTab.rui"
    else:
        rui_file_main = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Working\EnneadTab.rui"
    rui_file_test = r"C:\Users\szhang\github\EnneadTab-for-Rhino\Source Codes\research.rui"

    for rui_file in [ rui_file_main,rui_file_test]:
        lookup_data = DocumentationLookup(rui_file)
        lookup_data.anaylize()
    
    EnneadTab.NOTIFICATION.messenger(main_text = "Lookup Finish")
    
def print_separation(func):

    """
    Decorator to print a separation line before calling the function.
    """
    def wrapper(*args, **kwargs):
        print("\n\n\n**************{}****************\n".format(func.__name__))
        out = func(*args, **kwargs)
        return out
    return wrapper



    
    
class DocumentationLookup:
    def __init__(self, rui_file):
        if not os.path.exists(rui_file):
            return
        with open(rui_file) as fd:
            self.data = xmltodict.parse(fd.read())['RhinoUI']
        
        if EnneadTab.USER.is_SZ():
            self.data_folder = r"C:\Users\szhang\github\EnneadTab-for-Rhino\bin\Icon Lookup"
        else:
            self.data_folder = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\bin\Icon Lookup"
        self.knowledge = dict()
        self.macro_data = dict()
        self.error_log = ""
        self.allow_print = True
        # get the file name from file path
        print ("\n\n\n\n\n\n\n########### Checking {} ############".format(os.path.basename(rui_file)))
        if False:
            print ("Below are the high level key names")
            for i, key in enumerate(self.data.keys()):
                print ("{}: {}".format(i, key))

    def log(self, text):
        self.error_log += text + "\n"

    def anaylize(self):
        if not hasattr(self, "data"):
            return
        self.print_extend_menu_detail()
        self.print_menu_detail()
        self.print_toolbar_group_detail()
        self.print_toolbar_detail()
        self.print_macro_detail()
        # self.print_bitmap_detail()
        self.print_scripts_detail()
        
        
        
        print (self.error_log)
        
    def collect_data(self):
        self.allow_print = False
        self.print_macro_detail()
        self.print_toolbar_detail()
        
        for bt_name, value in self.knowledge.items():
            if value["macro_id"] in self.access_map.keys():
                value["access"] = self.access_map[value["macro_id"]]
                self.knowledge[bt_name] = value
            if value["macro_id"] in self.button_location_map.keys():
                location_data = self.button_location_map[value["macro_id"]]
                value["tab_name"] = location_data["tab_name"]
                value["tab_icon_id"] = location_data["tab_icon_id"]
                self.knowledge[bt_name] = value
        # EnneadTab.NOTIFICATION.messenger(main_text = "xxxx")

    @print_separation
    def print_extend_menu_detail(self):
        """not sure what this is.
        """
        content = self.data["extend_rhino_menus"]
        print (content)
        pass
    
    @print_separation
    def print_menu_detail(self):
        """this refer to the dropdown menu at top
        """
        content = self.data["menus"]
        print (content)
        
        pass
    
    @print_separation
    def print_scripts_detail(self):
        """not sure what this is
        """
        content = self.data["scripts"]
        print (content)
        pass
    
    @print_separation
    def print_toolbar_group_detail(self):
        """information about all the toolbar groups, AKA tabs icon, tab name
        for knowledge, a toolbar group is amany tabs that are sticked together to forma UI clustor
        For EnneadTab, there should be only one tolbar group item, and on that toolbar group that should be 11 toolbar, aka 11 tabs
        """
        def detail_print(dict_data):
            print ("Tab Group Name = <{}>".format(dict_data["text"]["locale_1033"]))
            print ("There are {} tabs(toolbar) on tab(toolbar) group, and below are their names:".format(len(dict_data["tool_bar_group_item"])))
            for i,tab in enumerate(dict_data["tool_bar_group_item"]):
                
                print ("--{}: {}".format(i,tab["text"]["locale_1033"]))
                print ("     guid = {}".format(tab["@guid"]))
                print ("     tab(toolbar) guid = {}".format(tab["tool_bar_id"]))
        
                
        
        
        content = self.data["tool_bar_groups"]["tool_bar_group"]
        # print (content)
        if (isinstance(content, list)):
            # print ("[List data]Below are the items in the toolbar group")
            for i, item in enumerate(content):
                # print ("{}: {}".format(i, item.keys()))
                detail_print(item)
        elif (isinstance(content, dict)):
            # print ("[Dict data]Below are the items in the toolbar group")
            # for i, key in enumerate(content.keys()):
            #     print ("{}: {}".format(i, key))
            detail_print(content)
                
            
        # print ("\n\nBelow are the tabs info")
        # for tab_dict in content["tool_bar_group_item"]:
        #     print (tab_dict)
        # pass
    
    @print_separation
    def print_toolbar_detail(self):
        """each toolbar information, AKA all the buttons info, left right click to which macro, which bitmp id it is using
        """
        self.access_map = {}
        self.button_location_map = {}
        
            
        def recycle_right_click_icon(button_dict):
            # try to recycle left click macro's icon for the right click macro
            right_click_id = button_dict.get("right_macro_id", None)
            if not right_click_id:
                return
            if not hasattr(self, "macro_data"):
                return
                
            right_macro = self.macro_data.get(right_click_id, None)
            
            
            if not right_macro:
                print ("Right click macro id = {} not found in macro data".format(right_click_id))
                return
            right_button_name = DocumentationLookup.get_name(right_macro,"button_text")
            right_button_icon_id = right_macro["@bitmap_id"]
            
            left_click_id = button_dict.get("left_macro_id", None)
            left_macro = self.macro_data[left_click_id]
            left_button_name = DocumentationLookup.get_name(left_macro,"button_text")
            self.knowledge[right_button_name]["icon_id"] = self.knowledge[left_button_name]["icon_id"]
            
            
            
        def detail_print_button(counter, button_dict):
            # print ("----{}: Button Name = <{}>".format(counter, get_name(button_dict))) # this name is not very helpful info
            # print button_dict.keys()
            if self.allow_print:
                print ("\n----{}: Button guid = {}".format(counter, button_dict["@guid"]))
                print ("       Button left macro id = {}".format(button_dict.get("left_macro_id", None)))
                print ("       Button right macro id = {}".format(button_dict.get("right_macro_id", None)))
            self.access_map[button_dict.get("left_macro_id", "None")] = "Left Click"
            self.access_map[button_dict.get("right_macro_id", "None")] = "Right Click"
            
            
            
            recycle_right_click_icon(button_dict)
            
            
            
                
                
            self.button_location_map[button_dict.get("left_macro_id", "None")] = {"tab_name":toolbar["text"]["locale_1033"],
                                                                                  "tab_icon_id":toolbar.get("@bitmap_id", None)}
            self.button_location_map[button_dict.get("right_macro_id", "None")] = {"tab_name":toolbar["text"]["locale_1033"],
                                                                                  "tab_icon_id":toolbar.get("@bitmap_id", None)}
            
        content = self.data["tool_bars"]["tool_bar"]
        
        for i, toolbar in enumerate(content):
            if self.allow_print:
                print ("\n++++{}: <{}> with {} buttons\n".format(i,
                                                        toolbar["text"]["locale_1033"],
                                                        len(toolbar["tool_bar_item"]) if isinstance(toolbar["tool_bar_item"], list) else 1))
                print ("       toolbar guid = {}".format(toolbar["@guid"]))
                print ("       toolbar bitmap guid = {}\n".format(toolbar.get("@bitmap_id", None)))
            buttons =  toolbar["tool_bar_item"]
            if isinstance(buttons, dict):
                detail_print_button(0, buttons)
                continue
            for j, button in enumerate(buttons):
                detail_print_button(j, button)
                #
        pass
    
    @print_separation
    def print_macro_detail(self):
        """information about which script it is linking to , what is the button text, menu text, icon guid, tooltip!!
        """
        content = self.data["macros"]['macro_item']
        print ("There are {} macros".format(len(content)))
        for i, macro in enumerate(content):
            # print macro.keys()
            if self.allow_print:
                print("\n--{}: macro guid = {}".format(i, macro["@guid"]))
                print ("     macro bitmap guid = {}".format(macro["@bitmap_id"]))
                print ("     macro macro name = {}".format(DocumentationLookup.get_name(macro)))
                print ("     macro button text = {}".format(DocumentationLookup.get_name(macro,"button_text")))
                print ("     macro menu text = {}".format(DocumentationLookup.get_name(macro,"menu_text")))
                print ("     macro tooltip = {}".format(DocumentationLookup.get_name(macro,"tooltip")))
                # print ("     macro script = \n<<<\n{}\n>>>".format(macro.get("script", None)))  
                
            button_name = DocumentationLookup.get_name(macro,"button_text")   
            if button_name in self.knowledge.keys():
                self.log ("\nmacro name = <{}>'s button text <{}> already exists in knowledge key".format(DocumentationLookup.get_name(macro), button_name))
                self.log("The previous macro name <{}>'s button name is also <{}>".format(self.knowledge[button_name]["macro_name"], button_name))
                EnneadTab.NOTIFICATION.messenger("Watch out")
                
            self.knowledge[button_name] = {"macro_id":macro["@guid"],
                                            "macro_tooltip":DocumentationLookup.get_name(macro,"tooltip"),
                                            "icon_id":macro["@bitmap_id"],
                                            "access":"undefined",
                                            "macro_name":DocumentationLookup.get_name(macro)}
            self.macro_data[macro["@guid"]] = macro
        pass
    
    @print_separation
    def print_bitmap_detail(self):
        """the merged bmp image that have all the icon stacked. There are three levels of display
        """
        # self.data_folder = EnneadTab.FOLDER.get_EA_dump_folder_file("Rhino_Toolbar_Icon_Lookup")
        
        if not os.path.exists(self.data_folder):
            os.mkdir(self.data_folder)
        
        detail_level_map = {"small_bitmap":16,
                            "normal_bitmap":24,
                            "large_bitmap":32}
        content = self.data["bitmaps"]
        # print (content)
        
        for detail_level in detail_level_map.keys():
            print ("\n\ndetail_level = {}".format(detail_level))
            # print bitmap_dict
            bitmap_dict = content[detail_level]
            for i, macro_usage_map in enumerate(bitmap_dict['bitmap_item']):
                print ("{}: related macro id = {}".format(i, macro_usage_map["@guid"]))
                
            if not EnneadTab.USER.is_SZ():
                continue
            
            if EnneadTab.ENVIRONMENT.is_Rhino_environment():
                continue
            
            
            bitmap_data = bitmap_dict['bitmap']
            # print ("bitmap_data = {}".format(bitmap_data))
            decoded_bitmap = base64.b64decode(bitmap_data)
            
            
            """save this to L drive directly and use silent Email to notify me if it is out of date or cannot find icon.
            somehow the ironpython PIL cannot use module correclty. Or can consider making this a exe....
            """
                
            # save the decoded bitmap to a file
            local_bmp = "{}\decoded_bitmap_{}.bmp".format(self.data_folder,
                                                          detail_level)
            with open(local_bmp, "wb") as f:
                f.write(decoded_bitmap)
                 
            img = pil_image.open(local_bmp)
            # img = decoded_bitmap

            # Initialize coordinates for slicing
            square_size = detail_level_map[detail_level]
            x1, y1, x2, y2 = 0, 0, square_size, square_size

            # Loop through to create as mnay as there are item slices
            for i in range(len(bitmap_dict['bitmap_item'])):
                # Slice image
                slice_img = img.crop((x1, y1, x2, y2))
                
                # Save each slice
                slice_img.save("{}\{}_{}.png".format(self.data_folder,
                                                     bitmap_dict['bitmap_item'][i]['@guid'],
                                                     detail_level))
                
                # Move y-coordinates for next slice
                y1 += square_size
                y2 += square_size
            
        pass

    @staticmethod
    def get_name(data, key = "text"):
        if not data.get(key, None):
            return ""
        return data[key]["locale_1033"]
######################  main code below   #########
if __name__ == "__main__":

    documentation_lookup()




"""
##The Search Paths options manage locations to search for bitmaps that used for render texture and bump maps.
rs.AddSearchPath(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EA_UTILITY.py')




rs.FindFile(filename)
Searches for a file using Rhino's search path. Rhino will look for a
    file in the following locations:
      1. The current document's folder.
      2. Folder's specified in Options dialog, File tab.
      3. Rhino's System folders
path = rs.FindFile("Rhino.exe")
print(path)




Rhino.RhinoObject.Select(True, True, True, False, True, False)

"""
