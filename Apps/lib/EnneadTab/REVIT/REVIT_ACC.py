_api_help_website = "https://aps.autodesk.com/en/docs/bim360/v1/reference/http/"

import os
import time
import base64
import sys
import threading
import subprocess
import logging
import uuid  # added at top for job id generation
# Setup imports
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import SECRET, DATA_FILE, NOTIFICATION

try:
    import requests
except ImportError:
    NOTIFICATION.messenger("requests module not found, please install it.")

# Setup logging
logging.basicConfig(
    filename=os.path.join(os.path.expanduser("~"), "Desktop", "EnneadTab_ACC.log"),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

def EXAMPLE_1():
    import pprint
    time_start = time.time()
    sample_project = get_project_data_by_name("2317_NYU Kimmel Garage Infill")
    if sample_project:
        project_id = sample_project["id"]
        hub_id = sample_project["relationships"]["hub"]["data"]["id"]
        pprint.pprint(get_project_revit_files_data(project_id, hub_id))

    time_end = time.time()
    print("\nTime taken: {} seconds".format(time_end - time_start))

    time_start = time.time()
    pprint.pprint(get_ACC_summary_data(show_progress=True))
    time_end = time.time()
    print("\nTime taken: {} seconds".format(time_end - time_start))

def run_example_1_in_thread():
    thread = threading.Thread(target=EXAMPLE_1)
    thread.start()
    thread.join()

def EXAMPLE_2_IMPROVED():
    print("Starting EXAMPLE_2_IMPROVED...")
    export_by_project_name_improved("2317_NYU Kimmel Garage Infill")
    print("EXAMPLE_2_IMPROVED completed.")

def export_by_project_name_improved(project_name):
    """Export all sheets and DWGs from BIM360 files in a given project with improved error handling.
    Args:
        project_name (str): The name of the project to export from.
    Returns:
        bool: True if export was successful, False otherwise.
    """
    print("Starting export for project: {}".format(project_name))
    print("Getting project data...")
    project_data = get_project_data_by_name(project_name)
    if not project_data:
        print("Project not found: {}".format(project_name))
        NOTIFICATION.messenger("Project not found: {}".format(project_name))
        return False
    print("Project data found. Project ID: {}".format(project_data["id"]))
    project_id = project_data["id"]
    hub_id = project_data["relationships"]["hub"]["data"]["id"]
    print("Getting Revit files data...")
    revit_files = get_project_revit_files_data(project_id, hub_id)
    if not revit_files:
        print("No Revit files found in project")
        NOTIFICATION.messenger("No Revit files found in project")
        return False
    print("Found {} Revit files".format(len(revit_files)))
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_folder = os.path.join(desktop_path, "cloud export")
    if not os.path.exists(output_folder):
        print("Creating output folder: {}".format(output_folder))
        os.makedirs(output_folder)
    print("Getting access token...")
    data = SECRET.get_acc_key_data()
    if not data:
        print("Failed to get ACC key data")
        return False
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")
    if not (client_id and client_secret):
        print("Missing client ID or secret")
        return False
    token_url = "https://developer.api.autodesk.com/authentication/v2/token"
    token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "data:read data:write data:create data:search bucket:read bucket:create account:read"
    }
    print("Requesting access token...")
    token_resp = requests.post(token_url, headers=token_headers, data=token_data)
    print("Token response status: {}".format(token_resp.status_code))
    print("Token response body: {}".format(token_resp.text))
    if token_resp.status_code != 200:
        print("Failed to get access token. Status code: {}".format(token_resp.status_code))
        return False
    access_token = token_resp.json().get("access_token")
    print("Access token obtained successfully")
    for i, file_data in enumerate(revit_files, 1):
        print("\nProcessing file {}/{}".format(i, len(revit_files)))
        if "data" not in file_data:
            print("Skipping file - no data found")
            continue
        file_id = file_data["data"]["id"]
        file_name = file_data["data"]["attributes"]["displayName"]
        print("Processing file: {}".format(file_name))
        versions_url = "https://developer.api.autodesk.com/data/v1/projects/{}/items/{}/versions".format(project_id, file_id)
        versions_headers = {"Authorization": "Bearer {}".format(access_token)}
        print("Getting file versions...")
        versions_resp = requests.get(versions_url, headers=versions_headers)
        print("Versions response status: {}".format(versions_resp.status_code))
        print("Versions response body: {}".format(versions_resp.text))
        if versions_resp.status_code != 200:
            print("Failed to get versions. Status code: {}".format(versions_resp.status_code))
            continue
        versions_data = versions_resp.json()
        if not versions_data.get("data"):
            print("No versions found")
            continue
        latest_version = versions_data["data"][0]
        urn = latest_version["id"]
        urn_b64 = base64.b64encode(urn.encode("utf-8")).decode("utf-8").rstrip("=")
        print("Using base64 URN: {}".format(urn_b64))
        export_url = "https://developer.api.autodesk.com/modelderivative/v2/designdata/job"
        export_headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
            "x-ads-force": "true"
        }
        export_data = {
            "input": {
                "urn": urn_b64
            },
            "output": {
                "formats": [
                    {
                        "type": "dwg",
                        "views": ["2d", "3d"]
                    },
                    {
                        "type": "pdf",
                        "views": ["2d"]
                    }
                ]
            }
        }
        print("Creating export job...")
        export_resp = requests.post(export_url, headers=export_headers, json=export_data)
        print("Export job response status: {}".format(export_resp.status_code))
        print("Export job response body: {}".format(export_resp.text))
        if export_resp.status_code == 409:
            print("Export job already in progress, skipping...")
            continue
        if export_resp.status_code == 406:
            print("File is a shallow copy, skipping...")
            continue
        if export_resp.status_code not in [200, 202]:
            print("Failed to create export job. Status code: {}".format(export_resp.status_code))
            continue
        job_id = urn_b64
        manifest_url = "https://developer.api.autodesk.com/modelderivative/v2/designdata/{}/manifest".format(urn_b64)
        manifest_headers = {"Authorization": "Bearer {}".format(access_token)}
        print("Waiting for export to complete...")
        max_retries = 10
        retry_count = 0
        while retry_count < max_retries:
            manifest_resp = requests.get(manifest_url, headers=manifest_headers)
            print("Manifest response status: {}".format(manifest_resp.status_code))
            print("Manifest response body: {}".format(manifest_resp.text))
            if manifest_resp.status_code == 404:
                print("Manifest not found, retrying... ({}/{})".format(retry_count + 1, max_retries))
                time.sleep(10)
                retry_count += 1
                continue
            if manifest_resp.status_code != 200:
                print("Failed to get manifest. Status code: {}".format(manifest_resp.status_code))
                break
            manifest_data = manifest_resp.json()
            if manifest_data["status"] == "success":
                print("Export successful, downloading files...")
                for derivative in manifest_data.get("derivatives", []):
                    if derivative["type"] in ["dwg", "pdf"]:
                        for output in derivative.get("output", []):
                            download_url = output["url"]
                            download_resp = requests.get(download_url, headers=manifest_headers)
                            if download_resp.status_code == 200:
                                output_file = os.path.join(output_folder, "{}_{}.{}".format(
                                    file_name, output["name"], derivative["type"]))
                                print("Saving file: {}".format(output_file))
                                with open(output_file, "wb") as f:
                                    f.write(download_resp.content)
                break
            elif manifest_data["status"] == "failed":
                print("Export failed")
                break
            print("Export in progress...")
            time.sleep(5)
    print("\nExport completed. Files saved to: {}".format(output_folder))
    NOTIFICATION.messenger("Export completed. Files saved to: {}".format(output_folder))
    return True

