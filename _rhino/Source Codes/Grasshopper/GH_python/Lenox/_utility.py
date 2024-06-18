import json
import os

import sys
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab



try:
    import collections
    import array
    import math
    from System import Object
    from System.Windows import Forms
    from System import Environment
    import System # pyright: ignore.Security.Principal as sec
    import System # pyright: ignore.Threading.Tasks as tasks
except ImportError:
    # print("Failed to import System # pyright: ignore.")
    pass

try:
    from Grasshopper.Kernel import GH_RuntimeMessageLevel as Message
    from Grasshopper.Kernel.Types import GH_ObjectWrapper as Goo
    from Grasshopper import DataTree
    from Grasshopper.Kernel.Data import GH_Path as Path
    from Grasshopper import Instances
except ImportError:
    # raise ImportError("Failed to import Grasshopper.")
    pass


try:
    import rhinoscriptsyntax as rs
    import Rhino # pyright: ignore.UI as rui

except ImportError as e:
    # raise ImportError("Failed to import Rhino # pyright: ignore.\n{}".format(e))
    pass


DATA_FOLDER = "L:\\4b_Applied Computing\\03_Rhino\\22_HB_Study"



def generate_doc_string(doc_string, input_list, output_list):
    doc_string = "+"*50 + "\n" +  doc_string
    if len(input_list) == 0:
        doc_string += "\n\nNo input parameter required!"
    else:
        doc_string += "\n\nInput Parameter(s):"
        for variable_data in input_list:
            variable_name = variable_data[0]
            variable_type = variable_data[1]
            variable_desc = variable_data[2]
            if variable_type.lower().endswith("s"):
                note = "[Need to set to list access in gh input]"
            else:
                note = ""
            doc_string += "\n{}({}){}: {}".format(variable_name, variable_type, note, variable_desc)

    doc_string += "\n\nOutput Parameter(s):"
    for variable_data in output_list:
        variable_name = variable_data[0]
        variable_type = variable_data[1]
        variable_desc = variable_data[2]
        doc_string += "\n{}({}): {}".format(variable_name, variable_type, variable_desc)

    return doc_string

def generate_default_value_map():
    """not in use"""
    print ("this func should be depreciated and not showing anywhere")
    return {"String": "",
            "Number": 0,
            "Boolean": True}



def validate_input_list(globals_dict, input_list):
    
    for variable_data in input_list:
        variable_name = variable_data[0]
        
        # do not override the namescape if exist
        if variable_name in globals_dict:
            continue
        
        variable_type = variable_data[1]
        if variable_type.lower().endswith("s"):
            
            globals_dict[variable_name] = []
        else:
            globals_dict[variable_name] = None
            
    return globals_dict

def get_input_names(input_list):
    return [input_data[0] for input_data in input_list]

def generate_para_inputs(globals_dict, input_list):
    return [globals_dict[input_data[0]] for input_data in input_list]

def generate_para_outputs(globals_dict, output_list, result):
    if isinstance(result, list):
        pass
    elif isinstance(result, tuple):
        pass
    else:
        result = [result]
        
    for i,item in enumerate(output_list):
        output_name = item[0]
        globals_dict[output_name] = result[i]
        
    return globals_dict
    

def is_all_input_valid(globals_dict, input_list):
    for variable_data in input_list:
        variable_name = variable_data[0]
        if globals_dict.get(variable_name, None) is None:
            note = "<{}> input is not set".format(variable_name)
            print (note)
            EnneadTab.NOTIFICATION.messenger(main_text = note)
            if "ghenv" in globals_dict:
                give_warning(globals_dict["ghenv"].Component, note)
            return False
    return True

def create_valid_study_name():
    data_list = [x.split(".json")[0] for x in os.listdir(DATA_FOLDER)]
    while True:
        study_name = rs.StringBox("Name of the study", title="EnneadTab Save Study") 
        if not study_name:
            EnneadTab.NOTIFICATION.messenger(main_text = "Study saving cancelled")
            return None
        if study_name not in data_list:
            return study_name
        
        EnneadTab.NOTIFICATION.messenger(main_text = "Study name [{}] already exist!\nTry Some thing unique".format(study_name))

def get_study_data_file(study_name):
    return "{}\\{}.json".format(DATA_FOLDER,
                                study_name)

def save_study_data(study_name, data):
    with open(get_study_data_file(study_name), "w") as f:
        json.dump(data, f)
        
def load_study_data(study_name):
    with open(get_study_data_file(study_name), "r") as f:
        return json.load(f)


##########################################
# funcs below has been largely inspired/borrowed from ladybug_rhino module
##########################################
def give_warning(component, message):
    """Give a warning message (turning the component orange).

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
        message: Text string for the warning message.
    """
    component.AddRuntimeMessage(Message.Warning, message)


def give_remark(component, message):
    """Give an remark message (giving a little grey ballon in the upper left).

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
        message: Text string for the warning message.
    """
    component.AddRuntimeMessage(Message.Remark, message)


