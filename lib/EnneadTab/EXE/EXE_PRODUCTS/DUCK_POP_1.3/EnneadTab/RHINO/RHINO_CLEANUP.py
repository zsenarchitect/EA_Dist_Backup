

import rhinoscriptsyntax as rs
try:
    import Rhino
except:
    pass

def purge_layer():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_Yes _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

def purge_material():
    rs.Command("_NoEcho _Purge _Pause _Materials=_Yes _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

def purge_block():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_Yes _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

def purge_group():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_Yes _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")


def save_small():
    rs.Command("savesmall")


def close_note_panel():
    note_id = Rhino.UI.PanelIds.Notes
    Rhino.UI.Panels.ClosePanel(note_id)
