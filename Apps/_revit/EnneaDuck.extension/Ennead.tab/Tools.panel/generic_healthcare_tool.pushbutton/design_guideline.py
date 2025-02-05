import os

note = """
NYU Health as sample

base of design need to have PIM #

need to have "GFA Scheme" and "DGSF Scheme", each need to have a color scheme???
area para name list


parking para name list


during early design, avoid using design option for total massing study. Such as T building VS L building. 
Instead, duplicate the entire model for new scheme.
This might be controversy:
the risk of using design option: 
"""


def show_design_outline(doc):
    print (note)
    
    os.startfile(os.path.join(os.path.dirname(__file__),"Healthcare deliverable.PNG"))


if __name__ == "__main__":
    show_design_outline(None)