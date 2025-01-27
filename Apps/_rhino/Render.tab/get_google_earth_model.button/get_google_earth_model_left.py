
__title__ = "GetGoogleEarthModel"
__doc__ = "This button does GetGoogleEarthModel when left click"


from EnneadTab import ERROR_HANDLE, LOG
import webbrowser
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def get_google_earth_model():
    webbrowser.open("https://www.youtube.com/watch?v=YtlK4046VRQ")

    print ("Also check script folder for the python script used in blender")

    
if __name__ == "__main__":
    get_google_earth_model()
