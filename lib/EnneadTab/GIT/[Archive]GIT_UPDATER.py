"""generated from python 3.10, auto_py_to_exe.exe
need add folder path to 'git' modeule in site package"""

"""
2023-12-11 update
this attemp fails, becasue it turns out that even after packing to exe, 
the end user runing exe also need to have actual git installed and configured,
this is pretty much not ppossible with my current knowledge


2023-12-16
new hope...
how about trying this with the Cpython for pyrevit and Rhino8? no need to compile to exe...
"""
import sys
import os
import json
import traceback

try:
    # when running within EXE
    import ENVIRONMENT_CONSTANTS
except:
    #when running from python
    parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_folder)
    import ENVIRONMENT_CONSTANTS

def safe_stop(error):
    
    
    # NOTE to self: when using daily---> return early
    # when preparing EXE, do prepare output
    #  this way the global EnneadTab core importer will not freak out about missing gitdb, which is not avaible for ironpython 2.7
    # return

    print (error)
    exe_folder = "{}\Documents".format(os.environ["USERPROFILE"])
    with open("{}\\error_log.txt".format(exe_folder), "w") as f:
        f.write(error)
    os.startfile("{}\\error_log.txt".format(exe_folder))
    # sys.exit()
    

def read_json_as_dict(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
        return data




# run this if developer computer is setup with GitPython pip
try:
    #when running inside exe
    import git
except:
    
    try:
        #when running inside python
        sys.path.append(ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER_LEGACY)
        import git
    except:
        try:
            last_hope_folder = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe\\GIT_UPDATER_0.2\\_internal"
            sys.path.append(last_hope_folder)
            import git
        except:
            safe_stop(traceback.format_exc())
    
       

GIT_HOLDING_KEY = "EnneadTab_git_working_is_busy"
LOGIN_USERNAME = "zsenarchitect"
LOGIN_PASSWORD = "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"

REPO_DICT_EDITOR = {"Revit-Monopoly":"https://github.com/zsenarchitect/Revit-Monopoly.git",
                 "EnneadTab-for-Revit":"https://github.com/Ennead-Architects-LLP/EnneadTab-for-Revit.git",
                 "EnneadTab-for-Rhino": "https://github.com/zsenarchitect/EnneadTab-for-Rhino.git"}





try:
    REPO_DICT = read_json_as_dict("{}\\Git Repo.json".format(ENVIRONMENT_CONSTANTS.CORE_RESOURCES_FOLDER_FOR_PUBLISHED_REVIT))
except:
    safe_stop(traceback.format_exc())


class GitRepoManager:
    def __init__(self, repo_url):
        self.repo_url = repo_url

        self.username = LOGIN_USERNAME
        self.access_token = LOGIN_PASSWORD

    def clone(self, destination_folder):
        try:
            git.Repo.clone_from(
                url=self.repo_url,
                to_path=destination_folder,
                env={"GIT_ASKPASS": "git-askpass-helper"},
                depth=1,  # Optional: Clone only the latest commit to save bandwidth
            )
            return True
        except git.exc.GitCommandError as e:
            print("Error cloning repository: {}".format(e))
            return False

    def check_for_updates(self, local_repo_path):
        try:
            repo = git.Repo(local_repo_path)
            remote = repo.remote()
            remote.fetch()
            # Compare the local branch with the remote branch
            if repo.head.commit != remote.refs[0].commit:
                return True  # Updates available
            else:
                return False  # No updates available
        except git.exc.GitCommandError as e:
            print("Error checking for updates: {}".format(e))
            return False

    def pull_updates(self, local_repo_path):
        try:
            repo = git.Repo(local_repo_path)
            repo.git.pull()
            return True
        except git.exc.GitCommandError as e:
            print("Error pulling updates: {}".format(e))
            return False


def main_exe():
    """need GitPython pip installed
    making exe from python 3.10
    """
    print ("preparing to update Ecosystem...")


    os.environ[GIT_HOLDING_KEY] = "True"
    for repo in REPO_DICT:
        print ("Updating {}".format(repo))
        update_repo_action(repo)
    os.environ[GIT_HOLDING_KEY] = "False"
    
    
    marker = "{}\\Documents\\EnneadTab Settings\\Local Copy Dump\\{}.json".format(os.environ["USERPROFILE"], GIT_HOLDING_KEY)
    try:
        os.remove(marker)
        return True
    except:
        return False
    

        
def update_repo_action(repo_name):
    repo_url = REPO_DICT[repo_name]

    

    git_manager = GitRepoManager(repo_url)

    repo_folder =  "{}\\{}".format(ENVIRONMENT_CONSTANTS.ECOSYSTEM_FOLDER,
                                   repo_name)

    if not os.path.exists(repo_folder):
        os.makedirs(repo_folder)
        if git_manager.clone(repo_folder):
            print("Repository cloned successfully.")
            
        if not os.path.exists(repo_folder):
            os.rmdir(repo_folder)
            return
       


    if git_manager.check_for_updates(repo_folder):
        if git_manager.pull_updates(repo_folder):
            print("Updates pulled successfully.")
        else:
            print("Failed to pull updates.")
    else:
        print("No updates available.")
  

###############################################
if __name__ == '__main__':
    
    try:
        main_exe()
    except:
        safe_stop(traceback.format_exc())