def give_popup_message(message, window_title='', icon_type='information'):
    """Give a Windows popup message with an OK button.

    Useful in cases where you really need the user to pay attention to the message.

    Args:
        message: Text string for the popup message.
        window_title: Text string for the title of the popup window. (Default: "").
        icon_type: Text for the type of icon to be used. (Default: "information").
            Choose from the following options.

            * information
            * warning
            * error

    """
    icon_types = {
        'information': Forms.MessageBoxIcon.Information,
        'warning': Forms.MessageBoxIcon.Warning,
        'error': Forms.MessageBoxIcon.Error
    }
    icon = icon_types[icon_type]
    buttons = Forms.MessageBoxButtons.OK
    rui.Dialogs.ShowMessageBox(message, window_title, buttons, icon)


def all_required_inputs(component):
    """Check that all required inputs on a component are present.

    Note that this method needs required inputs to be written in the correct
    format on the component in order to work (required inputs have a
    single _ at the start and no _ at the end).

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.

    Returns:
        True if all required inputs are present. False if they are not.
    """
    is_input_missing = False
    for param in component.Params.Input:
        if param.NickName.startswith('_') and not param.NickName.endswith('_'):
            missing = False
            if not param.VolatileDataCount:
                missing = True
            elif param.VolatileData[0][0] is None:
                missing = True

            if missing is True:
                msg = 'Input parameter {} failed to collect data!'.format(param.NickName)
                print(msg)
                give_warning(component, msg)
                is_input_missing = True
    return not is_input_missing



def data_tree_to_list(input):
    """Convert a grasshopper DataTree to nested lists of lists.

    Args:
        input: A Grasshopper DataTree.

    Returns:
        listData -- A list of namedtuples (path, dataList)
    """
    all_data = list(range(len(input.Paths)))
    pattern = collections.namedtuple('Pattern', 'path list')

    for i, path in enumerate(input.Paths):
        data = input.Branch(path)
        branch = pattern(path, [])

        for d in data:
            if d is not None:
                branch.list.append(d)

        all_data[i] = branch

    return all_data


def list_to_data_tree(input, root_count=0, s_type=object):
    """Transform nested of lists or tuples to a Grasshopper DataTree.

    Args:
        input: A nested list of lists to be converted into a data tree.
        root_count: An integer for the starting path of the data tree.
        s_type: An optional data type (eg. float, int, str) that defines all of the
            data in the data tree. The default (object) works will all data types
            but the conversion to data trees can be more efficient if a more
            specific type is specified.
    """

    def proc(input, tree, track):
        for i, item in enumerate(input):
            if isinstance(item, (list, tuple, array.array)):  # ignore iterables like str
                track.append(i)
                proc(item, tree, track)
                track.pop()
            else:
                tree.Add(item, Path(*track))

    if input is not None:
        t = DataTree[s_type]()
        proc(input, t, [root_count])
        return t


def merge_data_tree(data_trees, s_type=object):
    """Merge a list of grasshopper DataTrees into a single DataTree.

    Args:
        input: A list Grasshopper DataTrees to be merged into one.
        s_type: An optional data type (eg. float, int, str) that defines all of the
            data in the data tree. The default (object) works will all data types
            but the conversion to data trees can be more efficient if a more
            specific type is specified.
    """
    comb_tree = DataTree[s_type]()
    for d_tree in data_trees:
        for p, branch in zip(d_tree.Paths, d_tree.Branches):
            comb_tree.AddRange(branch, p)
    return comb_tree


def flatten_data_tree(input):
    """Flatten and clean a grasshopper DataTree into a single list and a pattern.

    Args:
        input: A Grasshopper DataTree.

    Returns:
        A tuple with two elements

        -   all_data -- All data in DataTree as a flattened list.

        -   pattern -- A dictionary of patterns as namedtuple(path, index of last item
            on this path, path Count). Pattern is useful to un-flatten the list
            back to a DataTree.
    """
    Pattern = collections.namedtuple('Pattern', 'path index count')
    pattern = dict()
    all_data = []
    index = 0  # Global counter for all the data
    for i, path in enumerate(input.Paths):
        count = 0
        data = input.Branch(path)

        for d in data:
            if d is not None:
                count += 1
                index += 1
                all_data.append(d)

        pattern[i] = Pattern(path, index, count)

    return all_data, pattern


def unflatten_to_data_tree(all_data, pattern):
    """Create DataTree from a single flattened list and a pattern.

    Args:
        all_data: A flattened list of all data
        pattern: A dictionary of patterns
            Pattern = namedtuple('Pattern', 'path index count')

    Returns:
        data_tree -- A Grasshopper DataTree.
    """
    data_tree = DataTree[Object]()
    for branch in range(len(pattern)):
        path, index, count = pattern[branch]
        data_tree.AddRange(all_data[index - count:index], path)

    return data_tree

