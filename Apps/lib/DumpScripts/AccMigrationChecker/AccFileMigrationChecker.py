import os
import winsound
from datetime import datetime, timedelta
import shutil
from tqdm import tqdm
from colorama import Fore, Style
from setting import REPORT_FOLDER
from utility import progress_bar_decorator, format_size

class ACCMigrationChecker:
    """
    Class to handle the checking and copying of files for ACC projects.
    """

    def __init__(self, project_folder, folder_names_to_check, acc_project_name, 
                 acc_project_inner_folder_name, prefix, limit, cutoff_days, 
                 is_real_copy):
        """
        Initialize the ACCMigrationChecker.

        Args:
            project_folder (str): Path to the project folder.
            folder_names_to_check (list): List of folder names to check.
            acc_project_name (str): Name of the ACC project.
            acc_project_inner_folder_name (str): Inner folder name in the ACC project.
            prefix (str): Prefix for the new path.
            limit (int): Path length limit.
            cutoff_days (int): Number of days to consider a file as recent.
            is_real_copy (bool): Flag to indicate if the copy is real.
        """
        self.project_folder = project_folder
        self.acc_project_name = acc_project_name
        self.folder_names_to_check = folder_names_to_check
        self.acc_project_inner_folder_name = acc_project_inner_folder_name
        self.prefix = prefix
        self.limit = limit
        self.cutoff_days = cutoff_days
        self.is_real_copy = is_real_copy
        self.job_number = os.path.basename(project_folder)

    def generate_new_path(self, original_path):
        """
        Generate a new path based on the original path and class attributes.

        Args:
            original_path (str): The original file path.

        Returns:
            str: The newly constructed path.
        """
        # do not use os.path.join, it will make bad path for acc
        new_path = (
                    self.prefix + "\\" + self.acc_project_name + "\\" + "Project Files" + 
                    "\\" + self.acc_project_inner_folder_name + "\\" + 
                    original_path.replace(self.project_folder, "")
                )
        return new_path.replace("\\\\", "\\")

    def is_recent_file(self, original_path):
        """
        Check if a file is recent based on the cutoff days.

        Args:
            original_path (str): Path to the file.

        Returns:
            bool: True if the file is recent, False otherwise.
        """
        current_time = datetime.now()
        time_days_ago = current_time - timedelta(days=self.cutoff_days)
        
        file_info = os.stat(original_path)
        creation_time = datetime.fromtimestamp(file_info.st_ctime)
        modified_time = datetime.fromtimestamp(file_info.st_mtime)
        accessed_time = datetime.fromtimestamp(file_info.st_atime)

        return any([
            accessed_time > time_days_ago,
            modified_time > time_days_ago,
            creation_time > time_days_ago
        ])

    def is_in_folder_names_to_check(self, root):
        """
        Check if the file path is in any of the folder names to check.

        Args:
            root (str): Root path of the file.

        Returns:
            bool: True if the file path is in any of the folder names to check, 
                  False otherwise.
        """
        for folder in self.folder_names_to_check:
            if folder in root:
                return True
        return False
   

    @progress_bar_decorator("Checking and copying files")
    def check_and_copy_files(self):
        """
        Check the path length of files and copy them to the ACC project if necessary.

        Returns:
            tuple: Lists of recent and older affected files with their original and 
                   new paths and timestamps.
        """
        recent_long_files = []
        older_long_files = []
        all_files = []
        file_paths = []

        for folder in self.folder_names_to_check:
            working_folder = os.path.join(self.project_folder, folder)

            for root, _, files in os.walk(working_folder):
                if not self.is_in_folder_names_to_check(root):
                    continue
                for file in files:
                    full_path = os.path.join(root, file)
                    file_paths.append(full_path)

        # file_paths here are files that are part of the folder check
        with tqdm(total=len(file_paths), desc=Fore.GREEN + "Hard working..." + Style.RESET_ALL, 
                      unit="file", bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}") as pbar:
            for original_path in file_paths:
                new_path = self.generate_new_path(original_path)  # Use the new method
                target_path_length = len(new_path)

                file_info = os.stat(original_path)
                creation_time = datetime.fromtimestamp(file_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                modified_time = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                accessed_time = datetime.fromtimestamp(file_info.st_atime).strftime('%Y-%m-%d %H:%M:%S')

                if target_path_length > self.limit:
                    if self.is_recent_file(original_path):
                        recent_long_files.append((original_path, new_path, creation_time, modified_time, accessed_time))
                    else:
                        older_long_files.append((original_path, new_path, creation_time, modified_time, accessed_time))

                all_files.append((original_path, new_path, creation_time, modified_time, accessed_time))

                # copy as long as is real copy and it is recent file, path length not important here because assuming have checked that before.
                if self.is_real_copy and self.is_recent_file(original_path):
                    target_folder, base_name = os.path.split(new_path)
        
                    if not os.path.exists(target_folder):
                        os.makedirs(target_folder)
                    try:
                        shutil.copy2(original_path, new_path)
                    except PermissionError:
                        print(f"\nPermission denied: {original_path}\n")

                pbar.update(1)

        return recent_long_files, older_long_files, all_files

    def generate_report_content(self, recent_long_files, older_long_files, elapsed_time):
        """
        Generate the content for the report.

        Args:
            recent_long_files (list): List of recent affected files.
            older_long_files (list): List of older affected files.
            elapsed_time (float): Time taken to check the path lengths.

        Returns:
            str: The report content.
        """
        report_content = []
        report_content.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_content.append(f"Elapsed time: {elapsed_time:.2f} seconds\n")
        report_content.append("="*80 + "\n")

        if recent_long_files:
            cutoff_date = (datetime.now() - timedelta(days=self.cutoff_days)).strftime('%Y-%m-%d')
            report_content.append("Recent files:\n")
            report_content.append(f"There are {len(recent_long_files)} files that are from folders in {self.folder_names_to_check} and path too long and are less than {self.cutoff_days} days old, which is {cutoff_date}\n")
            report_content.append("="*80 + "\n")
            for idx, (original_path, new_path, creation_time, modified_time, accessed_time) in enumerate(recent_long_files, 1):
                report_content.append(f"{idx}.\nOriginal Path: {original_path}\n")
                report_content.append(f"New Path: {new_path}\n")
                report_content.append(f"Path Length Change: {len(original_path)} -> {len(new_path)}\n")
                report_content.append(f"Creation Time: {creation_time}\n")
                report_content.append(f"Modified Time: {modified_time}\n")
                report_content.append(f"Accessed Time: {accessed_time}\n")
                report_content.append("="*80 + "\n")
            report_content.append("\n\n")
        if older_long_files:
            cutoff_date = (datetime.now() - timedelta(days=self.cutoff_days)).strftime('%Y-%m-%d')
            report_content.append("Older files:\n")
            report_content.append(f"There are {len(older_long_files)} files that are from folders in {self.folder_names_to_check} and path too long and are older than {self.cutoff_days} days, which is before {cutoff_date}\n")
            report_content.append("="*80 + "\n")
            for idx, (original_path, new_path, creation_time, modified_time, accessed_time) in enumerate(older_long_files, 1):
                report_content.append(f"{idx}.\nOriginal Path: {original_path}\n")
                report_content.append(f"New Path: {new_path}\n")
                report_content.append(f"Path Length Change: {len(original_path)} -> {len(new_path)}\n")
                report_content.append(f"Creation Time: {creation_time}\n")
                report_content.append(f"Modified Time: {modified_time}\n")
                report_content.append(f"Accessed Time: {accessed_time}\n")
                report_content.append("="*80 + "\n")
        return "".join(report_content)

    def generate_copy_report_content(self, recent_long_files, files_to_copy, elapsed_time):
        """
        Generate the content for the full report.

        Args:
            recent_long_files (list): List of recent affected files.
            files_to_copy (list): List of all files being copied.
            elapsed_time (float): Time taken to check the path lengths.

        Returns:
            str: The full report content.
        """
            
        report_content = []
        if len(recent_long_files) != 0:
            report_content.append(f"################################\nPlease note that there are still {len(recent_long_files)} recent files path too long.\nI do not recommand turn on real copy until that is fixed.\n################################\n\n")
        report_content.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_content.append(f"Files here are less than {self.cutoff_days} days old and are in {self.folder_names_to_check} folders.\n")
        report_content.append(f"Elapsed time: {elapsed_time:.2f} seconds\n")
        report_content.append("="*80 + "\n")

        report_content.append(f"All {len(files_to_copy)} files being copied:\n")
        total_size = format_size(sum(os.path.getsize(path) for path, _, _, _, _ in files_to_copy))
        report_content.append(f"Total file size is {total_size}.\nPlease make sure you have at least those amount C drive before turn on real copy.\n")
        report_content.append("="*80 + "\n")
        for idx, (original_path, new_path, creation_time, modified_time, accessed_time) in enumerate(files_to_copy, 1):
            report_content.append(f"{idx}. {new_path}\n")
            report_content.append("="*80 + "\n")
        return "".join(report_content)

    def save_text_report(self, report_content, status, report_type):
        """
        Save the report content to a text file.

        Args:
            report_content (str): The report content.
            status (str): The status of the report (good or bad).
            report_type (str): The type of the report (summary or full).

        Returns:
            bool: True if the report was saved to the L drive, False otherwise.
        """
        saved_to_l_drive = True
        txt_filename = f"Acc Migration Filepath Length PreCheck [{self.job_number}]_{status}_{report_type}.txt"
        for file in os.listdir(REPORT_FOLDER):
            if str(self.job_number) in file and report_type in file:
                os.remove(os.path.join(REPORT_FOLDER, file))
        txt_output_path = os.path.join(REPORT_FOLDER, txt_filename)


        try:
            with open(txt_output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        except (UnicodeEncodeError, PermissionError) as e:
            desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop")
            txt_output_path = os.path.join(desktop_folder, txt_filename)
            saved_to_l_drive = False

        try:
            with open(txt_output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            os.startfile(txt_output_path)
        except Exception as e:
            print(f"Failed to write report to desktop: {e}")
        finally:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

        return saved_to_l_drive





