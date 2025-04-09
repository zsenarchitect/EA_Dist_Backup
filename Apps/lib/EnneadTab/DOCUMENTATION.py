import sys
# if hasattr(sys, "setdefaultencoding"):
#     sys.setdefaultencoding('utf-8')  # This line ensures the default encoding is UTF-8, only need for some old py2

"""Utilities for showing tips and documentation for tools.

This module provides functionality for managing and displaying documentation, tips,
and knowledge base content across the EnneadTab ecosystem. It supports both Revit
and Rhino environments.

Key Features:
- Documentation retrieval and display
- Tip of the day functionality
- Knowledge base management
- Scott's tips integration from EI posts
- Icon and resource management
"""

import io
import os
import random

import json

import ENVIRONMENT
import FOLDER
import USER
import OUTPUT
import ERROR_HANDLE
import DATA_FILE



def get_text_path_by_name(file_name):
    """Get the full path of a text file in the documents library.

    Args:
        file_name (str): Name of the text file to locate

    Returns:
        str: Full path to the text file if found, None otherwise
    """
    path = "{}\\text\\{}".format(ENVIRONMENT.DOCUMENT_FOLDER, file_name)
    if os.path.exists(path):
        return path
    print ("A ha! {} is not valid or accessible. Better luck next time.".format(path))



TIP_KEY = "__tip__"
SCOTT_TIPS = ["https://ei.ennead.com/post/3046/revit-legends-legend-components",
              "https://ei.ennead.com/post/2777/revit-short-subject-purge-cad-before-linking-into-revit",
              "https://ei.ennead.com/post/3007/don-t-use-groups-as-single-entities",
              "https://ei.ennead.com/post/2981/keeping-enough-c--drive-free-space",
              "https://ei.ennead.com/post/2824/revit-short-subject-acc-bim-360-requirements",
              "https://ei.ennead.com/post/2673/revit-short-subject-worksharing-etiquette",
              "https://ei.ennead.com/post/31/revit-short-subject-design-options",
              "https://ei.ennead.com/post/19/revit-short-subject-keyboard-shortcuts",
              "https://ei.ennead.com/post/47/revit-short-subject-3d-view-navigation",
              "https://ei.ennead.com/post/64/revit-short-subject-don-t-manually-hide-elements",
              "https://ei.ennead.com/post/75/revit-short-subject-limit-use-of-groups",
              "https://ei.ennead.com/post/99/revit-short-subject-the-cad-query-tool",
              "https://ei.ennead.com/post/114/revit-short-subject-best-practice-for-new-views"]

def show_scott_tip():
    """Display a random tip from Scott's EI knowledge base.
    
    Opens the tip in the default web browser and displays it in the output window.
    Tips are curated from Scott's posts on the Ennead Intranet.
    """
    if ENVIRONMENT.is_Revit_environment():
        from pyrevit import script
        output = script.get_output()
        if not ENVIRONMENT.IS_OFFLINE_MODE:
            pass
            # output.print_image("L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Misc\\scott_but_younger.png")
    else:
        output = OUTPUT.Output()
    tip = random.choice(SCOTT_TIPS)
    import webbrowser
    webbrowser.open(tip)
    output.print_md ("#Scott's Tip of the day:\n{}".format(tip))

    embed_html = """<!DOCTYPE html>
<html>
<head>
    <title>Embedding a Webpage</title>
</head>
<body>
    <h1>...............................................</h1>
    
    <!-- Use an iframe to embed the webpage -->
    <iframe src={} width="1200" height="900" frameborder="0"></iframe>
    
    <p>Enjoy!</p>
</body>
</html>""".format(tip)
    # output.print_html(embed_html)
    OUTPUT.display_output_on_browser()
    

