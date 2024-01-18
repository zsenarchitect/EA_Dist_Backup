"""run this in 3.10+"""

import subprocess
import os
import shutil

import sys

parent_folder = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_folder)
import ENVIRONMENT_CONSTANTS
import DATA_FILE
import NOTIFICATION


def create_exe(source_script, 
                icon_path=None, 
                other_files=[], 
                folders=[],
                hidden_modules=[], 
                version=None, 
                new_name=None, 
                final_folder=None,
                is_folder=True, 
                is_no_console=True):
    
    
    # Construct the basic PyInstaller command
    command = ['pyinstaller', source_script]

    # Add icon if provided
    if icon_path:
        command.extend(['--icon', icon_path])

    # Add other files
    for file in other_files:
        command.extend(['--add-data', '{};.'.format(file)])

    # Add folders
    for folder in folders:
        command.extend(['--add-data', '{};.'.format(folder)])

    # Add hidden imports
    for module in hidden_modules:
        command.extend(['--hidden-import', module])

    # Add no console flag
    if is_no_console:
        command.append('--noconsole')

    # Add folder flag
    if is_folder:
        command.append('--onedir')
    else:
        command.append('--onefile')

    # Run the command
    subprocess.run(command)

    # Rename and move the executable if needed
    if new_name or final_folder:
        dist_folder = os.path.join('.', 'dist')
        original_exe_name = os.path.splitext(os.path.basename(source_script))[0]
        original_exe = os.path.join(dist_folder, original_exe_name)
        if is_folder:
            original_exe = os.path.join(original_exe, original_exe_name)

        if version:
            new_name = "{}_{}".format(new_name, version)

        if not new_name:
            new_name = os.path.basename(original_exe)

        new_path = os.path.join(final_folder or dist_folder, new_name)

        if is_folder:
            shutil.move(original_exe, new_path)
        else:
            os.rename(original_exe, new_path + '.exe')

        print('Executable created at {}'.format(new_path))
        
        
    NOTIFICATION.messenger(main_text= "Exe is created!")


def get_availible_version_num(exe_name, main_version = None):
    """note to self::::::::can split the exe folder names that contain the exe name, 
    split by the ".", make last bit a int and +1 to get the next availble version number

    Args:
        exe_name (_type_): _description_
        main_version (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if main_version:
        return "main_version.1"
    return 2.1


def make_exe_from_json(json_file):
    data = DATA_FILE.read_json_as_dict(json_file)
    data_list = data.get("pyinstallerOptions")
    
    # set default value incase that is not captured in json
    icon_path = "{}\\ennead-e-logo.png".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT)
    is_one_file = False
    is_console = False
    other_files = []
    final_folder = ENVIRONMENT_CONSTANTS.EXE_FOLDER
    version = get_availible_version_num("temp")
    
    for item in data_list:
        key = item["optionDest"]
        value = item["value"]
        
        if key == "filesnames":
            source_script = value
        
        if key == "icon_file":
            icon_path = value
            
        if key == "onefile":
            is_one_file = value
    
        if key == "console":
            is_console = value
            
        if key == "datas":
            other_files.append(value)
    
    
        
    
    
  
            
    create_exe(source_script, 
               icon_path=icon_path,
                other_files=other_files, 
                folders=[],
                hidden_modules=[], 
                version=version, 
                new_name=None, 
                final_folder=final_folder,
                is_folder=not is_one_file, 
                is_no_console=not is_console)



def create_and_move_exe(source_script, target_folder, exe_name=None):
    import subprocess
    import shutil
    import os
    
    """
    Creates a single-file executable from a Python script using PyInstaller and moves it to a specified folder.

    :param source_script: Path to the Python script to be converted.
    :param target_folder: Path to the folder where the executable will be moved.
    :param exe_name: Optional new name for the executable. If None, the script's base name is used.
    """
    # Change to the directory of the source script
    script_dir = os.path.dirname(os.path.abspath(source_script))
    os.chdir(script_dir)
    # Check if PyInstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return
        raise RuntimeError("PyInstaller is not installed. Please install it using 'pip install pyinstaller'.")


    
    # Creating the executable
    try:
        subprocess.run(["pyinstaller", "--onefile", source_script], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create executable: {e}")

    # Define the executable's name and paths
    script_name = os.path.splitext(os.path.basename(source_script))[0]
    exe_name = exe_name or script_name
    exe_path = os.path.join('dist', exe_name + '.exe')

    # Ensure target folder exists
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Move the executable to the target folder
    target_exe_path = os.path.join(target_folder, exe_name + '.exe')
    shutil.move(exe_path, target_exe_path)

    print(f"Executable created and moved to {target_exe_path}")



##########################################################
if __name__ == "__main__":
    # Example usage
    create_and_move_exe("C:\\Users\\szhang\\github\\EnneadTab-for-Revit\\ENNEAD.extension\\lib\\EnneadTab\\REPO MANAGER\\Setup EnneadTab.py", 
                        "C:\\Users\\szhang\\github\\EnneadTab-for-Revit\\ENNEAD.extension\\lib\\EnneadTab\\REPO MANAGER", 
                        "optional_new_name")