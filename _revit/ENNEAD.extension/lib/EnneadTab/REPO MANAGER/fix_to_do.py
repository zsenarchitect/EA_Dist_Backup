import os
import re
import webbrowser

parent_folder = os.path.dirname(os.path.dirname(__file__))

import traceback
import sys
sys.path.append(parent_folder)

import ENVIRONMENT, NOTIFICATION

class ToDoFinder:
    
    graphic_settings = {
        'background_color': 'black',
        'font_family': 'Helvetica, Arial, sans-serif',
        'text_color': 'white'
    }

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.result = []
        self.report_path = os.path.join(os.path.expanduser("~/Desktop"), "todo_report.html")

    def search_variations_of_todo(self):
        # Define a regular expression pattern to match variations of "TO-DO"
        todo_pattern = re.compile(r'to[- ]?do', re.IGNORECASE)

        for root, dirs, files in os.walk(self.folder_path):
            # exclude vitural env
            if ".venv" in root:
                continue
            for filename in files:
                if not filename.endswith(".py"):
                    continue

                
                file_path = os.path.join(root, filename)

                # exlcude current file
                if file_path == os.path.realpath(__file__):
                    continue
                
                matching_lines = []
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()
                    for line_number, line in enumerate(lines, start=1):
                        if todo_pattern.search(line):
                            matching_lines.append((line_number, line.strip()))

                            # this can show a bit more of context
                            count = 0
                            this_line = line_number
                            while this_line+1< len(lines) and count < 2:
                                matching_lines.append((this_line + 1, lines[this_line+1].strip()))
                                count += 1
                                this_line+= 1
                            matching_lines.append(("XXX", "XXX"))
                     
                if matching_lines:
                    self.result.append((file_path, matching_lines))

    def generate_html_report(self):
        with open(self.report_path, 'w', encoding='utf-8') as report_file:
            report_file.write("<html><head><title>TO-DO Finder Report</title></head><body>")
            report_file.write("<style>")
            report_file.write("body {{ background-color: {}; font-family: {}; color: {}; }}"
                              .format(self.graphic_settings['background_color'], self.graphic_settings['font_family'], self.graphic_settings['text_color']))
            report_file.write("h1 {{ font-size: 20px; font-weight: bold; }}")
            report_file.write("h2 {{ font-size: 16px; color: lightgrey; }}")
            report_file.write("h3 {{ font-size: 5px; color: lightgrey; }}")
            report_file.write("ol {{ list-style-type: none; margin: 0; padding: 0; }}")
            report_file.write("li {{ margin-bottom: 20px; }}")  # Increased margin
            report_file.write(".filename {{ font-size: 30px; color: white; }}")  # Larger font size and white color
            report_file.write(".link {{ font-size: 5px; color: white; }}")  # Larger font size and white color
            report_file.write("</style>")
            
            report_file.write("<h1>EnneadTab unfinished business in {}</h1>"
                              .format(self.folder_path))
            
            report_file.write("<h1>Files containing variations of 'TO-DO':</h1>")
            report_file.write("<br><br>")  # Add 2 empty gap lines

            i = 0
            total = len(self.result)
            for file_path, matching_lines in self.result:
                i += 1
                file_name = os.path.basename(file_path)
                report_file.write("<h2 class='filename'>{}/{}:{}</h2>"
                                  .format(i, total,file_name))  # Apply the class to increase font size
                # Create a clickable link for the file path using an anchor tag
                report_file.write("<h3 class='link'><a href='file://{0}' target='_blank'>{0}</a></h3>".format(file_path))
                report_file.write("<ol>")
                for line_number, line_content in matching_lines:
                    if line_number == "XXX":
                        report_file.write("<br>")
                    else:
                        report_file.write("<li>Line {}: {}</li>"
                                        .format(line_number, line_content))
                report_file.write("</ol>")
                report_file.write("<br><br>")  # Add 2 empty gap lines
            report_file.write("</body></html>")


    def print_html_report(self):
        webbrowser.open("file://{}".format(self.report_path))

def main():
    folders = [ENVIRONMENT.WORKING_FOLDER_FOR_REVIT,
               ENVIRONMENT.WORKING_FOLDER_FOR_RHINO]

    for folder in folders:
        if not os.path.exists(folder):
            continue
        todo_finder = ToDoFinder(folder)
        todo_finder.search_variations_of_todo()

        
        # Generate and open an HTML report on the desktop
        todo_finder.generate_html_report()
        NOTIFICATION.messenger(main_text="Detailed TO-DO generated!")
        
        # Open the HTML report in the default web browser
        todo_finder.print_html_report()

if __name__ == "__main__":
    main()
