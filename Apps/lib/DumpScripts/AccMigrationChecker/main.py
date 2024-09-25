"""
Main module for processing ACC project folders.
"""

import os
import time
from datetime import datetime

from data import ACC_MAPPING
from setting import PREFIX_TEMPLATE, LIMIT
from AccFileMigrationChecker import ACCMigrationChecker
from utility import log_progress
from DiskSpaceReleaser import DiskSpaceReleaser

def process_project(info):
    """
    Process the project folder to check path lengths and copy files to ACC.

    Args:
        info (dict): Dictionary containing project information. Expected keys:
            - project_folder (str): Path to the project folder.
            - acc_project_name (str): Name of the ACC project.
            - acc_project_inner_folder_name (str): Inner folder name in the ACC project.
            - folder_names_to_check (list): List of folder names to check.
            - cutoff_days (int): Number of days to consider for file age.
            - is_real_copy (bool): Flag indicating if the copy should be real.

    Returns:
        None
    """
    start_time = datetime.now()
    project_folder = info["project_folder"]
    acc_project_name = info["acc_project_name"]
    acc_project_inner_folder_name = info["acc_project_inner_folder_name"]
    folder_names_to_check = info["folder_names_to_check"]
    cutoff_days = info["cutoff_days"]
    is_real_copy = info["is_real_copy"]

    real_acc_prefix = PREFIX_TEMPLATE.format(os.getlogin())

    log_progress("Starting path length check and file copy", start_time)

    checker = ACCMigrationChecker(project_folder, folder_names_to_check, acc_project_name, 
                                  acc_project_inner_folder_name, real_acc_prefix, LIMIT, 
                                  cutoff_days, is_real_copy)

    recent_long_files, older_long_files, all_files_in_checked_folder = checker.check_and_copy_files()
    elapsed_time = time.time() - start_time.timestamp()

    report_content = checker.generate_report_content(recent_long_files, older_long_files, elapsed_time)
    checker.save_text_report(
        report_content, 
        "bad" if recent_long_files or older_long_files else "good",
        "summary"
    )

    checker.save_text_report(
        checker.generate_copy_report_content(recent_long_files, all_files_in_checked_folder, elapsed_time), 
        "_",
        "simulated_copy"
    )

    log_progress("Path length check and file copy completed", start_time)

    total_elapsed_time = datetime.now() - start_time
    print(f"\nTotal time taken for {project_folder}: {total_elapsed_time}\n")
    print("="*80)



    

def main():
    """
    Main function to process the ACC project folders.
    """
    for info in ACC_MAPPING.values():
        process_project(info)

    print("Done")

if __name__ == "__main__":
    main()