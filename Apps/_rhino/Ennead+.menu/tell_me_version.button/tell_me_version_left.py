__title__ = "TellMeVersion"
__doc__ = """Display current EnneadTab Rhino version.

Key Features:
- Version number display
- Update status information
- Installation verification
- Component compatibility check
- Release notes access"""


from EnneadTab import  VERSION_CONTROL

def tell_me_version():
    VERSION_CONTROL.show_last_success_update_time()


    
if __name__ == "__main__":
    tell_me_version()
