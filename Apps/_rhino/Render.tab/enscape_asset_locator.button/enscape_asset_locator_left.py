
__title__ = "EnscapeAssetLocator"
__doc__ = "Help you find the Enscape asset folder by search name, so you can manipulate asset material."

__is_popular__ = True
from EnneadTab import ERROR_HANDLE, LOG, EXE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def enscape_asset_locator():
    EXE.try_open_app("EnscapeAssetChanger")
    
if __name__ == "__main__":
    enscape_asset_locator()