ACC_PROJECT_DETAIL_FILE = "ACC_PROJECTS_DETAILS"
def get_acc_projects_data(use_record = False):
    save_file = ACC_PROJECT_DETAIL_FILE
    if use_record:
        data = DATA_FILE.get_data(save_file, is_local=False)
        return data
    else:
        data = get_all_acc_projects_data_action()
        DATA_FILE.set_data(data, ACC_PROJECT_DETAIL_FILE, is_local=False)
        return data


def get_all_acc_projects_data_action():
    data = SECRET.get_acc_key_data()
    if not data:
        return None
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")
   
    if not (client_id and client_secret):
        return None

    token_url = "https://developer.api.autodesk.com/authentication/v2/token"
    token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "data:read data:write data:create data:search bucket:read bucket:create account:read"
    }
    token_resp = requests.post(token_url, headers=token_headers, data=token_data)
    if token_resp.status_code != 200:
        return None
    access_token = token_resp.json().get("access_token")
    if not access_token:
        return None

    hubs_url = "https://developer.api.autodesk.com/project/v1/hubs"
    hubs_headers = {"Authorization": "Bearer {token}".format(token=access_token)}
    hubs_resp = requests.get(hubs_url, headers=hubs_headers)
    if hubs_resp.status_code != 200:
        return None
    hubs_data = hubs_resp.json()
    hubs = hubs_data.get("data", [])
    if not hubs:
        return None

    all_projects_data = {}
    for hub in hubs:
        hub_id = hub.get("id")
        hub_name = hub.get("attributes", {}).get("name", "Unknown Hub")
        if not hub_id:
            continue
        projects_url = "https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects".format(hub_id=hub_id)
        projects_headers = {"Authorization": "Bearer {token}".format(token=access_token)}
        projects_resp = requests.get(projects_url, headers=projects_headers)
        if projects_resp.status_code != 200:
            all_projects_data[hub_name] = None
            continue
        projects_data = projects_resp.json()
        all_projects_data[hub_name] = projects_data

    return all_projects_data


