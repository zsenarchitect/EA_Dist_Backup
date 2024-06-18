import rhinoscriptsyntax as rs

import sys
sys.path.append("..\lib")
import EnneadTab



@EnneadTab.ERROR_HANDLE.try_catch_error
def unit_test_rhino():
    rs.ClearCommandHistory()

    EnneadTab.UNIT_TEST.test_core_module()

    report = rs.CommandHistory()
    
    EnneadTab.EMAIL.email(sender_email=None,
                            receiver_email_list=["szhang@ennead.com"],
                            subject="Rhino Unit Test Result",
                            body="This is the unit test result from Rhino side.\n\n{}".format(report),
                            body_folder_link_list=None,
                            body_image_link_list=None,
                            attachment_list=None,
                            schedule_time=None)
 
    


######################  main code below   #########
if __name__ == "__main__":

    unit_test_rhino()




