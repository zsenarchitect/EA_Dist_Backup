"""used to create, store and retreiave schema data that can travel with revit doc instead of L drive external storage.
This idea is very helpful becasue it remove many proejct data storage dependecy to server.

This also means there is no need to create temperory shared parameter for some script and bind to categpry. 
However, this will also mean the info is not visiable to user, so no luck seeing then in schedule or have it controled by user.
ONLY USE IT WHEN THE CONTENT IS NEVER EXPECTED TO BE MODIFIED THRU UI."""


# schemas = DB.ExtensibleStorage.Schema.ListSchemas()


"""https://twentytwo.space/2021/02/27/revit-api-extensible-storage-schema/
this a helpful guide on how to use schema. Good examples




https://help.autodesk.com/view/RVT/2024/ENU/?guid=Revit_API_Revit_API_Developers_Guide_Advanced_Topics_Storing_Data_in_the_Revit_model_Extensible_Storage_html
this is the help guide from official Autodesk, aslo good




https://archi-lab.net/what-why-and-how-of-the-extensible-storage/
one more from Archi-lab, should read this FIRST!!!!!!!!!!!!!!!!!!!!!!!!!"""