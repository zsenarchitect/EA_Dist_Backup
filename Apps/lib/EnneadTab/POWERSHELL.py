import os
import subprocess

import ENVIRONMENT

def run_powershell_script(script_name, no_wait = True):
    full_path = os.path.join(ENVIRONMENT.SCRIPT_FOLDER, script_name)
    if not os.path.exists(full_path):
        print("Script not found: {}".format(full_path))
        return

    try:
        if no_wait:
            # Use Popen for non-blocking execution with hidden window and no output
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.Popen(["powershell", 
                            "-ExecutionPolicy", "Bypass",
                            "-NoProfile",
                            "-NonInteractive",
                            "-WindowStyle", "Hidden",
                            "-File", full_path],
                           startupinfo=startupinfo,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        else:
            # Use run for blocking execution
            subprocess.run(["powershell", 
                          "-ExecutionPolicy", "Bypass",
                          "-NoProfile",
                          "-NonInteractive",
                          "-File", full_path], 
                            check=True, 
                            shell=True,
                            capture_output=True,
                            text=True)
    except subprocess.CalledProcessError as e:
        print("Error running script: {}".format(e))
        return


if __name__ == "__main__":
    run_powershell_script("Get-InstalledSoftware.ps1")