def get_project_data_by_name(project_name):
    """Get project data by searching for a specific project name.
    
    Args:
        project_name (str): The name of the project to search for.
        
    Returns:
        dict: Project data if found, None if not found.
    """
    projects_data = get_acc_projects_data()
    if not projects_data:
        return None
        
    for hub_name, hub_data in projects_data.items():
        if not hub_data or "data" not in hub_data:
            continue
            
        for data in hub_data["data"]:
            if data["attributes"]["name"] == project_name:
                return data
                
    return None

def get_project_revit_files_data(project_id, hub_id):
    """Get Revit files data for a specific project.
    Args:
        project_id (string): The ID of the project to get Revit files for.
        hub_id (string): The hub ID for the project.
    Returns:
        list: List containing Revit files data.
    """
    data = SECRET.get_acc_key_data()
    if not data:
        return None
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")
    if not (client_id and client_secret):
        return None

    token_url = "https://developer.api.autodesk.com/authentication/v2/token"
    token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "data:read data:write data:create data:search bucket:read bucket:create account:read"
    }
    token_resp = requests.post(token_url, headers=token_headers, data=token_data)
    if token_resp.status_code != 200:
        return None
    access_token = token_resp.json().get("access_token")

    project_url = "https://developer.api.autodesk.com/project/v1/hubs/{}/projects/{}".format(hub_id, project_id)
    project_headers = {"Authorization": "Bearer {}".format(access_token)}
    project_resp = requests.get(project_url, headers=project_headers)
    if project_resp.status_code != 200:
        return None
    project_data = project_resp.json()
    root_folder_id = project_data.get("data", {}).get("relationships", {}).get("rootFolder", {}).get("data", {}).get("id")
    if not root_folder_id:
        return None

    revit_files = []
    def search_folder(folder_id):
        items_url = "https://developer.api.autodesk.com/data/v1/projects/{}/folders/{}/contents".format(project_id, folder_id)
        items_headers = {"Authorization": "Bearer {}".format(access_token)}
        items_resp = requests.get(items_url, headers=items_headers)
        if items_resp.status_code != 200:
            return
        items_data = items_resp.json()
        for item in items_data.get("data", []):
            if item.get("type") == "items":
                file_name = item.get("attributes", {}).get("displayName", "")
                if file_name.lower().endswith(".rvt"):
                    item_id = item.get("id")
                    detail_url = "https://developer.api.autodesk.com/data/v1/projects/{}/items/{}".format(project_id, item_id)
                    detail_headers = {"Authorization": "Bearer {}".format(access_token)}
                    detail_resp = requests.get(detail_url, headers=detail_headers)
                    if detail_resp.status_code == 200:
                        detail_data = detail_resp.json()
                        revit_files.append(detail_data)
                    else:
                        revit_files.append({"id": item_id, "error": detail_resp.text})
            elif item.get("type") == "folders":
                search_folder(item.get("id"))
    search_folder(root_folder_id)
    return revit_files

