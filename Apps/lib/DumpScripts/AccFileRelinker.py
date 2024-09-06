import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import winsound

# ExtendScript template for relinking files in InDesign
extendscript = """
try {{
    var newFilePath = "{new_file}";
    var newFile = File(newFilePath);
    if (!newFile.exists) {{
        $.writeln("New file not found: " + newFilePath);
        exit();
    }}
    
    var doc = app.open(File("{indesign_path}"));
    
    // Iterate over all the links in the document
    for (var i = 0; i < doc.links.length; i++) {{
        var link = doc.links[i];
        if (link.filePath.indexOf("{old_file}") == -1) {{
            link.relink(newFile);
            link.update();
            $.writeln("Relinked: " + link.filePath + " -> " + newFilePath);
        }}
    }}
    
    doc.save();
    doc.close();
}} catch (e) {{
    alert("Error creating document: " + e.message);
}}
"""

# Function to create ExtendScript from the template
def create_extendscript(indesign_path, old_file, new_file, jsx_path):
    script = extendscript.format(
        indesign_path=indesign_path.replace("\\", "/"),
        old_file=old_file.replace("\\", "/"),
        new_file=new_file.replace("\\", "/")
    )
    
    # Save the script to the specified path
    with open(jsx_path, "w") as f:
        f.write(script)

# Function to get the desktop path
def get_desktop_path():
    return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

# Function to run ExtendScript from Python on Windows using VBScript
def run_extendscript(script_path, close_indesign, version):
    desktop_path = get_desktop_path()
    if close_indesign:
        close_indesign_line = "app.quit()"
    else:
        close_indesign_line = ""
    # Ensure that the script path is properly escaped and wrapped in double quotes
    vbs_content = """Set app = CreateObject("InDesign.Application.{version}")
app.DoScript "{script_path}", 1246973031
{close_indesign_line}""".format(version=version, script_path=script_path.replace("\\", "/"), close_indesign_line=close_indesign_line)

    # Create the path for the VBS script
    vbs_path = os.path.join(desktop_path, "run_script.vbs")
    
    # Write the VBS script to the desktop
    with open(vbs_path, "w") as f:
        f.write(vbs_content)
    
    # Use subprocess to call the VBScript
    subprocess.call(["wscript", vbs_path])


# Function to process a single InDesign file with relinking
def process_indesign(indesign_path, old_file, new_file, version, close_indesign=False):

    # Define where to save the JSX file
    jsx_path = os.path.join(get_desktop_path(), "relink_files.jsx")
    
    # Generate the ExtendScript
    create_extendscript(indesign_path, old_file, new_file, jsx_path)
    
    # Run the ExtendScript in InDesign
    run_extendscript(jsx_path, close_indesign, version)

# GUI for file selection and relinking
def select_files(version_entry):
    # Ask the user for the InDesign file
    indd_file = filedialog.askopenfilename(title="Select the InDesign file", filetypes=[("InDesign Files", "*.indd")])
    if not indd_file:
        messagebox.showerror("Error", "You must select an InDesign file.")
        return
    
    # Ask for the original (A.jpg) and new (B.jpg) files
    old_file = filedialog.askopenfilename(title="Select the original file (A.jpg)", filetypes=[("Image Files", "*.jpg;*.jpeg")])
    if not old_file:
        messagebox.showerror("Error", "You must select the original file.")
        return

    new_file = filedialog.askopenfilename(title="Select the new file (B.jpg)", filetypes=[("Image Files", "*.jpg;*.jpeg")])
    if not new_file:
        messagebox.showerror("Error", "You must select the new file.")
        return
    
    # Get the InDesign version from the entry field
    version = version_entry.get()

    # Process the relinking
    process_indesign(indd_file, old_file, new_file, version, close_indesign=True)
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
    messagebox.showinfo("Success", "Relinking completed and the InDesign document was saved.")

# Main function for the GUI
def main():
    # Create the main window
    root = tk.Tk()
    root.title("InDesign Relinker")

    # Add a label with instructions
    lbl_instruction = tk.Label(root, text="Select the InDesign file and the image files to relink")
    lbl_instruction.pack(pady=10)

    # Add a label and entry for InDesign version
    lbl_version = tk.Label(root, text="Your InDesign version")
    lbl_version.pack()
    version_entry = tk.Entry(root, justify='center')
    version_entry.insert(0, "2024")
    version_entry.pack(pady=5)

    # Add a button to select the files
    btn_select_files = tk.Button(root, text="Select Files and Start Relinking", command=lambda: select_files(version_entry))
    btn_select_files.pack(pady=20)

    # Run the GUI loop
    root.mainloop()

if __name__ == "__main__":
    main()
