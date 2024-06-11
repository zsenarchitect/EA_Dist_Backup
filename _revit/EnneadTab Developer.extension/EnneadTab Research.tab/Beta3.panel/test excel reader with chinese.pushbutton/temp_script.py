#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "read excel test"

from pyrevit import DB, revit, script
import EA_UTILITY
import EnneadTab

################## main code below #####################
output = script.get_output()
output.close_others()

import sys
reload(sys)
# 设定了输出的环境为utf8
sys.setdefaultencoding('utf-8')
filepath = r"C:\Users\szhang\Desktop\make sheet.xlsx"
#datas = EA_UTILITY.read_txt_as_list(filepath, use_encode = True)
datas = EA_UTILITY.read_data_from_excel(filepath, worksheet = "Test 1")
for data in datas:
    print(data)
