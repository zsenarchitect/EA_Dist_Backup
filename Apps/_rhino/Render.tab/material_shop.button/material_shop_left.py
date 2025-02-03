
__title__ = "MaterialShop"
__doc__ = "Find good material and asset."


from EnneadTab import ERROR_HANDLE, LOG
import webbrowser

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def material_shop():
    webbrowser.open("https://ambientcg.com/")

    
if __name__ == "__main__":
    material_shop()
