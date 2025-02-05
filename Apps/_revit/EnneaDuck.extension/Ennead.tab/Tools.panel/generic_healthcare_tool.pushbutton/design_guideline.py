import os

note = """
NYU Health as sample

base of design need to have PIM #

need to have 
"GFA Scheme"[Area Scheme]: Tracing of outline on each level, single area per level.
"DGSF Scheme"[Room Based]: Use room for area. Use rooom seperation line as bounding element in SD stage, and wall as bounding element in DD stage


area para name list


room para name list


parking para name list


essential family list:
    - elevator
    - elevator door
    - parking stall
    - patient bed room planner


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