#!/usr/bin/python
# -*- coding: utf-8 -*-


__context__ = "zero-doc"
__doc__ = "Perform the basic test for EnneadTab Core, make sure all is pass."
__title__ = "Unit Test\nRevit"

# from pyrevit import forms #
from pyrevit import script #




from EnneadTab import FOLDER, UNIT_TEST, EMAIL, ERROR_HANDLE

            
@ERROR_HANDLE.try_catch_error
def unit_test_revit():
    UNIT_TEST.test_core_module()
    
    # if is_SZ():
    #.    return 
    dest_file = FOLDER.get_EA_dump_folder_file("UnitTest.html")
    output.save_contents(dest_file)
    EMAIL.email(sender_email=None,
                            receiver_email_list=["szhang@ennead.com"],
                            subject="Revit Unit Test Result",
                            body="This is the unit test result from Revit side",
                            body_folder_link_list=None,
                            body_image_link_list=None,
                            attachment_list=[dest_file],
                            schedule_time=None)
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    unit_test_revit()