def get_files_with_keyword(keyword, folder):
    """Search for files containing a specific keyword in the given folder.
    
    Args:
        keyword (str): The keyword to search for in file contents
        folder (str): Root folder path to begin the search
        
    Returns:
        list: List of file paths containing the keyword
        
    Note:
        Excludes certain system folders and template files from the search.
    """
    
    max_open = 10
    opened = 0
    matching_files = []
    for root, dirs, files in os.walk(folder):
        
        
        
        if "Ennead Tailor.tab" in root:
            continue
        
        if "lib" in root:
            # ignore core modules
            continue
        
        if "archive" in root:
            continue
        
        if "Utility.panel" in root:
            continue
        
        if "MakeFloatingBox" in root:
            continue
        
        for file in files:
            if "DOCUMENTATION" in file:
                # ignore this file that is searching other files
                continue
            if "template" in file:
                continue
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # # tester
                # if "Merge_Family_UI" in file_path:
                #     return file_path
                
                
                with io.open(file_path, 'r', encoding="utf-8") as f:
                    contents = f.read()

                    
                    if "__main__" not in contents:
                        # this is to skip file that can actually run the whole thing during import. This is bad. shoud report back to SEn to fix
                        if USER.IS_DEVELOPER:
                            print ("\n\nThis contain dangerous format that can run during import:\n" + file_path + "\nYou can add this...")
                            print ("""if __name__ == "__main__":
    pass""")
                            if opened < max_open:
                                opened += 1
                                os.startfile(file_path)
                        continue
                    
                    if keyword in contents:
                        #print "Found keyword '%s' in file: %s" % (keyword, file_path)
                        matching_files.append(file_path)

    return matching_files
    if len(matching_files) > 0:
        # print "Totally {} file with bad documentation".format(len(matching_files))
        random_files = random.sample(matching_files, min(output_count, len(matching_files)))
        # print "Opening randomly selected files:"
        return random_files
        for file in random_files:
            return file
    else:
        # print "No files found containing keyword '%s'" % keyword
        pass

def get_title_tip_from_folder(folder, is_random_single = True):
    """Retrieve title and tip information from files in a folder.

    Args:
        folder (str): The folder path to search for tips
        is_random_single (bool, optional): If True, returns a single random tip. 
            Defaults to True.

    Returns:
        list: List of tuples containing (title, tip, icon_path) for each tip found
    """
    
    matching_files = get_files_with_keyword(TIP_KEY, folder)
    
    if is_random_single:

        return [get_title_tip_from_file(random.choice(matching_files), is_random_single)]
    
    return [get_title_tip_from_file(x, is_random_single) for x in matching_files]

def get_icon_from_path(file_path):
    """Locate the icon file associated with a given script path.

    Searches for icon files named 'icon.png' or containing 'icon' in the
    same directory as the script.

    Args:
        file_path (str): Path to the script file

    Returns:
        str: Path to the icon file if found, None otherwise
    """
    button_folder = os.path.dirname(file_path)
    for file in os.listdir(button_folder):
        if "icon.png" == file:
            return os.path.join(button_folder, file)
        
    for file in os.listdir(button_folder):
        if "icon" in file:
            return os.path.join(button_folder, file)
   
def get_title_tip_from_file(lucky_file, is_random_single):
    """Extract title and tip information from a Python script file.

    Args:
        lucky_file (str): Path to the Python script file
        is_random_single (bool): If True, returns only one random tip

    Returns:
        tuple: Contains (module_name, tip_text, icon_path)
            module_name (str): Name of the module
            tip_text (str or None): The tip text if found
            icon_path (str or None): Path to the module's icon
    """
    icon_path = get_icon_from_path(lucky_file)
        
    module_name = FOLDER.get_file_name_from_path(lucky_file).replace(".py", "")
    try:
        # Try imp first
        import imp # pyright: ignore
        ref_module = imp.load_source(module_name, lucky_file)
    except (ImportError, AttributeError):
        try:
            # Fallback to importlib if imp fails
            from importlib import resources  # use resources instead of util
            spec = resources.spec_from_file_location(module_name, lucky_file)
            ref_module = resources.module_from_spec(spec)
            spec.loader.exec_module(ref_module)
        except Exception as e:
            if USER.is_EnneadTab_developer:
                print ("\n\nDeveloper visible only logging:")
                print (ERROR_HANDLE.get_alternative_traceback())
            return module_name, None, icon_path
    except Exception as e:
        if USER.is_EnneadTab_developer:
            print ("\n\nDeveloper visible only logging:")
            print (ERROR_HANDLE.get_alternative_traceback())
            
        return module_name, None, icon_path
    
    tip = getattr(ref_module,TIP_KEY)
    
    if isinstance(tip, list): #>>>>>>>if manually define many tips then use that, otherwise use __doc__, it shold not require double writing
        pass
    else:
        tip = [ref_module.__doc__]
        
    if is_random_single:
        tip = [random.choice(tip)]

        
    if hasattr(ref_module, "__title__"):
        title = ref_module.__title__.replace("\n", " ")
    else:
        title = module_name
    
    
    return title, tip, icon_path

