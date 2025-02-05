import os


DESIGN_GUIDELINE_PATH = os.path.join(os.path.dirname(__file__), "design_guideline.md")

def show_design_outline(doc):
    # Quack! Let's find those images!
    png_files = [f for f in os.listdir(os.path.dirname(__file__)) 
                 if f.lower().endswith('.png') and f != 'icon.png']
    
    try:
        from pyrevit import script
        output = script.get_output()
        output.print_md(DESIGN_GUIDELINE_PATH)

        for file in png_files:
            output.print_md(os.path.join(os.path.dirname(__file__), file))
    except:
        # Read and print the contents of the MD file instead of just the path
        with open(DESIGN_GUIDELINE_PATH, 'r') as file:
            print(file.read())
        for file in png_files:
            os.startfile(os.path.join(os.path.dirname(__file__), file))



if __name__ == "__main__":
    show_design_outline(None)