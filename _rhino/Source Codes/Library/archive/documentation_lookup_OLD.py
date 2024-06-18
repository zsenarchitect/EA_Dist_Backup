import sys
sys.path.append('..\lib')

import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
import xml.dom.minidom
import xmltodict

# from PIL import Image

import base64

@EnneadTab.ERROR_HANDLE.try_catch_error
def documentation_lookup():
    
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
        from PIL import Image as pil_image
        
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


######################  main code below   #########
if __name__ == "__main__":

    documentation_lookup()