def show_tip_revit(is_random_single=True):

    from pyrevit import script
    output = script.get_output()
    if not output:
        output = OUTPUT.Output()


    search_folder = ENVIRONMENT.REVIT_PRIMARY_TAB if is_random_single else ENVIRONMENT.REVIT_PRIMARY_EXTENSION
    
    for title_tits_tuple in get_title_tip_from_folder(search_folder, is_random_single):
        title, tips, icon_path = title_tits_tuple
        if tips:
            print ("\n\n\n\n")
            if is_random_single:

                output.print_md ("#EnneadTab Tip of the day:")
            if icon_path:

                output.print_html("<span style='text-align: center;'><img src=\"file:///{0}\"></span>".format(icon_path))

            output.print_md("##Did you know in [{}]...".format(title))
            
            for tip in tips:
                print ("\n\n")
                for line in tip.split("\n"):
                    output.print_md (line)

    print ("\n\n\n\n")
    if is_random_single:
        OUTPUT.display_output_on_browser()




def extract_global_variables(script_path):
    import ast

    with io.open(script_path, 'r', encoding="utf-8") as file:
        script_content = file.read()
    
    tree = ast.parse(script_content)
    global_vars = {}
    
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Handling the value directly if it's a constant
                    if isinstance(node.value, ast.Constant):
                        var_value = node.value.value  # Directly accessing the value of the Constant node
                    else:
                        try:
                            # Fallback for other types using literal_eval for safe evaluation
                            var_value = ast.literal_eval(node.value)
                        except ValueError:
                            # For non-literals or complex cases, keep a representation of the code
                            var_value = "Unsupported value for safe evaluation, legacy version. See Sen Z to fix this for dynamic constant handling."
                    global_vars[var_name] = var_value
    
    return global_vars


def set_revit_knowledge():


    def strip_folder(folder):
        return folder.replace(ENVIRONMENT.REVIT_PRIMARY_EXTENSION, "").lstrip("\\")
    
    data_dict = {}
    for root, dirs, files in os.walk(ENVIRONMENT.REVIT_PRIMARY_EXTENSION):
        for file in files:
            if not file.endswith("_script.py"):
                continue
            if "floating_script.py" in file:
                continue
            if ".temp" in root:
                continue
            script_path = os.path.join(root, file)

   
            try:
                global_vars = extract_global_variables(script_path)
            except:
                print (script_path)
                print (ERROR_HANDLE.get_alternative_traceback())
                continue
            icon_path = get_icon_from_path(script_path)
            if ".panel" in script_path:
                panel_folder = script_path.split(".panel")[0] + ".panel"
                tab_name = os.path.basename(panel_folder).replace(".panel", "")
            else:
                panel_folder = os.path.dirname(script_path)
                tab_name = "No Tab"
            tab_icon_path = get_icon_from_path(panel_folder)

            
            if not icon_path:
                print (script_path)
                raise

    

            script_path = strip_folder(script_path)
            icon_path = strip_folder(icon_path)

            
            data_dict[script_path] = {
                        "script":script_path,
                        "icon":icon_path,
                        "alias": global_vars.get("__title__", "Alias not set").replace("\n", " "),
                        "doc": global_vars.get("__doc__", "Doc string not set"),
                        "tab": tab_name,
                        "tab_icon":tab_icon_path,
                        "is_popular": global_vars.get("__is_popular__", False)
                    }

    DATA_FILE.set_data(ENVIRONMENT.KNOWLEDGE_REVIT_FILE, data_dict)

def get_revit_knowledge():
    knowledge_pool = DATA_FILE.get_data(ENVIRONMENT.KNOWLEDGE_REVIT_FILE)


    knowledge = {}
    
    for value in knowledge_pool.values():
        command_names = value["alias"]
        if not isinstance(command_names, list):
            command_names = [command_names]
        for command_name in command_names:
            knowledge[command_name] = value

    return knowledge



def get_rhino_knowledge():
    knowledge_pool = DATA_FILE.get_data(ENVIRONMENT.KNOWLEDGE_RHINO_FILE)
 
    knowledge = {}
    
    for value in knowledge_pool.values():
        command_names = value["alias"]
        if not isinstance(command_names, list):
            command_names = [command_names]
        for command_name in command_names:
            knowledge[command_name] = value

    return knowledge


