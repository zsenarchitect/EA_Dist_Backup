__title__ = "ImportRevitCollection"
__doc__ = """Organize DWG exports from Revit into a readable Rhino layer tree.

Key Features:
- Imports multiple DWG files with unit conversion
- Creates organized layer hierarchy
- Preserves material properties from Revit
- Supports custom or default layer naming
"""

import scriptcontext as sc
import rhinoscriptsyntax as rs
from EnneadTab import NOTIFICATION, FOLDER, DATA_FILE, ENVIRONMENT
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_LAYER, RHINO_CLEANUP, RHINO_FORMS, RHINO_MATERIAL

import imp
import os
random_layer_color_script_folder = "{}\\Layer.tab\\random_layer_color.button".format(ENVIRONMENT.RHINO_FOLDER)
REF_MODULE = imp.load_source("random_layer_color_left", '{}\\random_layer_color_left.py'.format(random_layer_color_script_folder))

class RevitDwgImporter:
    def __init__(self):
        self.ost_material_map = DATA_FILE.get_data("EA_OST_MATERIAL_MAP.sexyDuck")
        
    def process_dwg(self, file, units, is_using_default_layer_structure):
        RHINO_CLEANUP.purge_block()
        print("working on file:" + file)
        
        rs.Command("_-import \"{}\" _ModelUnits={} -enter -enter".format(file, units))
        NOTIFICATION.messenger(sub_text="Come Back, come back!", main_text="Import Finish!")
        
        imported_objs = rs.LastCreatedObjects()
        if not imported_objs:
            NOTIFICATION.messenger(main_text="Cannot find imported objs in file\n{}.".format(file))
            return

        layers_used = self._get_layers_used(imported_objs)
        parent_layer_prefix = self._get_parent_layer_prefix(file, is_using_default_layer_structure)
        if parent_layer_prefix is None:
            return

        self._change_objs_layer(imported_objs, parent_layer_prefix)
        self._safely_delete_used_layer(layers_used)
        REF_MODULE.random_layer_color(default_opt=True)

    def _get_layers_used(self, imported_objs):
        return list({rs.ObjectLayer(obj) for obj in imported_objs})

    def _get_parent_layer_prefix(self, file, is_using_default):
        all_layers = rs.LayerNames()
        all_layers_user = [RHINO_LAYER.rhino_layer_to_user_layer(x) for x in all_layers]
        special_note = "<Type in a new parent layer name>"
        all_layers_user.insert(0, special_note)

        if is_using_default:
            parent_layer_prefix = all_layers_user[0]
        else:
            parent_layer_prefix = RHINO_FORMS.select_from_list(
                all_layers_user,
                title="Migrate imported Layers under another parent",
                message="Enter text or select for the name of the parent layer",
                multi_select=False,
                button_names=["Select Single Layer as Parent"],
                width=500,
                height=500
            )

        if parent_layer_prefix is None:
            return None

        if parent_layer_prefix == special_note:
            default_prefix = FOLDER.get_file_name_from_path(file).split(".dwg")[0]
            if is_using_default:
                parent_layer_prefix = default_prefix
            else:
                parent_layer_prefix = rs.StringBox(
                    message="type in parent layer name",
                    default_value=default_prefix,
                    title="EnneadTab"
                )
                if parent_layer_prefix is None:
                    return None
            parent_layer_prefix = "[" + parent_layer_prefix + "]"

        return RHINO_LAYER.user_layer_to_rhino_layer(parent_layer_prefix)

    def _safely_delete_used_layer(self, layers_to_remove):
        for layer in layers_to_remove:
            rs.DeleteLayer(layer)

    def _change_objs_layer(self, objs, parent_layer_prefix):
        cate_layer = parent_layer_prefix.split("Type_")[0]
        for obj in objs:
            current_layer = rs.ObjectLayer(obj)
            current_layer_color = rs.LayerColor(current_layer)
            desired_layer = cate_layer + "::" + parent_layer_prefix + "::" + current_layer
            
            if not rs.IsLayer(desired_layer):
                rs.AddLayer(name=desired_layer, color=current_layer_color)
                layer_material_index = self._retrieve_ost_material(current_layer)
                if layer_material_index is not None:
                    rs.LayerMaterialIndex(desired_layer, layer_material_index)
            
            rs.ObjectLayer(obj, desired_layer)
        rs.ExpandLayer(cate_layer, False)

    def _retrieve_ost_material(self, current_layer):
        for ost_name in self.ost_material_map:
            if current_layer.find(ost_name) != -1:
                break
        else:
            return None

        mat_id = RHINO_MATERIAL.get_material_by_name(ost_name, return_index=True)
        if mat_id:
            return mat_id

        material_data = self.ost_material_map.get(ost_name)
        if material_data is None:
            return None

        name = material_data.get("name", "Default")
        diffuse = material_data["color"].get("diffuse", (0,0,0))
        R, G, B = diffuse
        alpha = material_data["color"].get("transparency", 0)
        alpha = int(alpha/100)
        reflection = material_data["color"].get("shininess", 0)
        reflection = int(255*reflection/128)
        RGBAR = (R, G, B, alpha, reflection)

        id, _ = RHINO_MATERIAL.create_material(name, RGBAR, return_index=True)
        return id

    def change_objs_layer_in_block(self, block_name, parent_layer_prefix):
        block_definition = sc.doc.InstanceDefinitions.Find(block_name)
        objs = block_definition.GetObjects()
        self._change_objs_layer(objs, parent_layer_prefix)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def import_revit_collection():
    """Main function to import and process Revit DWG exports."""
    rs.EnableRedraw(False)
    
    unit_opts = ["Millimeters", "Feet", "Inches"]
    units = rs.ListBox(unit_opts,
                      message="Use which unit for the DWG?",
                      default=unit_opts[0],
                      title="EnneadTab Import Revit Exports")
    if units is None:
        return

    filenames = rs.OpenFileNames(
        title="pick dwg files to import collection",
        filter="DWG exports from Revit (*.dwg)|*.dwg||"
    )
    if not filenames:
        return

    auto_opts = ["Yes, Use Everything Default Layer Structure", 
                 "No, Let me pick each layer structure"]
    auto_opt = rs.ListBox(
        auto_opts,
        message="Use auto process option for layer structure?",
        default=auto_opts[0],
        title="EnneadTab Importing Revit Export Under Rhino"
    )
    if auto_opt is None:
        return

    is_using_default = (auto_opt == auto_opts[0])
    rs.EnableRedraw(False)

    importer = RevitDwgImporter()
    if not importer.ost_material_map:
        NOTIFICATION.messenger("No mapping data found. Did you export setting from Revit side?")
        return

    for filename in filenames:
        importer.process_dwg(filename, units, is_using_default)

    NOTIFICATION.duck_pop("All imported!")

if __name__ == "__main__":
    import_revit_collection()