import os
import io

import webbrowser


import FOLDER 
import ENVIRONMENT

import TIME 
import IMAGE

FUNCS = """
<script>
function sample_func(btn) {
  alert(btn.innerText);
  prompt("Type anything:");
  confirm("Do you want to continue?");
}

function highlightSearch() {
  var input, filter, body, p, h1, h2, li, i, txtValue;
  input = document.getElementById('searchBox');
  filter = input.value.toLowerCase();
  body = document.getElementsByTagName('body')[0];
  
  // Highlight paragraphs
  p = body.getElementsByTagName('p');
  for (i = 0; i < p.length; i++) {
    txtValue = p[i].textContent || p[i].innerText;
    if (filter === "") {
      p[i].style.backgroundColor = '';
    } else if (txtValue.toLowerCase().indexOf(filter) > -1) {
      p[i].style.backgroundColor = 'lightgreen';
    } else {
      p[i].style.backgroundColor = '';
    }
  }

  // Highlight titles
  h1 = body.getElementsByTagName('h1');
  for (i = 0; i < h1.length; i++) {
    txtValue = h1[i].textContent || h1[i].innerText;
    if (filter === "") {
      h1[i].style.backgroundColor = '';
    } else if (txtValue.toLowerCase().indexOf(filter) > -1) {
      h1[i].style.backgroundColor = 'lightgreen';
    } else {
      h1[i].style.backgroundColor = '';
    }
  }
  
  h2 = body.getElementsByTagName('h2');
  for (i = 0; i < h2.length; i++) {
    txtValue = h2[i].textContent || h2[i].innerText;
    if (filter === "") {
      h2[i].style.backgroundColor = '';
    } else if (txtValue.toLowerCase().indexOf(filter) > -1) {
      h2[i].style.backgroundColor = 'lightgreen';
    } else {
      h2[i].style.backgroundColor = '';
    }
  }

  // Highlight list items
  li = body.getElementsByTagName('li');
  for (i = 0; i < li.length; i++) {
    txtValue = li[i].textContent || li[i].innerText;
    if (filter === "") {
      li[i].style.backgroundColor = '';
    } else if (txtValue.toLowerCase().indexOf(filter) > -1) {
      li[i].style.backgroundColor = 'lightgreen';
    } else {
      li[i].style.backgroundColor = '';
    }
  }
}

function copyErrorCard(btn) {
    const card = btn.closest('.error-card');
    const text = card.textContent.replace('Copy', '').trim();
    navigator.clipboard.writeText(text).then(() => {
        btn.innerHTML = 'Copied!';
        setTimeout(() => {
            btn.innerHTML = 'Copy';
        }, 2000);
    });
}
</script>
"""

"""
EnneadTab Output Module

A sophisticated output management system for EnneadTab that provides HTML-based reporting and console output capabilities.
This module handles the formatting, styling, and display of output content through a singleton Output class.

Key Features:
    - HTML report generation with modern styling and interactive features
    - Search functionality within output content
    - Error highlighting and formatting
    - Support for different text styles (titles, subtitles, body text)
    - Copy functionality for error messages
    - Responsive design with animations
    - Environment-aware output handling (Revit/Rhino/Terminal)

Note:
    The module uses a singleton pattern to ensure consistent output handling across the application.
"""

class Style:
    """Style constants for output formatting.
    
    Defines the available text styles for output content:
        MainBody: Standard paragraph text
        Title: Main headings (h1)
        Subtitle: Secondary headings (h2)
        Footnote: Small text for additional information
    """
    MainBody = "p"
    Title = "h1"
    Subtitle = "h2"
    Footnote = "foot_note"
    

