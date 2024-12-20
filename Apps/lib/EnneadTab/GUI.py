"""Manipulate the GUI of apps by searching for image patterns."""

import EXE
import DATA_FILE

def simulate_click_on_image(image):
    """Add search json to find this image on screen and try to click on it."""

    with DATA_FILE.update_data("auto_click_data.sexyDuck") as data:
        if "ref_images" not in data:
            data["ref_images"] = []
        data["ref_images"].append(image)

    EXE.try_open_app("AutoClicker.exe")
