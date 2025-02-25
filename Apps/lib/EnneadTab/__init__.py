package_name = "EnneadTab"
version = "3.1"

import os
import sys
import traceback

def get_module_files():
    """Get all Python module files in the current directory.
    
    Scans the package directory and identifies all Python modules that should be
    imported, excluding the __init__.py file itself.
    
    Returns:
        set: A set of strings containing the filenames of all .py files in the
            current directory that aren't __init__.py.
    
    Example:
        >>> get_module_files()
        {'REVIT.py', 'PDF.py', 'RHINO.py'}
    """
    return {
        module for module in os.listdir(os.path.dirname(__file__))
        if module.endswith('.py') and module != '__init__.py'
    }

def import_special_modules(module_name):
    """Handle special module imports (RHINO, REVIT).
    
    Some modules require special handling during import due to their dependencies
    or initialization requirements. This function handles those cases separately.
    
    Args:
        module_name (str): The name of the module to potentially import.
            Expected to be either "RHINO" or "REVIT".
    
    Returns:
        bool: True if the module was handled as a special case (regardless of
            whether the import succeeded), False if the module wasn't identified
            as needing special handling.
    
    Note:
        Special module import failures are silently ignored to prevent blocking
        the initialization of other modules.
    """
    if module_name not in ["RHINO", "REVIT"]:
        return False
        
    try:
        __import__("{}.{}".format(package_name, module_name), fromlist=['*'])
    except Exception:
        pass  # Silently skip if special module import fails
    return True

def import_module(module_name):
    """Import a single module with error handling.
    
    Attempts to import a module while handling potential import errors and
    ensuring the module directory is in the Python path.
    
    Args:
        module_name (str): The name of the module to import. Can include the .py
            extension, which will be stripped before import.
    
    Note:
        If an import fails, the error will be printed to stdout. Two attempts
        are made to format the error message:
        1. Using the full traceback
        2. Using just the exception string if traceback formatting fails
    
    Example:
        >>> import_module('PDF.py')  # Will import EnneadTab.PDF
        >>> import_module('REVIT')   # Will import EnneadTab.REVIT
    """
    try:
        # Ensure module directory is in path for relative imports
        module_dir = os.path.dirname(__file__)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
            
        # Import the module (strip .py extension if present)
        base_name = module_name[:-3] if module_name.endswith('.py') else module_name
        __import__("{}.{}".format(package_name, base_name), fromlist=['*'])
    except Exception as e:
        try:
            print("Cannot import {} because\n\n{}".format(
                module_name, traceback.format_exc()))
        except:
            print("Cannot import {} because\n\n{}".format(
                module_name, str(e)))

def initialize_package():
    """Initialize the package by importing all modules.
    
    This function orchestrates the package initialization process by:
    1. Getting a list of all Python modules in the package
    2. Attempting to import special modules first
    3. Importing remaining modules
    
    The function handles both regular and special module imports, ensuring that
    all package components are properly initialized.
    
    Note:
        This function is automatically called when the package is imported.
        Special modules (RHINO, REVIT) are handled separately from regular modules
        due to their specific initialization requirements.
    """
    for module in get_module_files():
        if not import_special_modules(module):
            import_module(module)

# Execute package initialization
initialize_package()



