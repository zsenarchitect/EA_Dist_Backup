import os
import subprocess
import getpass

script_path = "C:\\Users\\szhang\\duck-repo\\EnneadTab-OS\\DarkSide\\_schedule_publish.py"
venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', '..', '.venv', 'Scripts', 'python.exe')
venv_python = os.path.abspath(venv_python)
vscode_path = r"C:\\Users\\szhang\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
task_name = "EnneadTab_SchedulePublisher"

def create_startup_batch():
    """Create a batch file in the user's startup folder as a fallback method"""
    startup_folder = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    batch_file = os.path.join(startup_folder, "EnneadTab_SchedulePublisher.bat")
    
    batch_content = '@echo off\nstart "VSCode" "{}" && "{}" "{}"\n'.format(vscode_path, venv_python, script_path)
    
    try:
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        print("Created startup batch file at: {}".format(batch_file))
        
        # Open the startup folder in Windows Explorer
        try:
            os.startfile(startup_folder)
            print("Opened startup folder in Windows Explorer")
        except Exception as e:
            print("Could not open startup folder: {}".format(e))
        
        return True
    except Exception as e:
        print("Failed to create startup batch file: {}".format(e))
        return False

if __name__ == "__main__":
    # Check computer name and script existence
    if os.environ.get('COMPUTERNAME', '').upper() == 'SZHANG' and os.path.exists(script_path):
        print("Setting up script to run after computer restart... (fun and professional)")
        
        # Method 1: Try ONSTART (runs immediately after computer restart, NO user login required)
        # This requires ADMINISTRATOR PRIVILEGES
        action_cmd = 'start "VSCode" "{}" && "{}" "{}"'.format(vscode_path, venv_python, script_path)
        
        print("Attempting ONSTART (runs after restart without user login - requires admin)...")
        schtasks_cmd = [
            'schtasks', '/Create', '/F',
            '/SC', 'ONSTART',
            '/TN', task_name,
            '/TR', action_cmd
        ]
        
        try:
            subprocess.run(schtasks_cmd, check=True, shell=True)
            print("SUCCESS! Task registered with ONSTART - will run after computer restart WITHOUT user login.")
            print("NOTE: You must run this script as Administrator for ONSTART to work.")
        except Exception as e:
            print("ONSTART failed (need admin rights): {}".format(e))
            print("")
            
            # Method 2: Try ONLOGON (runs when user logs in)
            print("Attempting ONLOGON (runs only AFTER user login)...")
            schtasks_cmd_logon = [
                'schtasks', '/Create', '/F',
                '/SC', 'ONLOGON',
                '/TN', task_name,
                '/TR', action_cmd
            ]
            
            try:
                subprocess.run(schtasks_cmd_logon, check=True, shell=True)
                print("Task registered with ONLOGON - will run AFTER user login (not at startup).")
            except Exception as e2:
                print("ONLOGON also failed: {}".format(e2))
                print("")
                
                # Method 3: Startup folder (runs when user logs in)
                print("Using startup folder method (runs only AFTER user login)...")
                if create_startup_batch():
                    print("Successfully set up startup using Windows startup folder!")
                    print("WARNING: This only runs AFTER you log in, not immediately at restart.")
                else:
                    print("All methods failed.")
        
        print("")
        print("SUMMARY:")
        print("- For immediate startup without login: Run this script as Administrator")
        print("- Current setup: Script runs only after user login")
        
    else:
        print("Not SZHANG or script does not exist. No task registered.")


