#!/usr/bin/python
# -*- coding: utf-8 -*-


try:
    import inspect
 
    def get_caller_file_path():
        #stack = inspect.stack()
        #caller_frame = stack[2]
        #caller_file_path = caller_frame[1]  # The filename is the second element in the tuple
        OUT = ""
        for x in inspect.stack():
            OUT += str(x) + "\n"
        return OUT
        #return caller_file_path

    
    
    # import EnneadTab
    # EnneadTab.EMAIL.email(sender_email=None,
    #                     receiver_email_list=["szhang@ennead.com"],
    #                     subject="EnneadTab Auto Email: EA_UTILITY Detected",
    #                     body="EA_UTILITY is called from {}".format(get_caller_file_path()),
    #                     body_folder_link_list=None,
    #                     body_image_link_list=None,
    #                     attachment_list=None,
    #                     schedule_time=None)
except Exception as e:
    print( str(e))
finally:
    pass
    #print "EA_UTILITY loaded, this should not happen!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"


try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except:
    #print "[Debug Note]: cannot load rhinoscriptsyntax and/or script context"
    pass


""""""
def try_catch_error(func):
    import traceback
    def wrapper(*args, **kwargs):

        print_note ("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
            print_note ( "Wrapper func for EA Log -- Finish:")
            return out
        except Exception as e:
            print_note ( str(e))
            print_note (  "Wrapper func for EA Log -- Error: " + str(e)  )
            error = traceback.format_exc()
            error_file = "{}\error_log.txt".format(get_user_folder())
            with open(error_file, "w") as f:
                f.write(error)
            open_file_in_default_application(error_file)
    return wrapper


"""
math and misc
"""
""""""
def is_current_enneadtab_on_main_rui():

    current_rui = rs.ToolbarCollectionPath("EnneadTab")
    main_rui = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\EnneadTab for Rhino\EnneadTab.rui"
    if current_rui == main_rui:
        #print current_rui
        toast(title = "Your EnneadTab is added but not registered.", message = "Please go to EnneadTab menu-->User Get Latest.")
        help_file = r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Manager\register_enneadtab.pdf'
        open_file_in_default_application(help_file)
        return True
    return False

""""""
def is_selection_not_valid(obj, note = "Nothing is selected."):
    if not obj:
        toast(title = note, message = "Action Cancelled")
        return False
    return True


def need_to_get_latest_ennadtab():
    toast(title = "Your EnneadTab version is behind.", message = "Please get latest by going to EnneadTab menu-->User Get Latest.")

""""""
def give_me_a_joke(talk = False, max_len = None):
    import sys
    sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Fun\jokes')
    import JOKES

    joke =  JOKES.random_joke()
    if not max_len:
        import textwrap as TW
        wrapper = TW.TextWrapper(width = 70)
        temp = ""
        for line in wrapper.wrap(joke):
            temp += line + "\n"
        joke = temp


    if talk:
        speak(joke.replace("\n", " "))
    return joke.replace("\n", " ")

""""""
def speak(text, language = 'en', accent = 'com'):
    """
    #language = 'zh-CN'
    #language = 'zh-TW'
    #language = 'en'

    #accent = 'co.uk'
    #accent = 'co.in'
    #accent = 'com'
    """
    if text:
        data = dict()
        data["text"] = text
        data["language"] = language
        data["accent"] = accent
        file_name = "EA_Text2Speech.json"
        dump_folder = get_EA_local_dump_folder()
        file_path = "{}\{}".format(dump_folder, file_name)
        save_dict_to_json(data, file_path)

    try:
        import imp
        full_file_path = r'C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Utility.panel\exe_1.stack\text2speech.pushbutton\TTS_script.py'
        if not is_SZ():
            full_file_path = remap_filepath_to_Rhino_folder(full_file_path)
        ref_module = imp.load_source("TTS_script", full_file_path)

        ref_module.run_exe()


    except:
        exe_location = "L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\EA_TEXT2SPEECH\EA_TEXT2SPEECH.exe"

        try:
            open_file_in_default_application(exe_location)
        except Exception as e:
            print(exe_location)
            print(str(e))


def remap_filepath_to_Rhino_folder(full_file_path):
    """
    remap  sccript path that point to Sen document---->to L drive
    """
    return full_file_path.replace(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension", r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Published\ENNEAD.extension")

""""""
def email_error(traceback, tool_name, error_from_user, subject_line = "EnneadTab Auto Email Error Log"):

    import time
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    body = "{}\nError happens on {}'s machine when running {}.\n\nDetail below:\n{}'".format(t, error_from_user, tool_name, traceback)
    email(sender_email = None,
            receiver_email_list = ["szhang@ennead.com"],
            subject = subject_line,
            body = body,
            body_folder_link_list = None,
            body_image_link_list = None,
            attachment_list = None,
            schedule_time = None)

""""""
def email(sender_email = None,
        receiver_email_list = None,
        subject = "EnneadTab Auto Email",
        body = None,
        body_folder_link_list = None,
        body_image_link_list = None,
        attachment_list = None,
        schedule_time = None):
    """sender email is not required for outlook approch
    schedule time is the desired time in uni seconds
    """


    if not receiver_email_list:
        return
    if isinstance(receiver_email_list, str):
        print("Prefer list but ok.")
        receiver_email_list = receiver_email_list.rstrip().split(";")

    if not body:
        return

    body = body.replace("\n", "<br>")


    data = dict()
    data["sender_email"] = sender_email
    data["receiver_email_list"] = receiver_email_list
    data["subject"] = subject
    data["body"] = body
    data["body_folder_link_list"] = body_folder_link_list
    data["body_image_link_list"] = body_image_link_list
    data["attachment_list"] = attachment_list
    data["schedule_time"] = schedule_time


    file_name = "EA_EMAIL.json"
    dump_folder = get_EA_local_dump_folder()
    file_path = "{}\{}".format(dump_folder, file_name)
    save_dict_to_json(data, file_path)


    exe_location = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\lib\EA_EMAIL\EA_EMAIL.exe"

    try:
        open_file_in_default_application(exe_location)
    except Exception as e:
        print(exe_location)
        print(str(e))

""""""
def pay_attention(objs, time = 25, visibility = True, selection = True, zoom_selected = True):
    """zoom flash"""

    original_state = rs.EnableRedraw(True)
    if zoom_selected:
        #rs.UnselectAllObjects()
        rs.SelectObjects(objs)
        rs.ZoomSelected()
        rs.UnselectObjects(objs)


    if objs:
        if visibility:
            for i in range(time):
                rs.FlashObject(objs, style = False)
        if selection:
            for i in range(time):
                rs.FlashObject(objs, style = True)
    rs.EnableRedraw(original_state)

def play_sound(file = "sound effect_popup msg3.wav"):
    # import sys
    # sys.path.append("..\lib")
    # import EA_SOUND
    # EnneadTab.SOUNDS.play_sound(file)
    return

""""""
def open_file_in_default_application(filepath):
    #subprocess.call('C:\Program Files\Rhino 7\System\Rhino.exe')
    #import subprocess, os
    import  os
    os.startfile(filepath)

def has_any_keyword(input, keywords):
    for keyword in keywords:
        if keyword in input.lower():
            return True
    return False


def test():
    print("in func")


def print_list(list):
    temp = ""
    for x in list:
        temp += str(x) + "\n"
    rs.TextOut(message = temp)


def map_num_linear(X, x0, x1, y0, y1):
    """
    x0, x1 ---> input range
    y0, y1 ---> output range
    """
    k = (y1 - y0) / (x1 - x0)
    b = y0 - k * x0
    #print k
    #print b
    Y = k * float(X) + b
    return Y


def map_num_with_clamp(X, x0, x1, y0, y1, clamp0, clamp1):
    """
    if clamp0 < x0 or clamp1 > x1:
        #raise ClampError('clamps must be between input range')
        print("clamp error")
        return None
    """
    """
    X = max(X, clamp0)
    X = min(X, clamp1)
    """
    if X < clamp0:
        return y0
    if X > clamp1:
        return y1
    return map_num_linear(X, clamp0, clamp1, y0, y1)

""""""
def print_note(note):
    if is_SZ():
        print("[Debug Note]: {}".format(note))

def filter_by_mask(X, Y):
    """
    X ---> obj list
    Y ---> boolean list
    """
    OUT = []
    for a, b in zip(X, Y):
        if b:
            OUT.append(a)
    return OUT


"""
export and reading, stickys
"""

""""""
def read_json_as_dict(filepath):
    import json
    # reads it back
    with open(filepath,"r") as f:
      dict = json.load(f)
    return dict

""""""
def save_dict_to_json(dict, filepath):
    import json
    # write to a file
    with open(filepath,"w") as f:
      json.dump(dict, f)



""""""
def read_txt_as_list(filepath = "path", use_encode = False):
    if use_encode:
        import io
        with io.open(filepath, encoding = "utf8") as f:
            lines = f.readlines()
    else:
        with open(filepath) as f: #encoding = "utf8"
            lines = f.readlines()
    return map(lambda x: x.replace("\n",""), lines)

""""""
def save_list_to_txt(list, filepath, end_with_new_line = False):
    with open(filepath, 'w') as f:
        # f.writelines(list)
        f.write('\n'.join(list))
        if end_with_new_line:
            f.write("\n")

""""""
def read_txt_as_dict(filepath = "path", use_encode = False):
    if use_encode:
        import io
        with io.open(filepath, encoding = "utf8") as f:
            lines = f.readlines()
    else:
        with open(filepath) as f: #encoding = "utf8"
            lines = f.readlines()
    return eval(lines[0])


def save_dict_to_txt(dict, filepath, end_with_new_line = False):
    with open(filepath, 'w') as f:
        # f.writelines(list)
        f.write(str(dict))
        if end_with_new_line:
            f.write("\n")

""""""
def copy_file(original_path, target_path):
    import shutil
    shutil.copyfile(original_path, target_path)

""""""
def copy_file_to_folder(original_path, target_folder):
    import shutil
    new_path = original_path.replace(get_folder_name_from_path(original_path), target_folder)
    try:
        shutil.copyfile(original_path, new_path)
    except Exception as e:
        print(e)

""""""
def read_file_safely(original_path, file_name = None):
    #print original_path
    if file_name is None:
        file_name = original_path.rsplit("\\", 1)[1]
    local_folder = get_EA_setting_folder() + "\\" + "Local Copy Dump"
    local_folder = secure_folder(local_folder)
    local_path = "{}\{}".format(local_folder, file_name)
    import shutil
    shutil.copyfile(original_path, local_path)
    #print "###"
    #print local_path
    content = read_txt_as_list(local_path)
    return content


""""""
def read_data_from_excel(filepath, worksheet = "Sheet1", by_line = True):
    import sys
    reload(sys)
    # 设定了输出的环境为utf8
    sys.setdefaultencoding('utf-8')
    import sys
    import EnneadTab
    sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
    import xlrd


    wb = xlrd.open_workbook(filepath)#, encoding_override = "cp1252")#""big5")#"iso2022_jp_2")#"gb18030")#"gbk")#"hz")  #"gb2312")   #"utf8"
    try:
        sheet = wb.sheet_by_name(worksheet)
    except:
        rs.MessageBox("Cannot open worksheet: {}".format(worksheet))
        return None
    #print sheet.cell_value(2, 1)
    OUT = []

    for i in range(0, sheet.nrows):
        OUT.append(sheet.row_values(i))
    return OUT

""""""
def save_data_to_excel(data, filepath, worksheet = "EnneadTab", open_after = True):
    import sys
    reload(sys)
    # 设定了输出的环境为utf8
    sys.setdefaultencoding('utf-8')
    import sys
    import EnneadTab
    sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
    import xlsxwriter as xw




    def write_data_item(worksheet, data):
        worksheet.write(data.row,
                        data.column,
                        data.item)

    workbook = xw.Workbook(filepath)
    worksheet = workbook.add_worksheet(worksheet)
    for data_entry in data:
        write_data_item(worksheet, data_entry)


    column_max_width_dict = dict()
    for entry in data:
        column, item = entry.column, entry.item
        if column not in column_max_width_dict.keys():
            column_max_width_dict[column] = 0
        column_max_width_dict[column] = max(column_max_width_dict[column], 1.2 * len(str(item)))

    for column in column_max_width_dict.keys():
        worksheet.set_column(column,column , column_max_width_dict[column])


    try:
        workbook.close()
        if not open_after:
            notification(main_text = "Excel saved at '{}'".format(filepath), height = 500)
    except:
        notification(main_text = "the excel file you picked is still open, cannot override. Writing cancelled.", height = 500)
        return

    if open_after:
        open_file_in_default_application(filepath)
    """
    def SampleExportUTF8():

        # extract texts in the model
        textList = []
        for o in rs.AllObjects():
            if rs.IsText(o):
            	# explicitly encode to utf-8
                s = rs.TextObjectText(o).encode('utf-8')
                textList.append(s)

        # create a filename variable
        path = System.Environment.GetFolderPath(System.Environment.SpecialFolder.Desktop)
        filename = System.IO.Path.Combine(path, 'SampleExportUTF8.csv');

        file = open(filename, 'w')

        # create and write a header for the CSV file
        headerList = [u'Index',u'中国',u'English',u'Français']

        # explicitly encode to utf-8
        headerList = [i.encode('utf-8') for i in headerList]
        header = u"{}\n".format(u';'.join(headerList))
        file.write(header)

        # create and write a line in CSV file for every text in the model
        lineList=[]
        i = 0
        for text in textList:
            line = [str(i),text]
            i += 1
            lineList.append(line)

        for line in lineList:
            fileLine = u';'.join(line)+u'\n'
            file.write(fileLine)

        file.close()
    """
    pass



def get_sticky(sticky_name, default_value_if_no_sticky):
    if sc.sticky.has_key(sticky_name):
        return sc.sticky[sticky_name]
    else:
        return default_value_if_no_sticky


def set_sticky(sticky_name, value_to_write):
    sc.sticky[sticky_name] = value_to_write


def get_sticky_longterm(sticky_name, default_value_if_no_sticky):
    folder = get_EA_setting_folder() + "\Longterm Sticky"
    #print folder
    folder = secure_folder(folder)
    file = folder + "\\" + sticky_name + ".STICKY"
    #print file
    #print sticky_name
    #print "***"
    #print get_filenames_in_folder(folder)
    if sticky_name + ".STICKY" not in get_filenames_in_folder(folder):
        print("stickyname not found in folder")
        set_sticky_longterm(sticky_name, default_value_if_no_sticky)
        return default_value_if_no_sticky
    content = read_txt_as_list(file)
    #print "****"
    #print value
    if content is None or len(content) == 0:
        set_sticky_longterm(sticky_name, default_value_if_no_sticky)
        return default_value_if_no_sticky
    else:
        if len(content) == 1:
            set_sticky_longterm(sticky_name, content[0])
            return content[0]
        value, type = content
        if type == "float":
            value = float(value)
        if type == "int":
            value = int(value)
        return value


def set_sticky_longterm(sticky_name, value_to_write):
    type = "string"
    if isinstance(value_to_write, float):
        type = "float"
    if isinstance(value_to_write, int):
        type = "int"
    folder = get_EA_setting_folder() + "\Longterm Sticky"
    folder = secure_folder(folder)
    file = folder + "\\" + sticky_name + ".STICKY"
    save_list_to_txt([str(value_to_write), type], file)

def mark_time_with_title(mark_title):
    import time
    my_time = time.time()
    if mark_title is not None:
        set_sticky(mark_title, my_time)
    return my_time

""""""
def mark_time():
    import time
    return time.time()

def time_span_with_title(mark_title, last_mark = None):
    import time
    if mark_title is not None:
        last_mark = get_sticky(mark_title, time.time())
    time_diff = time.time() - last_mark
    return time_diff

""""""
def time_span(last_mark):
    import time

    time_diff = time.time() - last_mark
    return time_diff

"""
folder manipulation
"""
def get_filenames_in_folder(folder):
    import os
    #print "&&&&&&"
    #print os.listdir(folder)
    return os.listdir(folder)

def rename_file_in_folder(search_file, new_file_name, folder):
    import os
    import os.path as op
    try:
        os.rename(op.join(folder, search_file),op.join(folder, new_file_name))
        return True
    except Exception as e:
        print(e)
        return False

def get_user_name():
    import os
    return os.environ["USERPROFILE"].split("\\")[-1]

def get_user_folder():
    from os import environ as OS_ENV
    #print OS_ENV["USERPROFILE"]
    return "{}\Documents".format(OS_ENV["USERPROFILE"])
    #import os
    #return "{}\Documents".format(os.environ["USERPROFILE"])

""""""
def is_SZ():
    from os import environ
    #print os.environ["USERPROFILE"]
    if environ["USERPROFILE"] == r"C:\Users\szhang":
        return True
    return False


def get_EA_setting_folder():
    folder = get_user_folder() + "\EnneadTab Settings"
    #print folder
    return secure_folder(folder)


def get_special_folder_in_EA_setting(folder_name):
    folder = get_EA_setting_folder() + "\{}".format(folder_name)
    return secure_folder(folder)

def get_EA_local_dump_folder():
    return get_special_folder_in_EA_setting("Local Copy Dump")


def secure_folder(path):
    from os import makedirs as OS_MAKEDIRS
    try:
        OS_MAKEDIRS(path)

    except Exception as e:

        #print_note( "folder cannot be secured")
        #print_note(e)
        pass
    return path

    """
    import os
    try:
        os.makedirs(path)

    except Exception as e:

        print_note( "folder cannot be secured")
        print_note(e)
        pass
    return path
    """

def get_file_name_from_path(file_path):
    import os.path as op
    head, tail = op.split(file_path)
    return tail

def get_folder_name_from_path(file_path):
    import os.path as op
    head, tail = op.split(file_path)
    return head


def remove_exisitng_file_in_folder(folder, file_name):
    import os
    import os.path as op
    if file_name not in os.listdir(folder):
        return False
    try:
        os.remove(op.join(folder, file_name))
        return True
    except Exception as e:
        print_note( "Cannot remove <{}> becasue of error: {}".format(file_name, e))
        return False



def is_file_exist_in_folder(check_file_name, folder):
    import os

    for file_name in os.listdir(folder):
        #print_note(file_name)
        if check_file_name == file_name:
            return True
    return False
"""
UI
"""

""""""
def purge_layer():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_Yes _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

""""""
def purge_material():
    rs.Command("_NoEcho _Purge _Pause _Materials=_Yes _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

""""""
def purge_block():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_Yes _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

""""""
def purge_group():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_Yes _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

""""""
def save_small():
    rs.Command("savesmall")


""""""
def rhino_layer_to_user_layer(name):
    return "[{}]".format(name.replace("::", "] - ["))

""""""
def user_layer_to_rhino_layer(name):
    return name[1:-1].replace("] - [", "::")

""""""
def get_layers(multi_select = True, message = "", layers = None):
    if layers is None:
        layers = sorted(rs.LayerNames())

    options = [rhino_layer_to_user_layer(x) for x in layers]
    sel_layers = select_from_list(options, multi_select = multi_select, message = message)
    if not sel_layers:
        return None
    layers = [user_layer_to_rhino_layer(x) for x in sel_layers]
    return layers





def select_from_image_list(image_list,
                        title = "EnneadTab",
                        message = "test message",
                        multi_select = True,
                        button_names = ["Run Me"],
                        width = 500,
                        height = 500):

    # image_list = [(image_path, display_name), ...] tuple pairs
    import EA_FORMS_SELECT_IMAGES
    return EA_FORMS_SELECT_IMAGES.ShowImageSelectionDialog(image_list,
                                                    title,
                                                    message,
                                                    multi_select,
                                                    button_names,
                                                    width,
                                                    height)

"""
rhino operation
"""


def set_text_justifiction(text_id, justification):
    """
    1 = Left
    2 = Center (horizontal)
    4 = Right
    65536 = Bottom
    131072 = Middle (vertical)
    262144 = Top
    """

    import System # pyright: ignore
    import Rhino # pyright: ignore
    #set new justification like with rs.AddText
    new_justification  = System.Enum.ToObject(Rhino.Geometry.TextJustification, justification)

    #grab geometry of the text object
    text_geometry = rs.coercegeometry(text_id)
    text_geometry.Justification = new_justification

    #replace geometry of the rhino object with new justification geometry
    sc.doc.Objects.Replace(text_id,text_geometry)

""""""
def get_center(obj):
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    center = (min + max)/2
    return center
""""""
def get_obj_h(obj):
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    z_diff = (max.Z - min.Z)
    return z_diff
""""""
def get_boundingbox_edge_length(obj):
    corners = rs.BoundingBox(obj)
    X = rs.Distance(corners[0], corners[1])
    Y = rs.Distance(corners[1], corners[2])
    Z = rs.Distance(corners[0], corners[5])
    return X, Y, Z

""""""
def get_material_by_name(name):
    mats = sc.doc.Materials
    """
    print("searching material with name: " + name)
    for mat in mats:
        print(mat.Name)
    """

    mat = filter(lambda x: x.Name == name, mats)
    if len(mat) != 0:
        return mat[0]
    return None

""""""
def create_material(name, RGBAR, return_index = False):
    # RGBAR = (r,g,b,t,R)
    from System.Drawing import Color
    import Rhino # pyright: ignore
    material = Rhino.DocObjects.Material()
    material.Name = name
    material = Rhino.Render.RenderMaterial.CreateBasicMaterial(material, sc.doc)
    sc.doc.RenderMaterials.Add(material)


    sphere = Rhino.Geometry.Sphere(Rhino.Geometry.Plane.WorldXY, 500)
    id = sc.doc.Objects.AddSphere(sphere)
    obj = sc.doc.Objects.FindId(id)
    obj.RenderMaterial = material;
    obj.CommitChanges()

    material = get_material_by_name(name)
    if material is None:
        rs.TextOut(message = "No material named [{}] found after creating material, contact Sen for help on why.".format(name), title = "EnneadTab")
    #material.CommitChanges()
    #print "begin changing material = {}".format(material)
    red, green, blue, transparency, reflectivity = RGBAR # trnasparency 0 = solid, 1 = see-thru,,,,,reflectivity 0 = matte, 255 = glossy
    material.DiffuseColor = Color.FromArgb(red,green,blue)
    #print material.DiffuseColor
    material.Transparency = transparency
    material.TransparentColor = Color.FromArgb(red,green,blue)
    #print material.TransparentColor
    material.ReflectionColor = Color.FromArgb(red,green,blue)
    material.Reflectivity = reflectivity
    material.ReflectionGlossiness = reflectivity
    material.Shine = reflectivity
    material.SpecularColor = Color.FromArgb(red,green,blue)
    material.AmbientColor  = Color.FromArgb(red,green,blue)

    material.CommitChanges()
    #rs.DeleteObject(id)
    if return_index:
        return material.MaterialIndex, id
    else:
        return material, id#return the sample material ball so the material is visible to search. you can delete ball with this ID after script.


""""""
def create_material_by_type(name,
                            RGBAR,
                            transparency_color = None,
                            type = 0,
                            return_index = True):
    """
    base_color_rgb ----> tuple of 3 int
    type = 0 --->basic
           1 --->glass
           2 --->metal
           3 --->plastic
           4 --->emission
           5 --->paint
           6 --->plaster
           10 ---> physically based

    trnasparency 0 = solid, 1 = see-thru
    reflectivity 0 = matte, 255 = glossy
    return material index by default, otherwise return material
    """

    import Rhino # pyright: ignore
    import scriptcontext as sc
    red, green, blue, transparency, reflectivity = RGBAR

    """
    bmtex = Rhino.Render.RenderContentType.NewContentFromTypeId(Rhino.Render.ContentUuids.BitmapTextureType)
    bmtex.Filename = "C:\\Users\\Nathan\\Pictures\\uvtester.png"

    simtex = bmtex.SimulatedTexture(Rhino.Render.RenderTexture.TextureGeneration.Allow)
    """
    #
    #print(Rhino.Render.ContentUuids.PhysicallyBasedMaterialType)
    #print(Rhino.Render.ContentUuids.GlassMaterialType)

    def create_physical_based_mat():
        # first create an empty PBR material
        pbr_rm = Rhino.Render.RenderContentType.NewContentFromTypeId(Rhino.Render.ContentUuids.PhysicallyBasedMaterialType)

        # to get to a Rhino.DocObjects.PhysicallyBasedMaterial we need to simulate the
        # render material first.
        sim = pbr_rm.SimulatedMaterial(Rhino.Render.RenderTexture.TextureGeneration.Allow)

        # from the simulated material we can get the Rhino.DocObjects.PhysicallyBasedMaterial
        pbr = sim.PhysicallyBased;

        # now we have an instance of a type that has all the API you need to set the PBR
        # properties. For simple glass we set color to white, opacity to 0 and opacity
        # IOR to 1.52
        pbr.Opacity = 0.0
        pbr.OpacityIOR = 1.52
        pbr.BaseColor = Rhino.Display.Color4f.White

        pbr.SetTexture(simtex.Texture(), Rhino.DocObjects.TextureType.PBR_BaseColor)

        # convert it back to RenderMaterial
        new_pbr = Rhino.Render.RenderMaterial.FromMaterial(pbr.Material, sc.doc)
        # Set a good name
        new_pbr.Name = name

        # Set pbr ui sections visible
        """
        new_pbr.SetParameter("pbr-show-ui-basic-metalrough", True);
        new_pbr.SetParameter("pbr-show-ui-subsurface", True);
        new_pbr.SetParameter("pbr-show-ui-specularity", True);
        new_pbr.SetParameter("pbr-show-ui-anisotropy", True);
        new_pbr.SetParameter("pbr-show-ui-sheen", True);
        new_pbr.SetParameter("pbr-show-ui-clearcoat", True);
        new_pbr.SetParameter("pbr-show-ui-opacity", True);
        new_pbr.SetParameter("pbr-show-ui-emission", True);
        new_pbr.SetParameter("pbr-show-ui-bump-displacement", True);
        new_pbr.SetParameter("pbr-show-ui-ambient-occlusion", True);
        """

        return new_pbr

    if type == 10:
        mat = create_physical_based_mat()


    # Add it to the document
    sc.doc.RenderMaterials.Add(mat)
    if return_index:
        return get_material_index(mat)##material name might surfix number if similar name exist, so the index should be get from final product not name.
    else:
        return mat

#################### always run area ###############


# try:
#     # print "checking rui"
#     #print is_current_enneadtab_on_main_rui()
# except:
#     pass

#################### test area ###############

if( __name__ == "__main__" ):
    # print create_material("test01", (32,108,134,0.95,250))
    # rs.MessageBox("123")
    print(123)
