from Autodesk.Revit import DB # pyright: ignore 
def filter_main_and_primary_elements(elements):
    """
    Filters elements to include only elements that either have no design option
    or belong to the primary design option.
    
    Args:
        elements (list): List of elements to filter
        
    Returns:
        list: List of filtered elements
    """

    
    return [element for element in elements 
            if element.DesignOption is None or 
            element.DesignOption.IsPrimary]


