input_list = [("Number_1", "Number", "Number to add"),
              ("Number_2", "Number", "Number to base")]
output_list = [("Result", "Number", "Result num of the script")]

basic_doc = """this is a sample doc for EnneadTab For Grasshopper.
This component will add the two input number together,
happy Monday"""

########################################### internal setup
import _utility
__doc__ = _utility.generate_doc_string(basic_doc, input_list, output_list)
# default_value_map = _utility.generate_default_value_map()

# print dir(_utility)
# use this to trick GH that all varibale is defined.
globals().update(_utility.validate_input_list(globals(), input_list))


################ input below ###########################

my_num = Number_1
adder = Number_2
import scriptcontext as sc
sc.doc = Rhino.RhinoDoc.ActiveDoc
############## main design below #######################


def add(my_num, adder):

    print ("{} + {} = {}".format(my_num, adder, adder + my_num))
    return adder+my_num

result = add(my_num, adder)


import Rhino # pyright: ignore
print ("the active doc is {}".format(Rhino.RhinoDoc.ActiveDoc))
print ("the layers are as below:")
for layer in Rhino.RhinoDoc.ActiveDoc.Layers:
    print(layer)
# when running in GH this is not the namescape
# if __name__ == "__main__":


################ output below ######################
Result = result


sc.doc = ghdoc