import random
import sys
sys.path.append("C:\\Users\\szhang\\design-repo\\EnneadTab-OS\\Apps\\lib")

try:
    import pattern_maker_left
    reload(pattern_maker_left)
    from pattern_maker_left import TYPE_DEFINITIONS, get_type_by_color
except:
    pass

from EnneadTab import EXCEL, NOTIFICATION

def get_location_map(max_x, max_y, sheet_name, is_header=False):
    """Return a dict of location and type based on excel data, expanded to fill max dimensions.
    
    The function reads data from excel and expands it to fill the requested dimensions
    by repeating the pattern as needed.
    
    Args:
        max_x (int): Maximum x coordinate to fill
        max_y (int): Maximum y coordinate to fill
        
    Returns:
        dict: Key is (x,y) tuple, value is type string from excel data
    """
    excel_path = "J:\\2128\\1_Study\\EA 2025-02-24 Tile Pattern\\Tile Study.xlsx"

    raw_data = EXCEL.read_data_from_excel(excel_path,
                                      worksheet=sheet_name,
                                      return_dict=True)
    # Process initial data
    base_pattern_data = {}
    bad_data_found = False


    def is_color_same(color1, color2):
        return color1[0] == color2[0] and color1[1] == color2[1] and color1[2] == color2[2]

    def is_process_zone(row, col):
        if is_header:
            if 120 >= col >= 59 and row <= 3:
                return True
            return False
        else:
            if 57 >= col and row <= 14:  # column "BE" max
                return True
            return False

    for key in sorted(raw_data.keys()):
        row, col = key
        if is_process_zone(row, col):
            raw_key = (row, col)
            human_key = (row, EXCEL.column_number_to_letter(col))
            # print ("%%%%%%")
            # print (raw_key)
            # print (human_key)

            excel_cell_color = raw_data[key]["color"]
            # print ("excel_cell_color at {} is : ".format(human_key), excel_cell_color)
            excel_cell_value = raw_data[key]["value"]
            # print ("excel_cell_value at {} is : ".format(human_key), excel_cell_value)
            type_lookup_data = TYPE_DEFINITIONS[excel_cell_value] # this is gettting the definition what excel claim the type to be 
            if not is_color_same(type_lookup_data['color'], excel_cell_color):
                print ("Color mismatch for {}, your excel is not correct at {}".format(excel_cell_value, human_key))
                print ("type_lookup_data['color'] is : ", type_lookup_data['color'])
                print ("excel_cell_color is : ", excel_cell_color)

                bad_data_found = True
            looked_up_type = get_type_by_color(excel_cell_color)
            if looked_up_type is None:
                print ("Type lookup failed for {}, your excel is not correct at {}".format(excel_cell_value, human_key))
                bad_data_found = True
                looked_up_type = TYPE_DEFINITIONS.keys()[0]

            # flip the pattern upside down
            if is_header:
                row = 4-row 
            else:
                row = 15-row
                
            new_key = (col-1, row-1)
            base_pattern_data[new_key] = looked_up_type
    
    # Get pattern dimensions
    pattern_width = max(x for x, _ in base_pattern_data.keys()) + 1
    pattern_height = max(y for _, y in base_pattern_data.keys()) + 1
    
    # Create expanded location map
    location_map = {}
    for y in range(max_y):
        for x in range(max_x):
            # Map coordinates to pattern coordinates
            pattern_x = x % pattern_width
            pattern_y = y % pattern_height
            
            # Copy value from pattern
            if (pattern_x, pattern_y) in base_pattern_data:
                location_map[(x, y)] = base_pattern_data[(pattern_x, pattern_y)]
    
    if bad_data_found:
        NOTIFICATION.messenger("Bad data found, please check your excel")
    return location_map

if __name__ == "__main__":
    excel_path = "J:\\2128\\1_Study\\EA 2025-02-24 Tile Pattern\\Tile Study.xlsx"

    raw_data = EXCEL.read_data_from_excel(excel_path,
                                      worksheet="Sheet1",
                                      return_dict=True)

    for key in sorted(raw_data.keys()):
        print (key, raw_data[key])


