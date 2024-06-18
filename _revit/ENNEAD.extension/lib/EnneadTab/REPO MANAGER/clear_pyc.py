

if __name__ == "__main__":
    try:
        import os
        print (__file__)
        parent_folder = os.path.dirname(os.path.dirname(__file__))
        print (parent_folder)
        
        
        import traceback
        # import sys
        # sys.path.append(parent_folder)
        # print (sys.path)
        
        # search all the files in the parent folder and print file name full path with .pyc extension
        for root, dirs, files in os.walk(parent_folder):
            print ("\n\nroot folder = {}".format(root))
            for file in files:
                if file.endswith(".pyc"):
                    print (os.path.join(root, file))
                    os.remove(os.path.join(root, file))
        
    except:
        pass
        print (traceback.format_exc())