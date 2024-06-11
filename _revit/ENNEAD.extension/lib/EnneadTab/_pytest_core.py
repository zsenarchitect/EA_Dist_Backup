
# this is experiental


def validate_all_modules():
    try:
        from unittest.mock import MagicMock
        import sys

        sys.modules['Autodesk'] = MagicMock()
        sys.modules['Autodesk.Revit'] = MagicMock()
        sys.modules['Autodesk.Revit.UI'] = MagicMock()

        import DATA_FILE
        return True
    except:
        return False
    
    
def main_test():
    assert validate_all_modules() == True