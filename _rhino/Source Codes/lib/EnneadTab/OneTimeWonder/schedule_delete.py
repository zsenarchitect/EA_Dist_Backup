import os

def delete_files(file_list):
    """Deletes files from the given list."""
    for file_path in file_list:
        try:
            os.remove(file_path)
            print("Deleted: {}".format(file_path))
        except FileNotFoundError:
            print("File not found: {}".format(file_path))
        except Exception as e:
            print("Error deleting {}: {}".format(file_path, e))

if __name__ == "__main__":
    # Example list of files to delete
    files_to_delete = [
        '/path/to/your/file1.txt',
        '/path/to/your/file2.txt',
        # Add more file paths as needed
    ]
    
    delete_files(files_to_delete)
