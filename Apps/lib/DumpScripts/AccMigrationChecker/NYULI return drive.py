from data import ACC_MAPPING
import os
import time
import filecmp
from tqdm import tqdm  # Import tqdm for progress bar
from datetime import datetime  # Import datetime for timestamp
import shutil
import tkinter.messagebox as messagebox

ACC_PREFIX = f"C:\\Users\\{os.getlogin()}\\DC\\ACCDocs\\Ennead Architects LLP\\{ACC_MAPPING['2151']['acc_project_name']}\\Project Files\\{ACC_MAPPING['2151']['acc_project_inner_folder_name']}"
J_DRIVE_PREFIX = ACC_MAPPING['2151']['project_folder']

IS_GOOD_FOLDER_ONLY = False

# compare two folders and give report
# report = filecmp.dircmp(ACC_PREFIX, J_DRIVE_PREFIX)
# report.report()
SITUATIONS = ["Do not have J drive cousin, can safely copy back", 
            "Have J drive cousin but different content, you should manually check copy or not copy", 
            "Have J drive cousin but same content, no need to copy back"]

IS_REAL_COPY = True

class FileInfo:
    def __init__(self, root, file):
        self.acc_full_path = os.path.join(root, file)
        

        self.acc_size = os.path.getsize(self.acc_full_path)
        self.acc_modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(self.acc_full_path)))
        self.acc_creation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(self.acc_full_path)))

        # find the matching root in J drive
        matching_root = root.replace(ACC_PREFIX, J_DRIVE_PREFIX)
        self.j_drive_full_path = os.path.join(matching_root, file)
        self.has_j_drive_cousin = os.path.exists(self.j_drive_full_path)
        self.is_same_file = False
        if self.has_j_drive_cousin:
            self.j_drive_size = os.path.getsize(self.j_drive_full_path)
            self.j_drive_modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(self.j_drive_full_path)))
            self.j_drive_creation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(self.j_drive_full_path)))

            # Compare if two files are the same based on content only
            self.is_same_file = filecmp.cmp(self.acc_full_path, self.j_drive_full_path, shallow=False)
            

        if self.has_j_drive_cousin:
            self.should_copy_back = False
            if self.is_same_file:
                self.situation = SITUATIONS[2]
            else:
                self.situation = SITUATIONS[1]
        else:
            self.should_copy_back = True
            self.situation = SITUATIONS[0]


            
    def get_details(self):
        out = f"{self.acc_full_path}\n"
        out += f"Size: {self.acc_size / (1024 * 1024):.2f} MB\n"
        out += f"Modified: {self.acc_modified_time}\n"
        out += f"Created: {self.acc_creation_time}\n"

        if self.has_j_drive_cousin:
            out += "Has a J Drive cousin:\n"
            out += f"{self.j_drive_full_path}\n"
            out += f"Size: {self.j_drive_size / (1024 * 1024):.2f} MB\n"
            out += f"Modified: {self.j_drive_modified_time}\n"
            out += f"Created: {self.j_drive_creation_time}\n"
            out += "Same file\n" if self.is_same_file else "Different file\n"
        else:
            out += "No J Drive cousin\n"

        # Improved readability for the should copy back message
        color = 'green' if self.should_copy_back else 'red'
        out += f"Ready to copy back: <strong style='color: {color};'>{self.should_copy_back}</strong>\n"
        out += "-" * 80 + "\n"
        return out

def is_good_folder(folder):
    for folder_name in ACC_MAPPING['2151']['folder_names_to_check']:
        if folder_name in folder:
            return True
    return False

