__title__ = "EnscapeAssetLocator"
__doc__ = """Your personal detective for hunting down elusive Enscape assets!

This handy tool launches the EnscapeAssetChanger application that helps you:
- Locate hidden Enscape asset folders across your system
- Access and modify materials on Enscape objects
- Customize properties of those beautiful Enscape trees, furniture and people
- Save hours of searching through obscure file directories

Perfect for visualization specialists who need precise control over their Enscape assets.
"""

__is_popular__ = True
from EnneadTab import ERROR_HANDLE, LOG, EXE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def enscape_asset_locator():
    EXE.try_open_app("EnscapeAssetChanger")
    
if __name__ == "__main__":
    enscape_asset_locator()
