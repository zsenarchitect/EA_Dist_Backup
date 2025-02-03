
__title__ = "TellMeVersion"
__doc__ = "Show current version of EnneadTab Rhino"


from EnneadTab import  VERSION_CONTROL

def tell_me_version():
    VERSION_CONTROL.show_last_success_update_time()


    
if __name__ == "__main__":
    tell_me_version()
