try:
    from System import Guid # pyright: ignore
except:
    pass

import DATA_FILE

def get_guid(app_name):
    """Get GUID for the specified application.
    
    Args:
        app_name: Name of the application
        
    Returns:
        System.Guid: A Guid object for the specified application
    """
    guid_dict = DATA_FILE.get_data("guid_dict.sexyDuck")
    if not guid_dict:
        guid_dict = {}

    if app_name not in guid_dict:
        # Create new GUID, store as string, return as Guid object
        new_guid = Guid.NewGuid()
        guid_dict[app_name] = str(new_guid)
        DATA_FILE.set_data(guid_dict, "guid_dict.sexyDuck")
        return new_guid
    else:
        # Return existing GUID as Guid object
        return Guid.Parse(guid_dict[app_name])
