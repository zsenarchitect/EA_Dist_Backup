import os
import asyncio
import winsound
import time
import random
from tqdm import tqdm
from colorama import Fore, Style

class ACCMigrationChecker:
    def __init__(self, drive, prefix, limit):
        self.drive = drive
        self.prefix = prefix
        self.limit = limit

    def get_job_folders(self):
        """Get main job folders in the drive"""
        folders = [os.path.join(self.drive, f) for f in os.listdir(self.drive) if os.path.isdir(os.path.join(self.drive, f))]
        folders = [ f for f in folders if "ennead" not in f.lower()]
        # random.shuffle(folders)
        # return folders
        return sorted(folders, reverse=True)

    async def check_path_length(self, job_folder):
        """Check if any file path will exceed the limit after adding the prefix"""

        
        affected_files = []
        file_paths = []
        
        # Collect all file paths first to get the correct count
        for root, dirs, files in os.walk(job_folder):
            for file in files:
                file_paths.append(os.path.join(root, file))
        
        # Use tqdm for the progress bar with custom color and style
        with tqdm(total=len(file_paths), desc=Fore.GREEN + f"Checking files in {os.path.basename(job_folder)}" + Style.RESET_ALL, unit="file", bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}") as pbar:
            for original_path in file_paths:
                
                # do not check those special folder such as marketing
                
                new_path = self.prefix + "\\" + os.path.basename(job_folder) + "_SAMPLE_NAME" + "\\" + "Project Files" + "\\" + os.path.basename(job_folder) + "_SAMPLE_NAME" + "\\" + original_path.replace(job_folder,"")
                # # C:\Users\szhang\ACCDocs\Ennead Architects LLP\1643_LHH\Project Files\00_1643 LHH
                # Replace double backslashes with a single backslash to mimic Windows OS behavior
                new_path = new_path.replace("\\\\", "\\")
                if len(new_path) > self.limit:
                    affected_files.append((original_path, new_path))
                pbar.update(1)

  
        return affected_files

    def generate_report_content(self, job_folder, affected_files, elapsed_time):
        """Generate report content for the job folder"""
        report_content = []
        if affected_files:
            summary = f"Summary: {len(affected_files)} files will be affected.\n"
            report_content.append(summary)
            note = f"Note: The warning limit is set to {self.limit} characters. The real limit is 256, but it should allow username variation and project name customizations and some contingency.\n"
            report_content.append(note)
            details_header = "Details of affected files:\n"
            report_content.append(details_header)
            for i, pair in enumerate(affected_files):
                original, new = pair
                detail = f"{i+1}.\nOriginal: {original}\nNew: {new}\nLength: {len(original)} -> {len(new)}\n"
                report_content.append(detail)
        else:
            summary = f"Summary: All paths are below {self.limit} length limit.\n"
            report_content.append(summary)
        report_content.append(f"\nTotal time taken: {elapsed_time:.2f} seconds\n")
        return "\n".join(report_content)

    def save_text_report(self, drive_letter, job_folder, report_content, status):
        """Save a text report for the job folder"""
        job_number = os.path.basename(job_folder)
        report_folder = f"L:\\4b_Applied Computing\\EnneadTab-DB\\ACC Migrate Path Length Report\\{drive_letter} Drive Report"
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
        except UnicodeEncodeError as e:
            error_txt_filename = f"Acc Migration Filepath Length PreCheck [{job_number}]_{status}_error.txt"
            error_txt_output_path = os.path.join(report_folder, error_txt_filename)
            with open(error_txt_output_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(report_content)
            print(f"Generated text report with error handling: {error_txt_output_path}\nError: {e}")
        finally:
            # Play Windows system alert sound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

async def process_drive(drive, prefix, limit):
    checker = ACCMigrationChecker(drive, prefix, limit)
    drive_letter = drive[0]  # Get the drive letter (J or I)
    job_folders = checker.get_job_folders()  # Get all job folders

    for job_folder in job_folders:
        start_time = time.time()
        affected_files = await checker.check_path_length(job_folder)
        elapsed_time = time.time() - start_time
        report_content = checker.generate_report_content(job_folder, affected_files, elapsed_time)
        status = "bad" if affected_files else "good"
        checker.save_text_report(drive_letter, job_folder, report_content, status)
        print(f"\nTotal time taken for {job_folder}: {elapsed_time:.2f} seconds\n")
        print("="*80)
    
    if not job_folders:
        print(f"No job folders found in {drive}.")

if __name__ == "__main__":
    prefix = "C:\\Users\\TYPICAL.USERNAME\\DC\\ACCDocs\\Ennead Architects LLP\\"
    limit = 245

    drives = [
        "I:\\",
        "J:\\", 
        "W:\\INOVA\\",
        ]

    async def main():
        tasks = [process_drive(drive, prefix, limit) for drive in drives]
        await asyncio.gather(*tasks)

    asyncio.run(main())
