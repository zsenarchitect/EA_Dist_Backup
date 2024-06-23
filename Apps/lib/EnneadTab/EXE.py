
import os


<<<<<<< HEAD
=======


def make_exe(maker_json):
    pass


def update_all_exes():
    pass


>>>>>>> 76e3fd102b014b1662a1e1b3ba697ce7e40c1030
def try_open_app_from_list(exes):
    for exe in exes:
        if not exe:
            continue
        if os.path.exists(exe):
            os.startfile(exe)
            return True
    if os.environ["USERPROFILE"].split("\\")[-1] == "szhang":
        print ("[SZ only log]No exe found in any of the location.")
        for exe in exes:
            print (exe)
<<<<<<< HEAD
    return False

=======
    return False
>>>>>>> 76e3fd102b014b1662a1e1b3ba697ce7e40c1030
