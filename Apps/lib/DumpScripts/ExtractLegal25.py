import os
from reportlab.lib.pagesizes import letter  # Changed to US Letter size
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Preformatted, Spacer
from reportlab.lib.units import inch
import textwrap  # Import textwrap for line wrapping

def get_file_content(file_path):
    """Reads the content of a file and returns the lines."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def extract_lines(lines, num_lines=50):
    """Extract the first and last N lines of a file."""
    first_lines = lines[:num_lines]
    last_lines = lines[-num_lines:]
    return first_lines, last_lines

def clean_text(text):
    return text

def wrap_text(text, width=80):
    """Wrap text to fit within the specified width."""
    return "\n".join(textwrap.wrap(text, width=width))

def process_file(file_path, num_lines=50):
    """Process a single file, extract lines, and return content with file headers."""
    lines = get_file_content(file_path)
    first_lines, last_lines = extract_lines(lines, num_lines)
    return first_lines, last_lines

def generate_pdf(content, output_file, title):
    """Generate a PDF with the extracted content, preserving code formatting, indentation, and newlines."""
    doc = SimpleDocTemplate(output_file, pagesize=letter)  # Changed to letter size
    story = []
    styles = getSampleStyleSheet()
    header_style = styles['Heading2']
    preformatted_style = styles['Code']  # Use 'Code' style for preserving indentation and newlines

    for module_name, lines in content:
        # Add module name as header
        story.append(Preformatted(f"{module_name}", header_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Process each line, wrap text to avoid overflow, and preserve formatting
        wrapped_lines = [wrap_text(clean_text(line), width=80) for line in lines]  # Wrap each line to avoid overflow
        code_block = "\n".join(wrapped_lines)
        story.append(Preformatted(code_block, preformatted_style))  # Preformatted preserves both indentation and line breaks
        story.append(Spacer(1, 0.5 * inch))

    doc.build(story)
    print(f"PDF generated: {output_file}")
    # os.startfile(output_file)

def process_enneadtab_chain(repo_path, num_lines=50):
    """Process the files in EnneadTab starting from __init__.py and ENVIRONMENT."""
    module_order = ['__init__.py', 'ENVIRONMENT.py']
    base_folder = repo_path
    
    # Get all other modules in EnneadTab
    all_files = [f for f in os.listdir(base_folder) if f.endswith('.py')]
    other_files = [f for f in all_files if f not in module_order]
    
    # Ensure the order is respected
    module_order += sorted(other_files)

    begin_content = []
    end_content = []
    
    for module in module_order:
        file_path = os.path.join(base_folder, module)
        if not os.path.exists(file_path):  # Skip if the file doesn't exist
            continue
        first_lines, last_lines = process_file(file_path, num_lines)
        
        begin_content.append((module, first_lines))
        end_content.append((module, last_lines))
    
    return begin_content, end_content

def report_enneadtab():
    current_dir = os.getcwd()
    repo_path = os.path.join(current_dir, 'Apps', 'lib',"EnneadTab")  # Updated as per your request
    output_folder = os.path.join(current_dir, 'Apps', 'lib', 'DumpScripts', 'Legal')

    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define output files
    beginning_output_file = os.path.join(output_folder, '[EnneadTab]25 pages of codebase from the beginning of scripts.pdf')
    ending_output_file = os.path.join(output_folder, '[EnneadTab]25 pages of codebase from the ending of scripts.pdf')

    # Extract content
    begin_content, end_content = process_enneadtab_chain(repo_path, num_lines=50)

    # Generate PDFs
    generate_pdf(begin_content, beginning_output_file, title="Beginning Pages of EnneadTab Modules")
    generate_pdf(end_content, ending_output_file, title="Ending Pages of EnneadTab Modules")

def report_acc_opener():
    current_dir = os.getcwd()
    repo_path = os.path.join(current_dir, 'DarkSide', 'exes','source code','AccFileOpenner')  # Updated as per your request
    output_folder = os.path.join(current_dir, 'Apps', 'lib', 'DumpScripts', 'Legal')

    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define output files
    beginning_output_file = os.path.join(output_folder, '[AccFileOpener]25 pages of codebase from the beginning of scripts.pdf')
    ending_output_file = os.path.join(output_folder, '[AccFileOpener]25 pages of codebase from the ending of scripts.pdf')

    # Extract content
    begin_content, end_content = process_enneadtab_chain(repo_path, num_lines=50)

    # Generate PDFs
    generate_pdf(begin_content, beginning_output_file, title="Beginning Pages of EnneadTab Modules")
    generate_pdf(end_content, ending_output_file, title="Ending Pages of EnneadTab Modules")


if __name__ == "__main__":
    report_enneadtab()
    report_acc_opener()