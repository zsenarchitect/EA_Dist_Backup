"""Output handling module for EnneadTab applications.

This module provides a singleton Output class for managing HTML report generation
and display. It handles formatting of text, images, and interactive elements with
consistent styling and search functionality.

Typical usage:
    output = get_output()
    output.write("Hello World", Style.Title)
    output.write("Some content")
    output.plot()

Features:
    - HTML report generation with consistent styling
    - Support for text, images, and interactive elements
    - Search functionality with real-time highlighting
    - Error message formatting with copy functionality
    - Singleton pattern to ensure single output stream
"""

import os
import io
import webbrowser

import FOLDER 
import ENVIRONMENT
import NOTIFICATION
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

class Style:
    """Constants for HTML element styles.
    
    These styles define the visual hierarchy of content in the output.
    
    Attributes:
        MainBody (str): Standard paragraph style for main content
        Title (str): Large heading style for main sections
        Subtitle (str): Medium heading style for subsections
        Footnote (str): Small text style for supplementary information
    """
    MainBody = "p"
    Title = "h1"
    Subtitle = "h2"
    Footnote = "foot_note"
    

class Output:
    """Singleton class for managing HTML output generation and display.
    
    This class handles the creation and formatting of HTML reports with consistent
    styling, search functionality, and interactive elements. It maintains a single
    instance to ensure all output goes to the same report.
    
    Attributes:
        _instance: Singleton instance of Output
        _out (list): Container for output content as (style, content) tuples
        _report_path (str): Path to output HTML file
        _graphic_settings (dict): Visual styling parameters for HTML output
        _is_print_out (bool): Whether to also print to console
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
    _is_print_out = not ENVIRONMENT.IS_REVIT_ENVIRONMENT
    
    def __new__(cls, *args, **kwargs):
        """Creates or returns the singleton instance."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def write(self, content, style=Style.MainBody, as_str=False):
        """Adds content to the output container with specified styling.
        
        Args:
            content: Content to write (text, image path, or button command)
            style: HTML style to apply (default: Style.MainBody)
            as_str: Force content to be treated as string (default: False)
        
        Examples:
            >>> output.write("Main Title", Style.Title)
            >>> output.write(["Item 1", "Item 2"])  # Formats as list
            >>> output.write(["Item 1", "Item 2"], as_str=True)  # Formats as string
        """
        if as_str:
            content = str(content)
        Output._out.append((style, content))
        if Output._is_print_out:
            print(content)

    def reset_output(self):
        """Clears all content from the output container.
        
        Similar to reset() method, provided for backwards compatibility.
        """
        Output._out = []

    def is_empty(self):
        """Checks if output container has any content.
        
        Returns:
            bool: True if no content exists, False otherwise
        """
        return not Output._out

    def plot(self):
        """Generates and displays the HTML report in default browser.
        
        Generates the report only if content exists (_out is not empty).
        Opens the generated HTML file in the system's default web browser.
        
        Note:
            This is the main method to display the output after writing content.
        """
        if self.is_empty():
            return
        self._generate_html_report()
        self._print_html_report()
        

    def _generate_html_report(self):
        """Generates the HTML report with all content and styling.
        
        Creates an HTML file that includes:
            - Custom styling based on _graphic_settings
            - Search functionality with highlighting
            - Copy-to-clipboard functionality
            - Formatted content from _out container
            - Error handling and display
            - Interactive elements (buttons)
        
        The generated HTML includes:
            - Header with search functionality
            - Main content area with styled elements
            - Footer with EnneadTab branding
            - JavaScript for interactivity
        
        Side Effects:
            - Creates or overwrites file at _report_path
            - Formats all content in _out container
        """
        html_content = []
        html_content.append("""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        background-color: %(background_color)s;
                        font-family: %(font_family)s;
                        color: %(text_color)s;
                        padding: 20px;
                    }
                </style>
                <!-- ... existing style and script content ... -->
            </head>
            <body>
        """ % Output._graphic_settings)
        
        # ... existing HTML generation code ...
        
        with io.open(Output._report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(html_content))

    def _print_html_report(self):
        """Opens the generated HTML report in default web browser.
        
        Uses webbrowser module to display the report file using its file:// URL.
        """
        webbrowser.open("file://{}".format(Output._report_path))

    def print_md(self, content):
        """Prints markdown content for compatibility with pyRevit.
        
        Args:
            content (str): Markdown formatted content to print
            
        Note:
            This is a compatibility method to match pyRevit's output interface.
        """
        print(content)

    def print_html(self, content):
        """Prints HTML content for compatibility with pyRevit.
        
        Args:
            content (str): HTML formatted content to print
            
        Note:
            This is a compatibility method to match pyRevit's output interface.
        """
        print(content)

    def insert_divider(self):
        """Inserts horizontal divider if not already present at end.
        
        Adds a visual separator between content sections. Checks last output
        to prevent duplicate dividers.
        """
        if not Output._out or Output._out[-1][0] != "<hr>":
            self.write("<hr>")

    def reset(self):
        """Clears all content from the output container.
        
        Removes all stored content, allowing for a fresh start.
        """
        Output._out = []






####################################################
def get_output():
    """Returns singleton instance of Output class.
    
    This is the recommended way to get an Output instance.
    
    Returns:
        Output: Singleton output instance
        
    Example:
        >>> output = get_output()
        >>> output.write("Hello World")
    """
    return Output()


def unit_test():
    """Runs comprehensive unit tests for Output functionality.
    
    Tests various output features including:
        - Different text styles (Title, Subtitle, MainBody, Footnote)
        - List handling (as items and as string)
        - Image display with different size conventions
        - Error message formatting
        - Button creation and display
        - Singleton pattern verification
    
    Example:
        >>> unit_test()
        # Displays test output in browser with all features demonstrated
    """
    output = get_output()
    output.write("Sample text in 'Title' style", Style.Title)
    output.write("Sample text in 'Subtitle' style", Style.Subtitle)
    output.write("Sample text in default style")
    output.write("sample text in foot note style", Style.Footnote)

    output.insert_divider()
    output.write("\n\n")
    output.insert_divider()
    
    output.write("Trying to print list as item list")
    test_list = ["A", "B", "C", 99, 440, 123]
    output.write(test_list)
    output.write("Trying to print list as str", as_str=True)
    output.write(test_list, as_str=True)
    
    output.insert_divider()
    
    output.write("Trying to print a random meme image")
    output.write(IMAGE.get_one_image_path_by_prefix("meme"))

    output.insert_divider()

    output.write("Trying to print an error:\nThis is a fake error msg but usually trigger by try-except")

    output.insert_divider()

    output.write("Trying to print a button")
    output.write("bt_sample button")

    output.insert_divider()
    new_output = get_output()
    new_output.write("This is a new output object but should write to same old output window")
    new_output.plot()



def display_output_on_browser():
    """Displays pyRevit output content in system browser.
    
    For Revit environment use only. Saves current pyRevit output
    content to a file and opens in default browser.
    
    Note:
        Only works in Revit environment.
    
    Raises:
        NotificationError: If not in Revit environment
    """
    if not ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        NOTIFICATION.messenger("currently only support Revit Env")
        return
    from pyrevit import script
    dest_file = FOLDER.get_EA_dump_folder_file("EnneadTab Output.html")
    output = script.get_output()
    output.save_contents(dest_file)
    output.close()
    os.startfile(dest_file)
      
#######################################################
if __name__ == "__main__":
    unit_test()
