"""
TO-DO: 

make __alias__ attr inside py, a list of tuple for command title and help doc.
there might be more than one tuple pairs to allow left right click action.
alias manager will then search and parse to generate alias based on folder structure and attr, if attr exist. 

""" 

import rhinoscriptsyntax as rs
import os
import sys
sys.path.append("..\lib")
import EnneadTab


def chapter_data(notes):
    out = dict()
    for note in notes:
        alias, script_path, description = note
        out[alias] = {"script_path": script_path, "description": description}
    return out


def get_all_alias():
    data = dict()
    #("xxx", "xxx", "xxx"),


    chapter = "Viewport"
    notes = [("SS", 'Views\\section_box.py', "Create Sectionbox from user defined freeform polysurf"),
            ("BB", 'Views\\section_box_by_bounding_box.py', "Create Sectionbox from selected objs, just like Revit")]
    data[chapter] = chapter_data(notes)


    chapter = "Layer"
    notes = [("IL", 'Selection\\isolate_layer_by_selection.py', "Isolate Layer by current selection"),
            ("LayIso", 'Selection\\isolate_layer_by_selection.py', "Isolate Layer by current selection"),
            ("EA_IsolateLayer", "Selection\\isolate_layer_by_selection.py", "Isolate Layer by current selection"),
            ("IF", "Selection\isolate_nested_layer.py", "Isolate objs on layers that are under same"),
            ("LL", "Selection\\isolate_layer_lock_by_selection.py", "Isolate Lock layer by current selection"),
            ("ML", "Layers\\merge_layers.py", "Merge layers to one. Including inside the blocks."),
            ("EA_MergeLayers", "Layers\\merge_layers.py", "Merge layers to one. Including inside the blocks."),
            ("LayMrg", "Layers\\merge_layers.py", "Merge layers to one. Including inside the blocks.")]
    data[chapter] = chapter_data(notes)

    chapter = "Blocks"
    notes = [("IB", "Selection\\isolate_similar_block.py", "Isolate blocks with same definition"),
            ("MBU", "Blocks\\make_block_unique.py", "Make block unique in place."),
            ("EA_MakeBlockUnique", "Blocks\\make_block_unique.py", "Make block unique in place."),
            ("MBD", "Blocks\\match_block_distortion.py", "Match blocks distortion to the desired block."),
            ("EA_MatchBlockDistortion", "Blocks\\match_block_distortion.py", "Match blocks distortion to the desired block."),
            ("EA_RandomizeBlock", "Blocks\\random_transform_block.py", "Randomly transoform blocks with scale and rotation."),
            ("EA_RandomlyDeSelectBlock", "Selection\\random_deselect.py", "Randomly deselect a percentage of selection")]
    data[chapter] = chapter_data(notes)



    chapter = "Material"
    notes = [("MM", "Materials\\merge_materials_3.0.py", "Merge materials to one."),
            ("EA_MergeMaterials", "Materials\\merge_materials_3.0.py", "Merge materials to one.")]
    data[chapter] = chapter_data(notes)



    chapter = "Revit"
    notes = [("EA_ImportDwgExportedFromRevit", "Import\\import_revit_export_under_layer.py", "Import DWG exported from Revit ISO exporter"),("Rhino2Revit","Export\export_for_rhino2revit.py", "Export content by layer to conitnue working in Revit EnneadTab" ),
             ("EA_Rhino2Revit","Export\\export_for_rhino2revit.py", "Export content by layer to conitnue working in Revit EnneadTab" )]
    data[chapter] = chapter_data(notes)

    chapter = "Utility"
    notes = [("EA_GetLatestEnneadTab", "Manager\\update_enneadtab.py", "Update EnneadTab to latest version"),
            ("EA_Dad_Joke", "Fun\\jokes\\tell_a_joke_with_form.py", "Show some Dad Jokes..."),
            ("EA_Red_Alert", "Fun\\add_game_sound.py", "Add game sound effect to Rhino using classic Red Alert sound track."),
            ("EA_Button_Searcher", "Library\\enneadtab_search.py", "Help you find the button you have been looking for."),
            ("EA_TimeSheet_Record", "Manager\\time_sheet_record_manually.py", "Record your which file you have worked on."),
            ("EA_TimeSheet_Show", "Manager\\time_sheet_show_record.py", "Print details about your timesheet."),
            ("EnneadTab_Starter", "Manager\\rhino_startup.py", "Initiallize EnneadTab")]
    data[chapter] = chapter_data(notes)

    chapter = "GFA"
    notes = [("EA_GFA_Display", "Display\\toggle_GFA_display.py", "Toggle GFA Display"),
             ("GFA", "Display\\toggle_GFA_display.py", "Toggle GFA Display")
            ]
    data[chapter] = chapter_data(notes)


    EnneadTab.DATA_FILE.pretty_print_dict(data)
    return data



@EnneadTab.ERROR_HANDLE.try_catch_error
def add_alias_set():
    alias_data = get_all_alias()
    
    script_parent = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino"
    if os.path.exists(EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_RHINO):
        script_parent = EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_RHINO
        

    good_alias = []
    
    for chapter in alias_data:

        for alias in alias_data[chapter]:
            if rs.IsAlias(alias) and "EnneadTab-for-Rhino" not in rs.AliasMacro(alias):
                #Skip setting alias for {} due to overlapping names, this is usually becasue user has setup their personal alias that happen to be same name as EA ones
                continue


            
            if rs.IsAlias(alias):
                current_macro = rs.AliasMacro(alias)
                current_full_path = current_macro.split('_-RunPythonScript "')[1].split('"')[0]
                if not os.path.exists(current_full_path):
                    rs.DeleteAlias(alias)
                


            
            
            script_path = alias_data[chapter][alias]["script_path"]
            full_path = "{}\\Source Codes\\{}".format(script_parent, script_path)
            script_content = r'! _-RunPythonScript "{}"'.format(full_path)
            if os.path.exists(full_path):
                rs.AddAlias(alias, script_content)
                good_alias.append(alias)
            else:
                if EnneadTab.USER.is_enneadtab_developer():
                    EnneadTab.NOTIFICATION.messenger(main_text="FileScript not found for alias: <{}>".format(alias))
                    print (alias)
                    print (full_path)
                    print ("\n\n")

            
    return good_alias

def alias_cheat_sheet():

    good_alias = add_alias_set()
    alias_data = get_all_alias()
    OUT = "Current Rhino Alias Shortcut:\n\n"

    for chapter in alias_data:
        OUT += "\n------- {} --------\n".format(chapter)
        for alias in alias_data[chapter]:
            if alias not in good_alias:
                print ("Bad Alias [{}]".format(alias))
                continue

            description = alias_data[chapter][alias]["description"]
            OUT += "[{}]: {}\n".format(alias, description)

    rs.TextOut(OUT)
    
    
if __name__ == "__main__":
    add_alias_set()
    
    
