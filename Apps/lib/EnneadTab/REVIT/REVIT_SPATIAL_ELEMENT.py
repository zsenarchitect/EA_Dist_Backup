

"""this is for Area and Room category...."""


def get_element_status(element):
    if element.Area <= 0:
        if element.Location:
            return "Not Enclosed"
        else:
            return "Not Placed"
    else:
        return "Good"


def is_element_bad(element):
    return get_element_status(element) != "Good"

def filter_bad_elements(elements):
    """
    return non_closed, non_placed
    """
    non_closed = filter(lambda x: get_element_status(x) == "Not Enclosed", elements)
    non_placed = filter(lambda x: get_element_status(x) == "Not Placed", elements)
    return non_closed, non_placed