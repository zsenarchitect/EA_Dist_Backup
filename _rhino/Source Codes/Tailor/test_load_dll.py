# from ctypes import cdll

# # Give the location of the DLL
# mydll = cdll.LoadLibrary("X:\\CXu\\2311_ACCS\\PythonImportTester\\PythonImportTester.dll")

# # Print the type of mydll
# print(type(mydll))

# # Enumerate and print the callable functions in the DLL
# for i, x in enumerate(dir(mydll)):
#     attr = getattr(mydll, x)
#     if callable(attr):
#         print("{}: {} is a function".format(i, x))

# # Call the SumTwoInt function
# result1 = mydll.SumTwoInt(10, 1)

# # Print the result as a string
# print("Addition value:", str(result1))

"""test ground to connect C# with python

dicovery so far: calling imported dll func will actaully be slower than calling sim python func. I think the repating call make it a problem in the interpureter
to make the best of dll, better to make the function directly so only call once in python namespace.
"""
import time
import sys
import clr # pyright: ignore
dll_folder = "X:\\CXu\\2311_ACCS\\PythonImportTester"

import os
for file in os.listdir(dll_folder):
  if file.endswith(".rhp"):
    dll_file = os.path.join(dll_folder, file).replace(".rhp", ".dll")
    try:
      os.remove(dll_file)
    except:
      pass

    # make a copy of rhp file to dll file
    rhp_file = os.path.join(dll_folder, file)
    os.system("copy {} {}".format(rhp_file, dll_file))

sys.path.append(dll_folder)
clr.AddReference("PythonImportTester")

import PythonImportTester
import rhinoscriptsyntax as rs
def test_load_dll():
  rs.ClearCommandHistory()
  for max in [10, 20, 30, 50, 100]:
    tester(max)
    print ("\n\n\n")
  rs.CommandHistory()
  
def tester(max):
  
  print ("calc sum of 1, 2, 3.....{}".format(max))
  t = time.time()
  python_sum = python_method(max)
  python_time = time.time() - t
  print ("python method time:", python_time)
  print ("python_sum:", python_sum)

  
  t = time.time() 
  dll_sum = dll_method(max)
  dll_time = time.time() - t
  print ("dll method time:", dll_time)
  print ("dll_sum:", dll_sum)
  

  print ("time difference: python - dll:", python_time - dll_time)
  print ("is result same?", dll_sum == python_sum)
  

    
def dll_method(max):
  print ("dll method:")
  return PythonImportTester.PythonImportTester.CalcFibonacci(max)



  # print (PythonImportTester.PythonImportTester.SumTwoInt(10, 1))
  sum = 0
  for x in range(max):
    sum = PythonImportTester.PythonImportTester.SumTwoInt(sum, x)
    
  return sum


def python_method(max):
  print ("python method:")
  map = {}
  def f_action(x):
      if x in map:
        return map[x]
      if x == 0:
        return 0
      elif x == 1:
        return 1
      else:
        map[x] = f_action(x-1) + f_action(x-2)
        return map[x]

  
  return f_action(max)


  # sum = 0
  # for x in range(max):
  #   sum = int(sum + x)
  # return sum

######################  main code below   #########
if __name__ == "__main__":

    test_load_dll()




