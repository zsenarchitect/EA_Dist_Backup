import os

# Define the line you want to remove
line_to_remove = '#! python 2\n'

# Function to walk through the directory and remove the line
def remove_line_in_scripts(root_folder):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                file_path = os.path.join(root, file)
                
                # Try to read the file and remove the line if present
                try:
                    with open(file_path, 'r') as f:
                        content = f.readlines()
                except:
                    print("!!!!!!!!!!!!!!!!!!cannot open file:", file_path)
                    continue

                # Remove the inserted line if it exists at the top of the file
                if content and content[0].strip() == line_to_remove.strip():
                    content.pop(0)
                    try:
                        with open(file_path, 'w') as f:
                            f.writelines(content)
                    except:
                        print("!!!!!!!!!!!!!!!!!!cannot write to file:", file_path)

# Main block to run the function
if __name__ == "__main__":
    # Specify your folder path
    root_folder = r"C:\Users\szhang\design-repo\EnneadTab-OS\Apps"  # Update to your folder path
    remove_line_in_scripts(root_folder)