def show_tip_rhino():
    """Show a random tip for Rhino. Not implemented yet.
    """
    knowledge = get_rhino_knowledge()


    button, tip_data = random.choice(list(knowledge.items()))
    

    
    if "_right.py" in tip_data["script"]:
        access = "Right Click"
    else:
        access = "Left Click"

    tab_name = tip_data.get("tab", None)
    if tab_name is None:
        tab_name = "Unknown"
    tab_name = tab_name.replace(".tab", " Tab").replace(".menu", " Menu")

    commands = tip_data.get("alias", None)
    if not isinstance(commands, list):
        commands = [commands]
    final_commands = []
    for command in commands:
        if command is None:
            continue
        if command.upper() == command:
            final_commands.append(command)
        else:
            final_commands.append("EA_{}".format(command))
    commands = " / ".join(final_commands)


    
    output = OUTPUT.Output()
    output.write ("EnneadTab Tip of the day:", OUTPUT.Style.Title)



    
    def update_image_action(search_key):
        
        icon_path = tip_data.get(search_key, None)
        if icon_path is None:
            icon_path = os.path.join("Knowledge.tab\\search_command.button", "missing_icon.png")
        
        icon_image_path = os.path.join(ENVIRONMENT.RHINO_FOLDER, icon_path)


        return icon_image_path


    button_icon = update_image_action("icon")
    output.write(button_icon)


    output.write("Did you know in [{}]...".format(commands), OUTPUT.Style.Subtitle)

    output.write (tip_data.get("doc"))

    output.insert_divider()
    
    output.write ("Activated by {}".format(access), OUTPUT.Style.Footnote)
    click_icon = "{}\\{}.png".format("{}\\Knowledge.tab\\search_command.button".format(ENVIRONMENT.RHINO_FOLDER), access)
    output.write(click_icon)

    
    output.write("Find this button in: {}".format(tab_name), OUTPUT.Style.Footnote)
    tab_icon = update_image_action("tab_icon")
    output.write(tab_icon)

    

    output.plot()



def tip_of_day():
    """Show a random tip of the day.
    """
    if not USER.IS_DEVELOPER:
        if random.random() < 0.2:
            return

        
    if ENVIRONMENT.is_Revit_environment():
        if random.random() < 0.95:
            show_tip_revit()
        else:
            show_scott_tip()
    if ENVIRONMENT.is_Rhino_environment():
        show_tip_rhino()
        
        
def unit_test():
    # tip_of_day()
    pass
    
    
def print_documentation_book_for_review_revit():
    """Print all the tips in a book or webpage to check spelling and doc updates."""
    show_tip_revit(is_random_single=False)
    
    OUTPUT.display_output_on_browser()

def show_floating_box_warning():
    """Show an informational message for floating a box window.
    """
    import NOTIFICATION
    NOTIFICATION.duck_pop(main_text="Click has no use for this button. Just hold down on the arrow and drag to make the window floating.\nThis will always stay on top even when changed to another tab.")
    
    
def get_floating_box_documentation():
    """Return an informational message for floating a box window.
    """
    return "Hold down on the arrow and drag to make the window floating. This will always stay on top even when changed to another tab."
    
    
    
def generate_documentation(debug = False):
    generate_app_documentation(debug, app="Rhino")
    generate_app_documentation(debug, app="Revit")



def generate_app_documentation(debug, app):
    if app == "Rhino":
        knowledge_dict = get_rhino_knowledge()
    elif app == "Revit":
        set_revit_knowledge()
        knowledge_dict = get_revit_knowledge()
    else:
        raise

    def get_command_order(x):
        tab = x.get("tab")
        commands =  x.get("alias")
        if not isinstance(commands, list):
            commands = [commands]

        if not tab:
            tab = "no tab"


        delayed_item_keywords = ["browser",
                                 "contents",
                                 "proj",
                                 "personal",
                                 "tester"]
        def is_in_delayed_category(x):
            for item in delayed_item_keywords:
                if item in x.lower():
                    return True
            return False
        return  "{}, {}, {}".format(is_in_delayed_category(tab), tab, commands)
    app_knowledge = sorted(knowledge_dict.values(), key = get_command_order)
    
    import PDF
    import time
    if debug:
        output =  "{}_knowledge_{}.pdf".format(app, time.time())
        PDF.documentation2pdf(app, app_knowledge,output)
        os.startfile(output)
    else:
        output = "{}\\EnneadTab_For_{}_HandBook.pdf".format(ENVIRONMENT.INSTALLATION_FOLDER, app)
        PDF.documentation2pdf(app, app_knowledge,output)

    # import WEB
    # output =  "rhino_knowledge_{}.html".format(time.time())
    # WEB.documentation2html(rhino_knowledge,output)
    # os.startfile(output)

def write_dream():
    output = OUTPUT.Output()
    output.write("the font of Dream", OUTPUT.Style.Title)
    from __init__ import __dream__
    output.write(__dream__)
    save_path = FOLDER.get_local_dump_folder_file("dream.html")
    output._generate_html_report(save_path)
    
if __name__ == "__main__":
    
    # generate_documentation(debug=True)
    write_dream()