def get_ACC_summary_data(show_progress = False):
    """Get a comprehensive summary of all ACC projects and their Revit files.
    
    Returns:
        dict: A dictionary containing project information and their associated Revit files.
        Structure:
        {
            "project_name": {
                "project_name": str,
                "project_id": str,
                "hub_id": str,
                "project_type": str,
                "revit_files": {
                    "doc_name": {
                        "file_name": str,
                        "file_id": str,
                        "model_guid": str,
                        "project_guid": str,
                        "revit_project_version": str,
                        "create_time": str,
                        "create_user_name": str,
                        "last_modified_time": str,
                        "last_modified_user_name": str,
                        "storage_size": int
                    }
                }
            }
        }
    """
    all_projects_data = get_acc_projects_data()
    if not all_projects_data:
        return None


    count = 0
    total = 0
    for hub_name, hub_data in all_projects_data.items():
        if not hub_data or "data" not in hub_data:
            continue
            
        for project in hub_data["data"]:
            total += 1




    summary = {}
    project_by_year = {}
    for hub_name, hub_data in all_projects_data.items():
        if not hub_data or "data" not in hub_data:
            continue
            
        for project in hub_data["data"]:
            project_version_year = set()
            project_name = project["attributes"]["name"]
            if show_progress:
                print ("{:0{}}/{} {}".format(count+1, len(str(total)), total, project_name))    
            count += 1
            project_id = project["id"]
            hub_id = project["relationships"]["hub"]["data"]["id"]
            project_type = project["attributes"]["extension"]["data"]["projectType"]
            revit_files = get_project_revit_files_data(project_id, hub_id)
            
            processed_files = {}
            if revit_files:
                for file_data in revit_files:
                    if "data" not in file_data:
                        continue

                        
                    if not file_data.get("included") or len(file_data["included"]) == 0:
                        continue
                    file_attributes = file_data["included"][0].get("attributes", {})
                    in_depth_attributes = file_attributes.get("extension", {}).get("data", {})
                    rvt_version = in_depth_attributes.get("revitProjectVersion", "N/A")
                    model_guid = in_depth_attributes.get("modelGuid", "N/A")
                    project_guid = in_depth_attributes.get("projectGuid", "N/A")

                    project_version_year.add(str(rvt_version))

                        
                        
                    doc_name = file_attributes.get("displayName", "")
                    processed_files[doc_name] = {
                        "file_name": doc_name,
                        "file_id": file_data["data"].get("id", ""),
                        "revit_project_version": rvt_version,
                        "model_guid": model_guid,
                        "project_guid": project_guid,
                        "create_time": file_attributes.get("createTime", ""),
                        "create_user_name": file_attributes.get("createUserName", ""),
                        "last_modified_time": file_attributes.get("lastModifiedTime", ""),
                        "last_modified_user_name": file_attributes.get("lastModifiedUserName", ""),
                        "storage_size": file_attributes.get("storageSize", -1)
                    }

            summary[project_name] = {
                "project_name": project_name,
                "project_id": project_id,
                "project_type": project_type,
                "revit_files": processed_files
            }


            key_project_version_year = str(sorted(list(project_version_year)))
            if key_project_version_year not in project_by_year:
                project_by_year[key_project_version_year] = []
            project_by_year[key_project_version_year].append(project_name)

            
    save_file = "ACC_PROJECTS_SUMMARY"
    DATA_FILE.set_data(summary, save_file, is_local=False)
    
    save_file = "ACC_PROJECTS_BY_YEAR"
    DATA_FILE.set_data(project_by_year, save_file, is_local=False)

    return summary



