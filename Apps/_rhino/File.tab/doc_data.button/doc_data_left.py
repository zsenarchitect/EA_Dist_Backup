__title__ = "DocData"
__doc__ = """Demonstrates usage of RHINO_PROJ_DATA module for document data management.

This script showcases how to:
- Inspect existing document data
- Set preferred Grasshopper file path
- Store structured Grasshopper input parameters
- Handle various data types (bool, int, float)

Example Usage:
    - Left-click to run the demonstration
    - View results in Rhino command line
"""

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.RHINO import RHINO_PROJ_DATA

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def doc_data():
    RHINO_PROJ_DATA.inspect_document_data()

    
    data = RHINO_PROJ_DATA.get_plugin_data()
    data[RHINO_PROJ_DATA.DocKeys.PreferredGrasshopperFile] = "C:/Users/szhang/Documents/sample.gh"
    data[RHINO_PROJ_DATA.DocKeys.GrasshopperInput] = {
        "option A": {
            "input_1": 100,
            "input_2": 200,
            "input_3": True,
            "input_4": "some text",
            }, 
        "option B": {
            "input_1": 100,
            "input_2": 200,
            "input_3": False,
            "input_4": "some other text",
            }, 
        }


    
    data["some_bool"] = True
    data["some_int"] = 123
    data["some_float"] = 123.456
    RHINO_PROJ_DATA.set_plugin_data(data)

    
if __name__ == "__main__":
    doc_data()
