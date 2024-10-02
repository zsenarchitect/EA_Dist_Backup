"""
The main purpose of this moudle to is to handle Rhino 8 situation. 
Native shutil.copyfile will fail in some cases, so we use dotnet to copy the file.

"""
try:
    import shutil
except:
    from System.IO import File  # pyright: ignore



def copyfile(src, dst):
    try:
        # Attempt to copy the file using shutil.copyfile
        shutil.copyfile(src, dst)
    except Exception as e:
        copyfile_with_dotnet(src, dst)

def copyfile_with_dotnet(src, dst):
    try:
        File.Copy(src, dst, True)  # True to overwrite if exists
        return True
    except Exception as e:
        return False


if __name__ == "__main__":
    copyfile()
