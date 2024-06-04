
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
from collections import OrderedDict

sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

from EnneadTab import EXCEL


@EnneadTab.ERROR_HANDLE.try_catch_error
def excel2shape():
    excel = "J:\\2412\\2_Master File\\B-70_Programming\\01_Program & Analysis\\01_Working\\2024-06-03 Preliminary Zoning + Category Level Program.xls"
    color_dict = EXCEL.read_data_from_excel(excel, "Category Level Program", return_dict=True)
    lines = EXCEL.read_data_from_excel(excel, "Category Level Program")
            

    line_headers = lines[2]
    headers = OrderedDict()
    for i, item in enumerate(line_headers):
        if item != "":
            headers[item] = {"value":i,
                             "color":color_dict[(2, i)]["color"]}


    # print (headers)



    data = OrderedDict()
    lines = lines[4:13]
    for line in lines:
        # print(line)

        department = line[EXCEL.letter_to_index("B")]
        temp_data = {"value": OrderedDict(),
                     "color": None}

        for header in headers.keys():
            column = headers[header]["value"]
            area = line[column+1]
            try:
                area = float(area)
            except:
                area = 0
            temp_data["value"][header] = area

        for item in color_dict.values():
            if item["value"] == department:
                temp_data["color"] = item["color"]

        data[department] = temp_data



    print (data)





    width = 150

    # stack 1
    collection = [] 
    pointer_x = 0
    pointer_y = 0
    for department in data.keys():
        total = 0
        
        color = data[department]["color"]
        print (color)
        for header, area in data[department]["value"].items():
            if area != 0:
                total += area
                print (department, header, area)
                height = area/width
                
                border = rs.AddRectangle(rs.CreatePlane((pointer_x, pointer_y, 0)), width, height)
                shape = rs.AddPlanarSrf(border)
                text = rs.AddText("{}: {}".format(header, int(area)), (pointer_x, pointer_y+15, 0))
                rs.DeleteObject(border)
                collection.append(shape)
                collection.append(text)
                rs.ObjectColor(shape, color)
                pointer_y += height

        pointer_y = 0
        title = rs.AddText("{}: {}".format(department, int(total)), (pointer_x, pointer_y-20, 0), height=2)
        collection.append(title)
        pointer_x += width*1.5

    rs.MoveObjects(collection, (0, 1500, 0))

    # stack 2
    collection = [] 
    pointer_x = 0
    pointer_y = 0
    for department in data.keys():
        total = 0
        
 
        for header, area in data[department]["value"].items():
            if area != 0:
                color = headers[header]["color"]
                total += area
                print (department, header, area)
                height = area/width
                
                border = rs.AddRectangle(rs.CreatePlane((pointer_x, pointer_y, 0)), width, height)
                shape = rs.AddPlanarSrf(border)
                text = rs.AddText("{}: {}".format(header, int(area)), (pointer_x, pointer_y+15, 0))
                rs.DeleteObject(border)
                collection.append(shape)
                collection.append(text)
                rs.ObjectColor(shape, color)
                pointer_y += height

        pointer_y = 0
        title = rs.AddText("{}: {}".format(department, int(total)), (pointer_x, pointer_y-20, 0), height=2)
        collection.append(title)
        pointer_x += width*1.5

    rs.MoveObjects(collection, (3000, 1500, 0))


    #  stack 3
    collection = [] 
    pointer_x = 0
    pointer_y = 0
    for working_header in headers.keys():
        total = 0
        for department in data.keys():
            color = data[department]["color"]
            for header, area in data[department]["value"].items():
                if header == working_header:
                    break
            if area != 0:
                total += area
      
                print (department, header, area)
                height = area/width
                
                border = rs.AddRectangle(rs.CreatePlane((pointer_x, pointer_y, 0)), width, height)
                shape = rs.AddPlanarSrf(border)
                text = rs.AddText("{}: {}".format(department, int(area)), (pointer_x, pointer_y+15, 0))
                rs.DeleteObject(border)
                collection.append(shape)
                collection.append(text)
                rs.ObjectColor(shape, color)
                pointer_y += height

        pointer_y = 0
        title = rs.AddText("{}: {}".format(header, int(total)), (pointer_x, pointer_y-20, 0), height=2)
        collection.append(title)
        pointer_x += width*1.5
    rs.MoveObjects(collection, (0, 0, 0))
 
    #  stack 4
    collection = [] 
    pointer_x = 0
    pointer_y = 0
    for working_header in headers.keys():
        total = 0
        for department in data.keys():
            color = headers[working_header]["color"]
            for header, area in data[department]["value"].items():
                if header == working_header:
                    break
            if area != 0:
                total += area
      
                print (department, header, area)
                height = area/width
                
                border = rs.AddRectangle(rs.CreatePlane((pointer_x, pointer_y, 0)), width, height)
                shape = rs.AddPlanarSrf(border)
                text = rs.AddText("{}: {}".format(department, int(area)), (pointer_x, pointer_y+15, 0))
                rs.DeleteObject(border)
                collection.append(shape)
                collection.append(text)
                rs.ObjectColor(shape, color)
                pointer_y += height

        pointer_y = 0
        title = rs.AddText("{}: {}".format(header, int(total)), (pointer_x, pointer_y-20, 0), height=2)
        collection.append(title)
        pointer_x += width*1.5
    rs.MoveObjects(collection, (3000, 0, 0))
######################  main code below   #########
if __name__ == "__main__":
    excel2shape()