class ACC_PROJECT_RUNNER:
    """Manages ACC project tasks and Revit automation.
    
    This class handles:
    - Loading and managing ACC project tasks
    - Starting Revit with specific versions
    - Monitoring task execution status
    - Coordinating between ACC and Revit processes
    """
    def __init__(self):
        self.global_task_file = "ACC_PROJECT_TASK_RUNNER"
        self.is_busy = False

    def _create_job_record(self, task_data):
        """Create a new job record file and return its id and path."""
        job_id = uuid.uuid4().hex
        job_file = "ACC_JOB_{0}".format(job_id)
        record = {
            "job_id": job_id,
            "state": "REVIT_STARTING",
            "created": time.time(),
            "task": task_data
        }
        DATA_FILE.set_data(record, job_file)
        return job_id, job_file

    def run_revit_action_till_failure(self, task_data):
        logging.info("Running action for project: {0}".format(task_data))
        self.active_revit_version = task_data.get("revit_version")
        logging.info("Set active_revit_version: {0}".format(self.active_revit_version))

        # ------------------------------------------------------------------
        # 1. Create a job record and get its file name
        # ------------------------------------------------------------------
        job_id, job_file = self._create_job_record(task_data)
        logging.info("Created job record: {0}".format(job_file))

        # ------------------------------------------------------------------
        # 2. Build Revit path and launch with ACC_JOB_ID env var
        # ------------------------------------------------------------------
        revit_path = "C:\\Program Files\\Autodesk\\Revit {0}\\Revit.exe".format(self.active_revit_version)
        logging.info("Attempting to start Revit at path: {0}".format(revit_path))
        try:
            env = os.environ.copy()
            env["ACC_JOB_ID"] = job_id
            subprocess.Popen(revit_path, env=env)
            logging.info("Successfully started Revit: {0}".format(revit_path))
        except Exception as e:
            logging.error("Failed to start Revit: {0}, Error: {1}".format(revit_path, e))
            # update job record to failed
            record = DATA_FILE.get_data(job_file)
            if record:
                record["state"] = "FAILED_START_REVIT"
                DATA_FILE.set_data(record, job_file)
            self.is_busy = False
            return False

        # ------------------------------------------------------------------
        # 3. Monitor job record state until completion or timeout
        # ------------------------------------------------------------------
        max_wait_cycle = 100  # 100 * 10s = approx 17 min
        wait_count = 0
        while True:
            time.sleep(10)
            record = DATA_FILE.get_data(job_file)
            if not record:
                logging.warning("Job record {0} cannot be found during wait.".format(job_file))
                wait_count += 1
            else:
                state = record.get("state")
                logging.info("Job {0} current state: {1}".format(job_id, state))
                if state == "SUCCESS":
                    logging.info("Job {0} completed successfully.".format(job_id))
                    self.is_busy = False
                    return True
                if state.startswith("FAILED"):
                    logging.warning("Job {0} failed with state {1}.".format(job_id, state))
                    self.is_busy = False
                    return False
                # If still working just continue loop
                wait_count += 1
            if wait_count > max_wait_cycle:
                logging.warning("Job {0} timed out after waiting.".format(job_id))
                if record:
                    record["state"] = "TIMEOUT"
                    DATA_FILE.set_data(record, job_file)
                self.is_busy = False
                return False

    def run_an_idle_job(self, year_version = None):
        """Find and execute an idle job matching the specified Revit version.
        
        Args:
            year_version (str, optional): Specific Revit version to target. Defaults to None.
            
        Returns:
            bool: True if a job was started successfully, False otherwise
        """
        logging.info("Starting ACC_PROJECT_RUNNER.run_an_idle_job()")
        task_data = DATA_FILE.get_data(self.global_task_file, is_local=False)
        all_projects_data = DATA_FILE.get_data("ACC_PROJECTS_SUMMARY", is_local=False)
        
        if not task_data:
            task_data = {}
            
        # Update task data from project information
        for project_name, project_data in all_projects_data.items():
            for revit_file_name, revit_file_data in project_data.get("revit_files", {}).items():
                task_name = revit_file_data.get("model_guid")
                if task_name not in task_data:
                    task_data[task_name] = {
                        "is_running": False,
                        "last_run_time": 0,
                        "project_name": project_name,
                        "revit_file": revit_file_data.get("file_name"),
                        "model_guid": revit_file_data.get("model_guid"),
                        "project_guid": revit_file_data.get("project_guid"),
                        "revit_version": revit_file_data.get("revit_project_version")
                    }
                    print("Added new task: {}".format(task_data[task_name]))
                
                task_data[task_name].update({
                    "revit_version": revit_file_data.get("revit_project_version")
                })
        
        if not task_data:
            print("No task data found after update.")
            return False

        # Process tasks in order of last run time
        task_list = list(task_data.values())
        task_list.sort(key=lambda x: x["last_run_time"], reverse=True)
        print("Found {} tasks to process".format(len(task_list)))
        
        for task in task_list:
            print("Checking task: {}_{}".format(task["project_name"], task["revit_file"]))
            
            # Skip if task is already running
            if task["is_running"]:
                logging.info("Project {}_{} is already running: {}".format(task["project_name"], task["revit_file"], task))
                print("Project {}_{} is already running".format(task["project_name"], task["revit_file"]))
                continue
                
            # Skip if Revit version is invalid
            if not isinstance(task["revit_version"], int):
                logging.warning("Revit version is not valid: {}. Skipping...".format(task["revit_version"]))
                print("Revit version is not valid: {}. Skipping...".format(task["revit_version"]))
                continue
                
            # Skip if version doesn't match requested version
            if str(year_version) and str(task["revit_version"]) != str(year_version):
                logging.info("Revit version is not the same as the year version: {}. Skipping...".format(task["revit_version"]))
                print("Revit version is not the same as the year version: {}. Skipping...".format(task["revit_version"]))
                continue

            # Start the task
            logging.info("Project is not running: {}. Locking and running now...".format(task))
            print("Project is not running: {}_{}. Locking and running now...".format(task["project_name"], task["revit_file"]))
            
            DATA_FILE.set_data(task_data, self.global_task_file, is_local=False)
            self.is_busy = True
            self.run_revit_action_till_failure(task)
            return True
            
        return False

