"""This should be compiled to exe from python 3 and make exe so it not holding up CPU
well i could use WEB module to make it work in production framework but it is better to try to 
fetch update before the actual hosting software because things like rui, layout yaml .etc need to need ready before the excuation of an EnneadTab.

Especially rhino .rui have a fallback saving mechinique that if i try to download rui during rhin ooopening, the new rui will be overrideen by session rui when closed...."""
import requests
import zipfile
import os
import shutil
import time
import traceback
import getpass

class RepositoryUpdater:
    def __init__(self, repo_url, extract_to):
        self.repo_url = repo_url
        self.extract_to = os.path.expanduser(extract_to)

        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)
            
        self.final_folder_name = self.extract_repo_name(repo_url)
        self.final_dir = os.path.join(self.extract_to, self.final_folder_name)
    
    def extract_repo_name(self, url):
        if '/archive/' in url:
            parts = url.split('/')
            repo_index = parts.index('archive') - 1
            return parts[repo_index]
        return "Repository"
    
    def run_update(self):
        self.download_zip()
        self.extract_zip()
        self.update_files()
        try:
            self.cleanup()
        except:
            pass
    
    def download_zip(self):
        response = requests.get(self.repo_url, stream=True)
        if response.status_code == 200:
            self.zip_path = os.path.join(self.extract_to, "repo.zip")
            wait = 0
            while wait < 10:
                if os.path.exists(self.zip_path):
                    break
                time.sleep(1)
                wait+= 1
            with open(self.zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Zip file downloaded successfully.")
        else:
            raise Exception("Failed to download the repository. Status code: {}".format(response.status_code))
    
    def extract_zip(self):
        self.temp_dir = os.path.join(self.extract_to, "temp_extract")
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        self.source_dir = os.path.join(self.temp_dir, os.listdir(self.temp_dir)[0])
        print("Zip file extracted.")
    
    def update_files(self):
        if not os.path.exists(self.final_dir):
            os.makedirs(self.final_dir)
        
        # Force copy everything over
        source_files = {os.path.join(dp, f): os.path.relpath(os.path.join(dp, f), self.source_dir) for dp, dn, filenames in os.walk(self.source_dir) for f in filenames}
        for src_path, rel_path in source_files.items():
            tgt_path = os.path.join(self.final_dir, rel_path)
            os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
            shutil.copy2(src_path, tgt_path)

            
        # Delete files older than 3 days
        now = time.time()
        three_days_ago = now - 3 * 24 * 60 * 60
        for dp, dn, filenames in os.walk(self.final_dir):
            for f in filenames:
                file_path = os.path.join(dp, f)
                if os.stat(file_path).st_mtime < three_days_ago:
                    os.remove(file_path)
                    try:
                        os.rmdir(dp)  # Attempt to remove the directory if empty
                    except OSError:
                        pass
        print("Files have been updated.")
    
    def cleanup(self):
        shutil.rmtree(self.temp_dir)
        os.remove(self.zip_path)
        print("Cleanup completed.")

def save_traceback_and_open(user, error_message):
    error_path = os.path.expanduser("~/Desktop/GIT_CLONE_error.txt")  

    with open(error_path, 'w') as f:
        f.write(error_message)
    if user in ["szhang", "Sen Zhang"]:
        os.startfile(error_path)

def main():
    repo_url = "https://github.com/zsenarchitect/EA_Dist/archive/refs/heads/master.zip"
    extract_to = r"~\Documents\EnneadTab Ecosystem"
    updater = RepositoryUpdater(repo_url, extract_to)
    updater.run_update()

if __name__ == '__main__':

    try:
        main()
    except Exception as e:
        error_info = traceback.format_exc()
        username = getpass.getuser()
        save_traceback_and_open(username, error_info)

