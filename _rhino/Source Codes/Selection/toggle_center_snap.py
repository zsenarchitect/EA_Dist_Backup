import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs


@EnneadTab.ERROR_HANDLE.try_catch_error
def toggle_center_osnap():

    osnap_mode_center = 32
    #add 'End' mode while keeping the ones that are already set
    mode = rs.OsnapMode()
    #print bin(mode)[-6]

    #current_stage = EnneadTab.DATA_FILE.get_sticky_longterm("OSNAP_MODE_CENTER", True)
    current_stage = int(bin(mode)[-6])
    if current_stage:
        rs.OsnapMode(mode - osnap_mode_center)
    else:
        rs.OsnapMode(mode + osnap_mode_center)

    #EnneadTab.DATA_FILE.set_sticky_longterm("OSNAP_MODE_CENTER", not(current_stage))
    #add 'End' mode while clearing the others
    #rs.OsnapMode(rhOsnapModeEnd)




if __name__=="__main__":
    toggle_center_osnap()
