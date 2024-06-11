
#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Use me to publish stable version and beta version."
__title__ = "Publish &\nArchive(New)"
__context__ = "zero-doc"
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import sys
sys.path.append(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\lib")
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
#doc = __revit__.ActiveUIDocument.Document # pyright: ignore



def main():
    opts = [["Publish to Beta Version", "(In most case, get the update to teaster only.)"],
            ["Publish to Stable Version", "...Rarely, this update to stable version only."],
            ["Publish to Both Version", ".......Occasionally, this update to both stable and beta version"],
            ["Publish Games", ".......no question ask!"]]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue(options = opts, main_text = "Pick carefully!!")
    if not res:
        return


    publish_beta_version = False
    publish_stable_version = False
    if res == opts[0][0]:
        publish_beta_version = True
    elif res == opts[1][0]:
        publish_stable_version = True
    elif res== opts[2][0]:
        publish_beta_version = True
        publish_stable_version = True
    elif res == opts[3][0]:
        publish_games()
        
    else:
        return

    EnneadTab.VERSION_CONTROL._publish_Revit_source_code(publish_stable_version, publish_beta_version)

    EnneadTab.SOUNDS.play_sound("sound effect_mario stage clear.wav")
    
    
def publish_games():
    src = r"C:\Users\szhang\github\Revit-Monopoly"
    game_repo = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Misc"
    EnneadTab.FOLDER.copy_dir(src, 
                            game_repo,
                            allow_print_log=True)
    EnneadTab.SOUNDS.play_sound("sound effect_mario fireball.wav")
    EnneadTab.NOTIFICATION.duck_pop(main_text = "game published!")
################## main code below #####################
output = script.get_output()
output.close_others()

if __name__ == "__main__":
    main()