class Output:
    """Singleton class managing EnneadTab's output system.
    
    This class handles the generation and display of formatted output through HTML reports
    and console output. It supports rich text formatting, error highlighting, and
    interactive features like search and copy functionality.

    Attributes:
        _instance (Output): Singleton instance of the Output class
        _out (list): Container for output content and styling
        _report_path (str): Path to the HTML report file
        _graphic_settings (dict): Visual styling configuration
        _is_print_out (bool): Flag controlling console output based on environment

    Note:
        The class automatically detects the environment (Revit/Rhino) to adjust output behavior.
    """

    _instance = None
    _out = [] # the container for everything that iEnneadTabng
    _report_path = FOLDER.get_EA_dump_folder_file("EnneadTab Output.html")
    _graphic_settings = {
            'background_color': 'rgb(50, 50, 50)',
            'font_family': 'Helvetica, Arial, sans-serif',
            'text_color': 'white'
        }

    # when in Reivit, do not print to pollute the nice pyrevit console
    _is_print_out = not (ENVIRONMENT.IS_REVIT_ENVIRONMENT or ENVIRONMENT.IS_RHINO_ENVIRONMENT)
    
    def __new__(cls, *args, **kwargs):
        """Implements the singleton pattern for Output class.

        Returns:
            Output: The single instance of the Output class.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def write(self, content, style = Style.MainBody, as_str=False):
        """Writes content to the output buffer with specified styling.

        Args:
            content: The content to write (can be any type)
            style: The style to apply (default: Style.MainBody)
            as_str (bool): Whether to force convert content to string (default: False)

        Note:
            Content is stored in the output buffer and will be displayed when plot() is called.
            If _is_print_out is True, content is also printed to console.
        """
        if as_str:
            content = str(content)
        Output._out.append((style, content))
        if Output._is_print_out:
            print (content)

    def reset_output(self):
        """Clears the output buffer.
        
        Removes all content from the output buffer without affecting the HTML report.
        """
        Output._out = []

    def is_empty(self):
        """Checks if the output buffer is empty.

        Returns:
            bool: True if no content in output buffer, False otherwise.
        """
        return not Output._out

    def plot(self):
        """Generates and displays the HTML report if output buffer is not empty.
        
        This method:
        1. Checks if there is content to display
        2. Generates the HTML report with current content
        3. Opens the report in the default web browser
        """
        if self.is_empty():
            return
        self._generate_html_report()
        self._print_html_report()

    def _generate_html_report(self):
        """Generates the HTML report with current output content.
        
        Creates a styled HTML file with:
            - Search functionality
            - Error highlighting
            - Copy buttons for error messages
            - Responsive design
            - EnneadTab branding
        """
        with io.open(Output._report_path, 'w', encoding='utf-8') as report_file:
            report_file.write("<html><head><title>EnneadTab Output</title></head><body>")
            report_file.write("<style>")
            report_file.write("body {{ background-color: #2B1C10; font-family: {}; color: #F4E1D2; margin-left:10%;margin-right:10%;}}"
                              .format(Output._graphic_settings['font_family']))
            report_file.write("h1 {{ font-size: 35px; font-weight: bold; color: #E1D4C1; }}")
            report_file.write("h2 {{ font-size: 20px; color: #987284; }}")
            report_file.write("ul {{ list-style-type: none; margin: 20; padding: 10; }}")
            report_file.write("li {{ margin-left: 40px; color: #E1D4C1; }}") 
            report_file.write(".foot_note {{ font-size: 8px; color: #987284; }}") 
            report_file.write("""
                .error-card {
                    background: #6E493A;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 20px 0;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    animation: shake 1.2s;
                    position: relative;
                    border-left: 5px solid #987284;
                    transition: all 0.3s ease;
                    color: #F4E1D2;
                    padding-right: 80px;
                }
                .error-card::before {
                    content: '!';
                    position: absolute;
                    right: 10px;
                    top: 10px;
                    font-size: 24px;
                    transition: transform 0.3s ease;
                }
                .error-card:hover {
                    transform: scale(1.02) translateX(5px);
                    box-shadow: 0 6px 12px rgba(152,114,132,0.15);
                    background: #2B1C10;
                    border-left: 5px solid #E1D4C1;
                }
                .error-card:hover::before {
                    transform: rotate(15deg) scale(1.2);
                    animation: bounce 0.8s infinite;
                }
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    25% { transform: translateX(-5px); }
                    75% { transform: translateX(5px); }
                    animation-timing-function: ease-in-out;
                }
                @keyframes bounce {
                    0%, 100% { transform: translateY(0) rotate(15deg); }
                    50% { transform: translateY(-5px) rotate(15deg); }
                }
                .copy-btn {
                    position: absolute;
                    right: 40px;
                    top: 50%;
                    transform: translateY(-50%);
                    padding: 5px 10px;
                    background: #987284;
                    border: none;
                    border-radius: 5px;
                    color: #F4E1D2;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .copy-btn:hover {
                    background: #E1D4C1;
                    color: #2B1C10;
                }
            """)
            report_file.write("</style>")

            report_file.write(FUNCS)

            # Add the search box
            report_file.write("""
            <div style='text-align: center;'>
                <input type='text' id='searchBox' onkeyup='highlightSearch()' placeholder='Search...'>
            </div>
            """)

            report_file.write("<h1 style='text-align: center;'>{}</h1>".format("EnneadTab Console"))
            report_file.write("<div style='text-align: center;'>")
            report_file.write("<img src='file://{}/logo_ennead-e_outline white.png' height='120'>".format(ENVIRONMENT.IMAGE_FOLDER))
            report_file.write("</div>")
            report_file.write("<p style='text-align: center;' class='foot_note'>{}</p>".format(TIME.get_formatted_current_time()))

            if Output._out and Output._out[0][1] != "<hr>":
                report_file.write("<hr>") 

            for header_style, content in Output._out:
                if isinstance(content, list):
                    report_file.write("<ul>")
                    for i, item in enumerate(content):
                        report_file.write("<li>{0} : {1}</li>".format(i+1,
                                                                    Output.format_content(item)))                      
                    report_file.write("</ul>")
                else:
                    # Make error detection more flexible
                    error_keywords = ["error", "exception", "failed", "crash"]
                    is_error = any(keyword in str(content).lower() for keyword in error_keywords)
                    
                    if is_error:
                        report_file.write("<div class='error-card'>{}<button class='copy-btn' onclick='copyErrorCard(this)'>Copy</button></div>".format(
                            Output.format_content(content)))
                    else:
                        report_file.write("<{0}>{1}</{0}>".format(
                            header_style, Output.format_content(content)))
                    
                
            report_file.write("</body></html>")

    @staticmethod
    def format_content(input):
        """Formats input content for HTML display.

        Args:
            input: Content to be formatted (any type)

        Returns:
            str: HTML-safe formatted string representation of the input
        """
        if "bt_" in str(input):
            return "<button onclick='return sample_func(this)'>{}</button>".format(input.split("bt_")[1])
        
        if os.path.exists(str(input)):
            # Special case image sizes
            if "_large" in str(input):
                return "<img src='file://{}' height='800'>".format(input)
            elif "icon" in str(input):
                return "<img src='file://{}' height='80'>".format(input)
            elif "Click.png" in str(input):
                return "<img src='file://{}' height='30'>".format(input)
            
            # Default case: full width with maintained aspect ratio
            return "<img src='file://{}' style='width: 100%; height: auto;'>".format(input)
            
        return str(input).replace("\n", "<br>")

    def print_md(self, content):
        """Prints content in markdown format.

        Args:
            content: Content to be displayed in markdown format
        """
        print (content)

    def print_html(self, content):
        """Prints raw HTML content.

        Args:
            content: HTML content to be displayed directly
        """
        print (content)

    def _print_html_report(self):
        """Opens the generated HTML report in the default web browser."""
        webbrowser.open("file://{}".format(Output._report_path))

    def insert_divider(self):
        """Inserts a horizontal line divider in the output."""
        if not Output._out or Output._out[-1][0] != "<hr>":
            self.write("<hr>")

    def reset(self):
        """Resets the output system.
        
        Clears the output buffer and removes the existing HTML report file.
        """
        Output._out = []






####################################################
def get_output():
    """Returns the singleton instance of the Output class.

    Returns:
        Output: The single instance of the Output class
    """
    return Output()


def unit_test():
    """Runs a comprehensive test of the output system.
    
    Tests:
        - Basic output functionality
        - Different style outputs
        - Error message formatting
        - List output
        - Divider insertion
        - HTML report generation
    """
    output = get_output()
    output.write("Sample text in 'Title' style",Style.Title)
    output.write("Sample text in 'Subtitle' style",Style.Subtitle)
    output.write("Sample text in default style")
    output.write("sample text in foot note style(this is not working yet)", Style.Footnote)

    output.insert_divider()
    output.write("\n\n")
    output.insert_divider()
    
    output.write("Trying to print list as item list")
    test_list = ["A", "B", "C", 99, 440, 123]
    output.write(test_list)
    output.write("Trying to print list as str")
    output.write(test_list, as_str=True)
    
    output.insert_divider()

    
    output.write("Trying to print a random meme image")
    output.write(IMAGE.get_one_image_path_by_prefix("meme"))


    output.insert_divider()

    output.write("Trying to print an error:\nThis is a fake error msg but ususaly trigger by try-except")

    output.insert_divider()


    output.write("Trying to print a button")
    output.write("bt_sample button")


    output.insert_divider()
    new_output = get_output()
    new_output.write("This is a new output object but should write to same old output window")
    new_output.plot()



def display_output_on_browser():
    """Forces the current output to be displayed in the browser.
    
    Note:
        This is a convenience function that creates an Output instance
        and calls its plot() method.
    """
    if not ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        import NOTIFICATION
        NOTIFICATION.messenger("currently only support Revit Env")
        return
    try:
        from pyrevit import script
        dest_file = FOLDER.get_EA_dump_folder_file("EnneadTab Output.html")
        output = script.get_output()
        output.save_contents(dest_file)
        output.close()
        os.startfile(dest_file)
    except Exception as e:
        return
      
#######################################################
if __name__ == "__main__":
    unit_test()