class ReturnDriveChecker:
    def check_return_drive(self):

        if IS_REAL_COPY:
            response = messagebox.askyesno("Confirm Copy", "This is a real copy operation. Do you want to copy all files back to J drive?")
            if not response:  # If the user selects 'No'
                print("Operation cancelled by the user.")
                return  # Terminate the app
        # walk all files in the return drive
        files_info = []  # List to store FileInfo objects
        output_file_path = os.path.join("J:\\2151", "return_drive_report.html")
        
        total_files_count = sum(len(files) for _, _, files in os.walk(ACC_PREFIX))  # Count total files

        start_time = time.time()  # Record start time

        with tqdm(total=total_files_count, desc="Processing files", colour='green') as pbar:
            for root, dirs, files in os.walk(ACC_PREFIX):
                if IS_GOOD_FOLDER_ONLY and not is_good_folder(root):
                    continue

                for file in files:
                    file_info = FileInfo(root, file)  # Create FileInfo object
                    files_info.append(file_info)  # Add to list
                    pbar.update(1)  # Update progress bar

                    if IS_REAL_COPY:
                        if file_info.should_copy_back:
                            shutil.copy(file_info.acc_full_path, file_info.j_drive_full_path)

        end_time = time.time()  # Record end time
        total_time = end_time - start_time  # Calculate total processing time

        # Sort files by modified time
        files_info.sort(key=lambda x: x.acc_modified_time, reverse=True)

        total_size = sum(file.acc_size for file in files_info)
        total_files = len(files_info)

        # Calculate totals for copy back
        should_copy_back_count = sum(1 for file in files_info if file.should_copy_back)
        should_not_copy_back_count = total_files - should_copy_back_count
        total_copy_back_size = sum(file.acc_size for file in files_info if file.should_copy_back) / (1024 * 1024 * 1024)  # in GB

        # Get the current timestamp
        report_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(output_file_path, 'w') as output_file:
            output_file.write("<html><head><style>\n")
            output_file.write("body { font-family: 'Helvetica', sans-serif; }\n")  # Set Helvetica font
            output_file.write("</style></head><body>\n")
            output_file.write("<h1>Return Drive Report</h1>\n")
            output_file.write(f"<p><strong>Report generated on:</strong> {report_timestamp}</p>\n")  # Add timestamp
            output_file.write(f"<p><strong>Total files to copy back:</strong> {should_copy_back_count} (Total size: {total_copy_back_size:.2f} GB)</p>\n")
            output_file.write(f"<p><strong>Total files not to copy back:</strong> {should_not_copy_back_count}</p>\n")
            output_file.write(f"<p><strong>Total processing time:</strong> {int(total_time // 60)} minutes {total_time % 60:.2f} seconds</p>\n")
            if IS_GOOD_FOLDER_ONLY:
                output_file.write("<p><strong>Only check files in the following folders:</strong></p>\n<ul>\n")
                for folder_name in ACC_MAPPING['2151']['folder_names_to_check']:
                    output_file.write(f"<li>{folder_name}</li>\n")
                output_file.write("</ul>\n")

            output_file.write(f"<br>It compares files in {ACC_PREFIX}.<br>\n")
            output_file.write(f"<br>There are totally {len(SITUATIONS)} situations to report. Click to expand.<br>\n")
            output_file.write("<ul>\n")
            for i, situation in enumerate(SITUATIONS):
                output_file.write(f"<br><li> {situation} </li><br>\n")
            output_file.write("</ul>\n")

            
            output_file.write("<h2>Sorted report detail by modified time</h2>\n")
            output_file.write(f"<p><strong>Total files:</strong> {total_files}</p>\n")
            output_file.write(f"<p><strong>Total size:</strong> {total_size / (1024 * 1024 * 1024):.2f} GB</p>\n\n")

            for j, situation in enumerate(SITUATIONS):
                output_file.write(f"<h2 onclick=\"toggleVisibility('situation-{j}')\" style='cursor: pointer;'>&#9658; {j + 1}/{len(SITUATIONS)}. {situation}</h2>\n")
                output_file.write(f"<div id='situation-{j}' style='display: none;'>\n")  # Initially collapsed
                files_in_situation = [file_info for file_info in files_info if file_info.situation == situation]
                for i, file_info in enumerate(files_in_situation):
                    output_file.write(f"<h3>File {i + 1}/{len(files_in_situation)}</h3>\n")
                    output_file.write(file_info.get_details().replace("\n", "<br>"))  # Use get_details method and replace newlines with <br>
                output_file.write("</div>\n")  # Close the situation div


            # Add JavaScript for toggling visibility
            output_file.write("<script>\n")
            output_file.write("function toggleVisibility(id) {\n")
            output_file.write("    var element = document.getElementById(id);\n")
            output_file.write("    if (element.style.display === 'none') {\n")
            output_file.write("        element.style.display = 'block';\n")
            output_file.write("    } else {\n")
            output_file.write("        element.style.display = 'none';\n")
            output_file.write("    }\n")
            output_file.write("}\n")
            output_file.write("</script>\n")

            output_file.write("</body></html>")

        # Open the output file
        os.startfile(output_file_path)  # This works on Windows

        return
        # print this text fiel to printer "east_sm_B&W on eany-print01"
        with open(output_file_path, 'r') as file:
            printer_name = "east_sm_B&W on eany-print01"
            import win32print
            win32print.PrintFile(printer_name, file.name, {})

if __name__ == "__main__":
    checker = ReturnDriveChecker()
    checker.check_return_drive()
