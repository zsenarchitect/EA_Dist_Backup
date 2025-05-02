__title__ = "ReloadEngine"
__doc__ = """Reload all EnneadTab modules to ensure latest changes are applied.

This script will:
1. Import all EnneadTab modules
2. Reload each module to apply latest changes
3. Handle any import errors gracefully"""

import imp
import os
import sys
from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def reload_engine():
    """Reload all EnneadTab modules to ensure latest changes are applied."""
    
    # Get the EnneadTab package directory
    enneadtab_dir = os.path.dirname(ENVIRONMENT.__file__)
    
    # List all Python files in the EnneadTab directory
    modules = []
    for file in os.listdir(enneadtab_dir):
        if file.endswith('.py') and not file.startswith('__'):
            # Check if file has python3 shebang
            file_path = os.path.join(enneadtab_dir, file)
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
                if first_line == "#!python3":
                    print("Skipped: {} (Python 3 module)".format(file))
                    continue
            module_name = file[:-3]  # Remove .py extension
            modules.append(module_name)
    
    # Also include subdirectories that are Python packages
    for item in os.listdir(enneadtab_dir):
        if os.path.isdir(os.path.join(enneadtab_dir, item)) and not item.startswith('__'):
            # Check if directory is a Python package
            if os.path.exists(os.path.join(enneadtab_dir, item, '__init__.py')):
                modules.append(item)
    
    # Import and reload each module
    for module in modules:
        try:
            full_module_name = "EnneadTab.{}".format(module)
            if full_module_name in sys.modules:
                try:
                    imp.reload(sys.modules[full_module_name])
                    print("Reloaded: {}".format(full_module_name))
                except SyntaxError:
                    print("Skipped: {} (Syntax error in module)".format(full_module_name))
                except ImportError:
                    print("Skipped: {} (Import error)".format(full_module_name))
            else:
                try:
                    __import__(full_module_name)
                    print("Imported: {}".format(full_module_name))
                except SyntaxError:
                    print("Skipped: {} (Syntax error in module)".format(full_module_name))
                except ImportError:
                    print("Skipped: {} (Import error)".format(full_module_name))
        except Exception as e:
            print("Failed to reload {}: {}".format(full_module_name, str(e)))
    
    print("EnneadTab modules reload complete.")

if __name__ == "__main__":
    reload_engine()
