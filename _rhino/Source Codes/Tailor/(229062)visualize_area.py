import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab
import math

def get_r_from_area(area):
    return math.sqrt(area/math.pi)

def make_cate_title_text(cate):
    global POSITION_X
    global POSITION_Y
    import textwrap

    # Wrap this text.
    wrapper = textwrap.TextWrapper(width = 12)

    cate = wrapper.fill(text = cate)
    """
    if len(cate) > 12:
        cate = cate.replace(" ", "\n")
    """
    rs.AddText(cate, [POSITION_X - 250, POSITION_Y, 0], height = 2)

def make_big_title_text(data):
    title = data[0]
    area = data[-1]
    title = "{}\n{}".format(title, int(area))
    global POSITION_X
    global POSITION_Y
    import textwrap
    # Wrap this text.
    wrapper = textwrap.TextWrapper(width = 12)

    cate = wrapper.fill(text = title)
    """
    if len(cate) > 12:
        cate = cate.replace(" ", "\n")
    """
    print("#######")
    print(title)
    global VERTICAL_STEP
    rs.AddText(title, [POSITION_X - 1000, POSITION_Y - VERTICAL_STEP, 0], height = 3)

def extra_info(data):
    global IS_EXCEL
    if IS_EXCEL:
        cate = data[0]
        room = data[1]
        area = float(data[2])
        color = [data[3], data[4],data[5]]
        color = map(lambda x: int(x), color)
        return cate, room, area, color

    cate = data.split("#")[0]
    room = data.split("#")[1]
    area = float(data.split("#")[2])
    color = data.split("#")[3].replace("[", "").replace("]","").split(",")
    color = map(lambda x: int(x), color)
    return cate, room, area, color



def process_data(data):
    print("@@@@@")
    print("new data = " + str(data))

    if data == ["","","","","","",""]:
        return
    if data[2] == "" and data[0] != "":
        make_big_title_text(data)
        return
    cate, room, area, color = extra_info(data)
    if room == "":
        room = cate
    center = [0,0,0]
    r = get_r_from_area(area)
    circle = rs.AddCircle(center, r)
    circle_srf = rs.AddPlanarSrf(circle)
    rs.ObjectColorSource(circle_srf, 1)
    rs.ObjectColor(circle_srf, color)
    rs.DeleteObject(circle)


    text_center = [0, -120, 0]
    text = rs.AddText("{}\n{}".format(room, int(area)), text_center, justification = 2)



    collection = [text, circle_srf]


    group = rs.AddGroup()
    rs.AddObjectsToGroup(collection,group)

    global ROW_CATE
    global POSITION_X
    global POSITION_Y
    global VERTICAL_STEP
    if cate != ROW_CATE:
        POSITION_X = 0
        POSITION_Y -= VERTICAL_STEP
        ROW_CATE = cate
        make_cate_title_text(cate)
    POSITION_X += r
    translation = [POSITION_X, POSITION_Y, 0]
    rs.MoveObjects(collection, translation)
    POSITION_X += r + 50# 50 for the gap
    pass

@EnneadTab.ERROR_HANDLE.try_catch_error
def Run():
    global POSITION_X
    global POSITION_Y
    global ROW_CATE
    global VERTICAL_STEP
    POSITION_X = 0
    POSITION_Y = 0
    ROW_CATE = ""
    VERTICAL_STEP = 300


    path = r"C:\Users\szhang\Desktop\room_area.txt"
    path = r"J:\Ennead Promotional Work\bmasuda\229062_area chart\Progam Spreadsheet_Grasshopper.xlsx"
    path = rs.OpenFileName()
    if EnneadTab.USER.is_SZ():
        pass
        #path = r"C:\Users\szhang\Downloads\Progam Spreadsheet_Grasshopper_study.xlsx"
    global IS_EXCEL
    IS_EXCEL = True
    if ".txt" in path:
        IS_EXCEL = False


    if IS_EXCEL:
        worksheet = rs.StringBox("worksheet name to import from", default_value = "Sheet1", title = "visualize area by circle")
        content = EnneadTab.EXCEL.read_data_from_excel(path, worksheet = worksheet)
    else:
        content = EnneadTab.DATA_FILE.read_txt_as_list(path)

    print(content)
    map(process_data, content)
    #print content





######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    Run()
