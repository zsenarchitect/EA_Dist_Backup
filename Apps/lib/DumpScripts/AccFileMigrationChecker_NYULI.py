import os
import asyncio
import winsound
import time
from tqdm import tqdm
from colorama import Fore, Style
from datetime import datetime

class ACCMigrationChecker:
    def __init__(self, project_folder, folder_names_to_check, acc_project_name, acc_project_inner_folder_name, prefix, limit):
        """
        Initialize the ACCMigrationChecker class with project details and path length limit.
        
        Args:
            project_folder (str): Path to the project folder.
            folder_names_to_check (list): List of folder names to check for exclusion.
            acc_project_name (str): Name of the ACC project.
            acc_project_inner_folder_name (str): Folder name in the ACC project.
            prefix (str): Prefix path for ACC migration.
            limit (int): Maximum allowed path length.
        """
        self.project_folder = project_folder
        self.acc_project_name = acc_project_name
        self.folder_names_to_check = folder_names_to_check
        self.acc_project_inner_folder_name = acc_project_inner_folder_name
        self.prefix = prefix
        self.limit = limit


    async def check_path_length(self, job_folder):
        """
        Check if any file path will exceed the defined length limit after adding the prefix.
        
        Args:
            job_folder (str): The job folder to check.
        
        Returns:
            list: A list of tuples containing the original and new paths for files that exceed the limit.
        """
        affected_files = []
        file_paths = []

        # Collect all file paths first
        for root, dirs, files in os.walk(job_folder):
            for file in files:
                full_path = os.path.join(root, file)
                
                # Get the list of all folders in the current file's full path
                full_path_folders = os.path.normpath(root).split(os.sep)

                # If any folder in folder_names_to_check is found in the full path folders, PROCESS
                if any(folder in full_path_folders for folder in self.folder_names_to_check):
                    
                    file_paths.append(full_path)
 
        # Progress bar using tqdm
        with tqdm(total=len(file_paths), desc=Fore.GREEN + f"Checking files in {os.path.basename(job_folder)}" + Style.RESET_ALL, 
                  unit="file", bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}") as pbar:
            for original_path in file_paths:
                new_path = self.prefix + "\\" + self.acc_project_name + "\\" + "Project Files" + "\\" + self.acc_project_inner_folder_name + "\\" + original_path.replace(job_folder,"")
                new_path = new_path.replace("\\\\", "\\")

                if len(new_path) > self.limit:
                    # Get file information
                    file_info = os.stat(original_path)
                    creation_time = datetime.fromtimestamp(file_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    modified_time = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    accessed_time = datetime.fromtimestamp(file_info.st_atime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Append the file along with its timestamps
                    affected_files.append((original_path, new_path, creation_time, modified_time, accessed_time))

                pbar.update(1)

        return affected_files

    def generate_report_content(self, job_folder, affected_files, elapsed_time):
        """
        Generate the content for the report based on affected files.
        
        Args:
            job_folder (str): The job folder being checked.
            affected_files (list): List of files that exceed the length limit.
            elapsed_time (float): Time taken to perform the check.
        
        Returns:
            str: Report content as a string.
        """
        report_content = []

        if affected_files:
            report_content.append(f"Summary: {len(affected_files)} files will be affected.\n")
            report_content.append(f"Note: The warning limit is set to {self.limit} characters. The real limit is 256.\n")
            report_content.append("Details of affected files:\n")
            for i, (original, new, creation_time, modified_time, accessed_time) in enumerate(affected_files):
                detail = (f"{i+1}.\nOriginal: {original}\nNew: {new}\n"
                          f"Length: {len(original)} -> {len(new)}\n"
                          f"Created: {creation_time}\nModified: {modified_time}\nAccessed: {accessed_time}\n")
                report_content.append(detail)
        else:
            report_content.append(f"Summary: All paths are below {self.limit} length limit.\n")
        
        report_content.append(f"\nTotal time taken: {elapsed_time:.2f} seconds\n")
        return "\n".join(report_content)


    def save_text_report(self, project_folder, report_content, status):
        """
        Save the generated report to a file and open it automatically.
        
        Args:
            project_folder (str): The project folder name.
            report_content (str): The report content to save.
            status (str): The status indicating whether the project is "good" or "bad".
        """
        job_number = os.path.basename(project_folder)
        report_folder = f"L:\\4b_Applied Computing\\EnneadTab-DB\\ACC Migrate Path Length Report\\_Projects Specific Report"
        
        if not os.path.exists(report_folder):
            os.makedirs(report_folder)

        txt_filename = f"Acc Migration Filepath Length PreCheck [{job_number}]_{status}.txt"
        txt_output_path = os.path.join(report_folder, txt_filename)

        # Remove old reports with the same job number
        for file in os.listdir(report_folder):
            if file.startswith(f"Acc Migration Filepath Length PreCheck [{job_number}]_"):
                os.remove(os.path.join(report_folder, file))

        try:
            # Save the new text report
            with open(txt_output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Generated text report: {txt_output_path}")
            
            # Automatically open the generated report
            os.startfile(txt_output_path)
            
        except UnicodeEncodeError as e:
            error_txt_filename = f"Acc Migration Filepath Length PreCheck [{job_number}]_{status}_error.txt"
            error_txt_output_path = os.path.join(report_folder, error_txt_filename)
            with open(error_txt_output_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(report_content)
            print(f"Generated text report with error handling: {error_txt_output_path}\nError: {e}")
            
            # Automatically open the error report if generated
            os.startfile(error_txt_output_path)
            
        finally:
            # Play Windows system alert sound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)


async def process_project(project_folder, folder_names_to_check, acc_project_name, acc_project_inner_folder_name, prefix, limit):
    """
    Process the project folder and generate the report.
    
    Args:
        project_folder (str): Path to the project folder.
        folder_names_to_check (list): List of folders to exclude from the check.
        acc_project_name (str): Name of the ACC project.
        acc_project_inner_folder_name (str): Folder name in the ACC project.
        prefix (str): Prefix path for ACC migration.
        limit (int): Maximum allowed path length.
    """
    checker = ACCMigrationChecker(project_folder, folder_names_to_check, acc_project_name, acc_project_inner_folder_name, prefix, limit)

    start_time = time.time()
    affected_files = await checker.check_path_length(project_folder)
    elapsed_time = time.time() - start_time

    report_content = checker.generate_report_content(project_folder, affected_files, elapsed_time)
    status = "bad" if affected_files else "good"
    checker.save_text_report(project_folder, report_content, status)

    print(f"\nTotal time taken for {project_folder}: {elapsed_time:.2f} seconds\n")
    print("="*80)


if __name__ == "__main__":
    prefix = "C:\\Users\\USER.NAME\\DC\\ACCDocs\\Ennead Architects LLP"
    limit = 245

    my_project = "J:\\2151"
    acc_project_name = "2151_NYULI"
    acc_project_inner_folder_name = "00_2151"
    folder_names_to_check = [
        "2_Record",
        "01_P-Image",
        "2_Master File"
    ]

    async def main():
        tasks = [process_project(my_project, folder_names_to_check, acc_project_name, acc_project_inner_folder_name, prefix, limit)]
        await asyncio.gather(*tasks)

    asyncio.run(main())
