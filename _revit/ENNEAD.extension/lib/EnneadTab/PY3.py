"""the base logic works but there is a unresolved issue:
the py3 engine will not pioritise the loaded module if same name already exist for PY2 loading, such as request

there is not current plan to fix it..."""


import USER_CONSTANTS
try:
    import subprocess
    import threading
    import locale
except:
    pass
import os

# Define the path to the Python executable in the pyRevit engine
py3_path = r"C:\Users\{}\AppData\Roaming\pyRevit-Master\bin\engines\CPY385\python.exe".format(USER_CONSTANTS.USER_NAME)

def run_py3(script_path, wait=True):
    """Runs a Python script using the specified Python 3 engine.
    
    Args:
        script_path (str): The path to the Python script to run.
        wait (bool): Whether to wait for the script to finish. Defaults to True.
    """
    
    def run_process():
        try:
            # Start the subprocess using the specified Python executable and script
            process = subprocess.Popen([py3_path, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()  # Wait for the process to complete
            encoding = locale.getpreferredencoding(False)
            if process.returncode == 0:
                print('File processing is complete!')
                print(stdout.decode(encoding))
            else:
                print('Error during script execution:')
                print(stderr.decode(encoding))
        except Exception as e:
            print("Unexpected error:", str(e))

    if wait:
        run_process()  # Run and wait for the process to complete
    else:
        thread = threading.Thread(target=run_process)
        thread.start()  # Run the process in a separate thread (non-blocking)

if __name__ == '__main__':
    # Example script path
    script_path = r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\lib\EnneadTab\REPO MANAGER\sync_core_module.py"
    if not os.path.exists(script_path):
        print("Script path does not exist.")
        

    else:
        # Blocking call
        run_py3(script_path)

        # Non-blocking call
        run_py3(script_path, wait=False)

        print("Main script continues to run...")
