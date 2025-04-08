import os


DESIGN_GUIDELINE_PATH = os.path.join(os.path.dirname(__file__), "design_guideline.md")

def show_design_outline(doc):
    with open(DESIGN_GUIDELINE_PATH, 'r') as file:
        content = file.read()
    # Quack! Let's find those images!

    png_files = [f for f in os.listdir(os.path.dirname(__file__)) 
                 if f.lower().endswith('.png') and f != 'icon.png']
    
 
    from pyrevit import script
    output = script.get_output()
    output.print_md(content)



    for file in png_files:
        output.print_image(os.path.join(os.path.dirname(__file__), file))




if __name__ == "__main__":
    show_design_outline(None)