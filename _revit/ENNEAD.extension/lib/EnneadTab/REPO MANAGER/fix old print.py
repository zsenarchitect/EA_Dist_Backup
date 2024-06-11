import os
import re


def convert_print_statements(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()

    new_content = []
    old_print_pattern = re.compile(r'^(\s*)print\s+([^(\s].*)')

    for line in content:
        match = old_print_pattern.match(line)
        if match:
            indentation = match.group(1)
            print_content = match.group(2)
            print_content = re.sub(r';\s*$', '', print_content)
            new_line = '{}print({})\n'.format(indentation, print_content)
            new_content.append(new_line)
        else:
            new_content.append(line)

    with open(file_path, 'w') as file:
        file.writelines(new_content)

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            #print (file_path)
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                print("Converting '{}'...".format(file_path))
                try:
                    convert_print_statements(file_path)
                except:
                    pass
    print("All files have been converted.")

if __name__ == '__main__':

    folders = [r"C:\Users\szhang\github\EnneadTab-for-Revit", r"C:\Users\szhang\github\EnneadTab-for-Rhino"]
    for folder in folders:
        process_directory(folder)

