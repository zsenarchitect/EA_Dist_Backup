import os
import ctypes
from ctypes import wintypes
from utility import format_size  # Ensure this function is defined in utility
from data import ACC_MAPPING
from setting import PREFIX_TEMPLATE

# Constants to mark files for cloud storage handling
FILE_ATTRIBUTE_OFFLINE = 0x1000

# Define the Windows API functions
kernel32 = ctypes.windll.kernel32

class DiskSpaceReleaser:
    def __init__(self, folder):
        """
        Initialize the DiskSpaceReleaser with the target folder.

        Args:
            folder (str): The folder path where files will be marked for cloud storage.
        """
        self.folder = folder
        self.success_count = 0
        self.failed_count = 0
        self.total_freed_space = 0

    def get_disk_space(self):
        """
        Get the total and free disk space of the drive containing the folder.

        Returns:
            tuple: Total space and free space in bytes.
        """
        _, total_space, free_space = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
        drive = os.path.splitdrive(self.folder)[0] + "\\"
        kernel32.GetDiskFreeSpaceExW(wintypes.LPWSTR(drive), ctypes.byref(free_space), ctypes.byref(total_space), None)
        return total_space.value, free_space.value

    def free_up_space(self, file_path):
        """
        Mark the file as offline to free up space.

        Args:
            file_path (str): The path of the file to mark as offline.
        """
        try:
            # Mark the file as offline (removes local copy but keeps the cloud version)
            result = kernel32.SetFileAttributesW(wintypes.LPWSTR(file_path), FILE_ATTRIBUTE_OFFLINE)
            
            if result != 0:
                self.success_count += 1
                file_size = os.path.getsize(file_path)
                self.total_freed_space += file_size
            else:
                self.failed_count += 1
                print(f"Failed to free up space for: {file_path}, error code: {ctypes.GetLastError()}")
        except Exception as e:
            self.failed_count += 1
            print(f"Error occurred while processing {file_path}: {e}")

    def release_space(self):
        """
        Release space for all files in the specified folder.
        """
        # Check disk space before
        total_space_before, free_space_before = self.get_disk_space()
        print (f"Trying to free up space for {self.folder}")
        print(f"Total space before: {format_size(total_space_before)}, Free space before: {format_size(free_space_before)}")

        # Loop over the directory and free up space for each file
        for subfolder, _, files in os.walk(self.folder):
            for file in files:
                # Construct the full file path
                file_path = os.path.join(subfolder, file)
                self.free_up_space(file_path)

        # Check disk space after
        total_space_after, free_space_after = self.get_disk_space()
        print(f"Total space after: {format_size(total_space_after)}, Free space after: {format_size(free_space_after)}")

        # Print final status
        print(f"\nFinal Status: {self.success_count} files successfully released, {self.failed_count} files failed.")
        print(f"Total disk space freed: {format_size(self.total_freed_space)}.")

# Example usage
if __name__ == "__main__":
    for info in ACC_MAPPING.values():
        real_acc_prefix = PREFIX_TEMPLATE.format(os.getlogin())
        acc_project_name = info["acc_project_name"]
        releaser = DiskSpaceReleaser(os.path.join(real_acc_prefix, acc_project_name))
        releaser.release_space()