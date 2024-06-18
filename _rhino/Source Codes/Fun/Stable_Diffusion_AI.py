import sys
sys.path.append("..\lib")

import EnneadTab
import re



def is_unchanged_file(file):
    """
    if match is not "20220916104302_411632104"
    """
    match = re.match(r"\d{14}_\d{9}", file)
    if match:
        return True
    return False


def update_image_name():
    """

    rename_file_in_folder(search_file, new_file_name, folder):
    """
    folder = r"L:\4b_Applied Computing\03_Rhino\13_External Generation\Stable Diffusion GRisk GUI\results"

    for file in EnneadTab.FOLDER.get_filenames_in_folder(folder):
        if ".png" not in file:
            continue
        if not is_unchanged_file(file):
            continue
        print(file)


        image_name = file.split(".png")[0]
        info_file = get_info_file(image_name, folder)
        new_image_name = get_description_from_info_file(info_file, folder)
        len_limit = 150
        if len(new_image_name) > len_limit:
            new_image_name = new_image_name[0:len_limit] + "..."
        base_name = new_image_name[:]
        print(base_name)

        count = 0
        while True:

            search_file = file
            new_file_name = file.replace(image_name, new_image_name)
            success = EnneadTab.FOLDER.rename_file_in_folder(search_file, new_file_name, folder)
            search_file = info_file
            new_file_name = info_file.replace(image_name, new_image_name)
            success *= EnneadTab.FOLDER.rename_file_in_folder(search_file, new_file_name, folder)
            if success:
                break
            if count > 5:
                break
            count += 1
            new_image_name = "{}_{:02}".format(base_name, count)
            print(new_image_name)

def get_info_file(image_name, folder):
    for file in EnneadTab.FOLDER.get_filenames_in_folder(folder):
        if ".txt" not in file:
            continue
        if image_name not in file:
            continue
        return file

def get_description_from_info_file(info_file, folder):
    info_file = folder + "\\" + info_file
    with open(info_file, "r") as f:
        raw = f.readlines(1)[0]
        """
        {'text': 'A car musem in Hongkong with speed feeling, vintage megazine cover style', 'folder': '.\\results', 'resX': 512, 'resY': 512, 'half': 1, 'seed': 3670559466, 'origin': None, 'origin_W': None, 'steps': 150, 'vscale': 7.5, 'samples': 1}
        """
        match_object = re.match(r"{'text': \'(.*?)\'.*", raw)
        return match_object.group(1)

def run_stable_diffusion():
    """
    filepath = r"L:\4b_Applied Computing\03_Rhino\13_External Generation\Stable Diffusion GRisk GUI\Stable Diffusion GRisk GUI.exe"
    EnneadTab.EXE.open_file_in_default_application(filepath)
    """
    import subprocess
    path = r"L:\4b_Applied Computing\03_Rhino\13_External Generation\AI generation\#"
    subprocess.Popen(r'explorer /select, {}'.format(path))

    
@EnneadTab.ERROR_HANDLE.try_catch_error    
def main():
    run_stable_diffusion()
    
    update_image_name()
  
######################  main code below   #########
if __name__ == "__main__":
    
    main()