def batch_run_projects():
    """Run a batch of ACC projects with specified Revit version.
    
    This function:
    - Creates an ACC_PROJECT_RUNNER instance
    - Attempts to run projects up to MAX_RUN_TIME times
    - Waits appropriate time between attempts
    - Logs progress and results
    """
    logging.info("Starting batch_run_projects()")
    print("Starting batch_run_projects()")
    acc_project_runner = ACC_PROJECT_RUNNER()
    MAX_RUN_TIME = 5
    count = 0
    
    while count < MAX_RUN_TIME:
        print("Attempt {} of {}".format(count + 1, MAX_RUN_TIME))
        
        if not acc_project_runner.is_busy:
            if acc_project_runner.run_an_idle_job(year_version = "2025"):
                print("Job finished successfully, waiting 60 seconds before next attempt so revit properly shut down")
                time.sleep(60)
            else:
                print("No idle jobs found, waiting 10 seconds before next attempt")
                time.sleep(10)
        else:
            print("Runner is busy, waiting 60 seconds before next attempt")
            time.sleep(60)
            
        count += 1
        logging.info("Batch run count: {}".format(count))
    
    logging.info("Max run time reached, breaking loop.")
    print("Max run time reached, breaking loop.")

if __name__ == "__main__":
    print("Script started from __main__.")
    logging.info("Script started from __main__.")
    batch_run_projects()