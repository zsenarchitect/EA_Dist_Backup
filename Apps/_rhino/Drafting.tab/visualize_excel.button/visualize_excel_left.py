__title__ = "VisualizeExcel"
__doc__ = """Convert Excel data into visual diagrams.

Key Features:
- Multiple shape options (circles, squares, bars)
- Customizable colors and sizes
- Automatic area calculations
- Support for grouped data visualization
- Dynamic layout adjustments."""
__is_popular__ = True

import rhinoscriptsyntax as rs
import math
import textwrap


from EnneadTab import NOTIFICATION
from EnneadTab import DATA_FILE
from EnneadTab import EXCEL
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def visualize_excel():
    ShapeWriter().write_shape()

class ShapeWriter:

    @staticmethod
    def get_edge_L_from_area(area):
        return math.sqrt(area)
    
    @staticmethod
    def get_r_from_area(area):
        return math.sqrt(area/math.pi)

    @staticmethod
    def secure_text(input_text):
        return input_text
        """convert the unicode object to pythong string that can be displayed properly

        Args:
            input_text (str): _description_

        Returns:
            str: secured text
        """
        # print input_text
        # print type(input_text)
        
        if EnneadTab.USER.IS_DEVELOPER:
            filepath = EnneadTab.FOLDER.get_local_dump_folder_file("excel_area_data.txt")
            
       
            EnneadTab.DATA_FILE.set_list([input_text], filepath, end_with_new_line = False)
            text = EnneadTab.DATA_FILE.get_list(filepath)
            return text[0]
            return EnneadTab.UNICODE.convert_unicode_to_string(input_text)
        else:
            return input_text
        # wrapper = textwrap.TextWrapper(width = 100)

        # return wrapper.fill(text = "".format(input_text))

    @staticmethod
    def extract_value(data_item):
        """Extract value from data item, handling both old list format and new dictionary format"""
        if isinstance(data_item, dict):
            return data_item.get('value', None)
        return data_item

    @staticmethod
    def extra_info( data):
        # print ('############')  # Removed debug print

        # print (type(data[0]))
        # Handle both old list format and new dictionary format
        cate = ShapeWriter.secure_text(ShapeWriter.extract_value(data[0]))
        room = ShapeWriter.secure_text(ShapeWriter.extract_value(data[1]))
        try:
            area_value = ShapeWriter.extract_value(data[2])
            area = float(area_value)
        except:
            return cate, None, None, None, 1
        
        # Extract color values 
        color_values = []
        for i in range(3, 6):  # data[3], data[4], data[5]
            if i < len(data):
                color_val = ShapeWriter.extract_value(data[i])
                color_values.append(color_val)
            else:
                color_values.append(None)
        
        color = color_values
        try:
            color = map(lambda x: int(x) if x is not None else 0, color)
        except:
            print(color_values)
            rs.MessageBox("This color data cannot read. [{}]".format(cate))
        
        try:
            if len(data) > 8:
                count_value = ShapeWriter.extract_value(data[8])
                if count_value == "" or count_value is None:
                    count = 1
                else:
                    count = int(count_value)
            else:
                count = 1
        except:
            count = 1
        return cate, room, area, color, count



    def __init__(self):
        path = rs.OpenFileName("Pick the source file for excel area data", filter= "Excel files (*.xlsx)|*.xlsx")
        
        if not path:
            return
        all_sheets = EXCEL.get_all_worksheets(path)
        sheet = rs.ListBox(all_sheets, "Pick the sheet for excel area data", title="EnneadTab Visualize Excel")
        if not sheet:
            return
        self.datas = EXCEL.read_data_from_excel(path, worksheet = sheet)
        # print self.datas
        
        # filepath = EnneadTab.FOLDER.get_local_dump_folder_file("excel_area_data.txt")
        # for i, entry in enumerate(self.datas):
        #     text, num = entry[:2], entry[2:]
        #     EnneadTab.DATA_FILE.set_list(text, filepath, end_with_new_line = False)
        #     text = EnneadTab.DATA_FILE.get_list(filepath)
        #     self.datas[i] = text + num
        
        opt = rs.ListBox(["Circle", "Square", "Bar"], "What shape to use?",  title="EnneadTab Visualize Excel")
        self.basic_shape = opt
        if opt == "Bar":
            self.fix_bar_width = rs.RealBox("What is the width of the bar?")



    
        self.pointer = [0,0,0]
        self.big_title_offset = DATA_FILE.get_sticky("viz_excel_big_title_offset", 100)
        self.small_title_offset = DATA_FILE.get_sticky("viz_excel_small_title_offset", 50)
        self.caption_text_drop = DATA_FILE.get_sticky("viz_excel_caption_text_drop", 10)
        self.row_gap = DATA_FILE.get_sticky("viz_excel_row_gap", 60)
        self.column_gap = DATA_FILE.get_sticky("viz_excel_column_gap", 40)
        self.use_hori = DATA_FILE.get_sticky("viz_excel_use_hori", 1)
        
        para_list = ["big_title_offset", "small_title_offset", "caption_text_drop", "row_gap", "column_gap", "use_hori"]
        
        res = rs.PropertyListBox(items = ["Big Title Offset", "Small Title Offset", "Caption Offset", "Row Gap", "Column Gap", "Use Horitional(1 = Yes, 0 = No)"],
                            values = [getattr(self, x) for x in para_list],
                            message = "Enter Data for Visualization Shape Control",
                            title = "Visualize Excel Area")
        if not res:
            return
        for i, x in enumerate(para_list):
            setattr(self, x, float(res[i]))
            
            DATA_FILE.set_sticky("viz_excel_" + x , float(res[i]))
        
        
        self.current_small_category = None
  
        self.is_first_row = True
        self.is_first_column = True
        rs.EnableRedraw(False)
        
    def write_shape(self):
        if not hasattr(self, "datas"):
            NOTIFICATION.messenger(main_text="Excel data not read.")
            return
        map(self.process_data, self.datas)
        


    def process_data(self, data):
        
        # print ("\n\nnew data = " + str(data))  # Removed debug print

        # Check for empty data - handle both old list format and new dictionary format
        if len(data) == 0:
            return
            
        # Check if all values are empty/None
        all_empty = True
        for item in data:
            value = ShapeWriter.extract_value(item)
            if value not in ["", None, "None"]:
                all_empty = False
                break
        if all_empty:
            return
            
        # Check for big title condition
        data_2_value = ShapeWriter.extract_value(data[2]) if len(data) > 2 else ""
        data_0_value = ShapeWriter.extract_value(data[0]) if len(data) > 0 else ""
        
        if (data_2_value == "" or data_2_value == "Area" or data_2_value is None) and data_0_value != "":
            self.make_big_title_text(data)
            return
            
        # print(data)  # Removed debug print
        # print (type(data))  # Removed debug print
        cate, room, area, color, count = ShapeWriter.extra_info(data)
        
        # Add check for None area to prevent TypeError
        if area is None:
            print("Skipping data entry '{}' because area could not be parsed.".format(cate))
            return
            
        if room == "":
            room = cate
        center = [0,0,0]
        
        # print cate, room, area, color, count
        srfs = []
        for i in range(count):
          
            
            x = i % 5
            y = int(i / 5)
            if self.use_hori and count > 25:
                x, y = y, x
            
            if self.basic_shape == "Square":
                L = ShapeWriter.get_edge_L_from_area(area)
                pts = [[L/2, L/2, 0],
                        [-L/2, L/2, 0],
                        [-L/2, -L/2, 0],
                        [L/2, -L/2, 0]]
                pts = [rs.PointAdd(pt, [x * L, y * L, 0]) for pt in pts]
                srfs.append(rs.AddSrfPt(pts))
                abstract_gap = L/2 
                
                
            elif self.basic_shape == "Circle":
                r = ShapeWriter.get_r_from_area(area)
                center = rs.PointAdd([0,0,0], [x * r * 2 , y * r * 2, 0])
                circle = rs.AddCircle(center, r)
                srfs.append( rs.AddPlanarSrf(circle))
                rs.DeleteObject(circle)
                abstract_gap = r 

            elif self.basic_shape == "Bar":
                W = self.fix_bar_width
                L = area/W
                pts = [[W/2, L/2, 0],
                        [-W/2, L/2, 0],
                        [-W/2, -L/2, 0],
                        [W/2, -L/2, 0]]
                pts = [rs.PointAdd(pt, [x * W, y * L, 0]) for pt in pts]
                srfs.append(rs.AddSrfPt(pts))
                abstract_gap = W/2
        
        
        caption_text_drop = max(self.caption_text_drop, abstract_gap + 5)
            
            
        [rs.ObjectColorSource(srf, 1) for srf in srfs]
        [rs.ObjectColor(srf, color) for srf in srfs]




        

        text_center = [0, -caption_text_drop, 0]
        note = int(area) if count == 1 else "{} x {}".format(int(area), count)
        text = rs.AddText("{}\n{}".format(room, note), text_center, justification = 2)


        collection = [text]
        collection.extend(srfs)


        group = rs.AddGroup()
        rs.AddObjectsToGroup(collection,group)

        if cate != self.current_small_category:   
            self.make_small_title_text(cate)
    
        if self.is_first_column:
            self.is_first_column = False
        else:
            self.pointer = rs.PointAdd(self.pointer, [self.column_gap, 0, 0])
            
        self.pointer = rs.PointAdd(self.pointer, [abstract_gap, 0, 0])
        rs.MoveObjects(collection, self.pointer)

       



    def make_small_title_text(self, cate):

 
        # Wrap this text.

        wrapper = textwrap.TextWrapper(width = 12)

        cate_new = wrapper.fill(text = cate)

        self.current_small_category = cate_new
        """
        if len(cate) > 12:
            cate = cate.replace(" ", "\n")
        """

    
        if self.is_first_row:
            self.pointer =[0,self.pointer[1],0]
            self.is_first_row = False
        else:
            self.pointer = rs.PointAdd([0,self.pointer[1],0], [0, -self.row_gap, 0])   
            
        small_title_location = rs.PointAdd([0,self.pointer[1], 0], [-self.small_title_offset, 0, 0])
        try:
            rs.AddText(cate_new, small_title_location, height = 2)
        except:
            rs.AddText(cate, small_title_location, height = 2)
        self.is_first_column = True

    def make_big_title_text(self, data):
        title_value = ShapeWriter.extract_value(data[0]) if len(data) > 0 else ""
        title = ShapeWriter.secure_text(title_value)
        
        # Get area from data[6] if available, handle dictionary format
        area_raw = ShapeWriter.extract_value(data[6]) if len(data) > 6 else None
        
        # Add protection against invalid area values
        try:
            area_value = float(area_raw) if area_raw else 0
        except (ValueError, TypeError):
            area_value = 0

        
        # Wrap this text.
        wrapper = textwrap.TextWrapper(width = 12)

        title_new = wrapper.fill(text = title)
        self.current_big_category = title_new
        """
        if len(cate) > 12:
            cate = cate.replace(" ", "\n")
        """
        # print ("#######")  # Removed debug print
        # print (title_new)  # Removed debug print
        big_title_location = rs.PointAdd([0,self.pointer[1], 0], [-self.big_title_offset, 0, 0])
        if self.is_first_row:
            pass
        else:
            big_title_location = rs.PointAdd(big_title_location, [0, -self.row_gap, 0])   
            

        try:
            rs.AddText(title_new, big_title_location, height = 3)
        except:
            rs.AddText(title, big_title_location, height = 3)
        rs.AddText(str(int(area_value)), rs.PointAdd(big_title_location, [0, -self.row_gap*0.5, 0]), height = 3)

if __name__ == "__main__":
    visualize_excel()