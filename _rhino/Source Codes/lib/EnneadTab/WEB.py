

import os
import zipfile

import FOLDER
try:
    import System # pyright: ignore
except:
    pass



def download_file_by_name(url, target_folder, file_name):
    """Download a file to a directory.

    This function has been copied from ladybug_rhino.download.

    Args:
        url: A string to a valid URL.
        target_folder: Target folder for download (e.g. c:/ladybug)
        file_name: File name (e.g. testPts.zip).
    """
    # create the target file path.
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    file_path = os.path.join(target_folder, file_name)

    # set the security protocol to the most recent version
    try:
        # TLS 1.2 is needed to download over https
        if System:
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
        else:
            raise ImportError("System module is not available.")
    except AttributeError:
        # TLS 1.2 is not provided by MacOS .NET in Rhino 5
        if url.lower().startswith('https'):
            print('This system lacks the necessary security libraries to download over https.')

    # attempt to download the file
    print("Downloading {} to {}".format(url, file_path))
    client = System.Net.WebClient()
    try:
        client.DownloadFile(url, file_path)
    except Exception as e:
        raise Exception('Download failed with the error:\n{}'.format(e))
    return file_path
    
def get_request(url):
    client = System.Net.WebClient()
    try:
        response = client.DownloadString(url)
        return response
    except Exception as e:
        return str(e)
    finally:
        client.Dispose()


def post_request(url, data):
    client = System.Net.WebClient()
    data_collection = System.Collections.Specialized.NameValueCollection()
    
    for key, value in data.items():
        data_collection.Add(key, value)

    try:
        response_bytes = client.UploadValues(url, "POST", data_collection)
        response = System.Text.Encoding.UTF8.GetString(response_bytes)
        return response
    except Exception as e:
        return str(e)
    finally:
        client.Dispose()





def unzip_file(source_file, dest_dir=None):
    """Unzip a compressed file.

    This function has been copied from ladybug.futil.

    Args:
        source_file: Full path to a valid compressed file (e.g. c:/ladybug/testPts.zip)
        dest_dir: Target folder to extract to (e.g. c:/ladybug).
            Default is set to the same directory as the source file.
    """
    # set default dest_dir and create it if need be.
    if dest_dir is None:
        dest_dir, fname = os.path.split(source_file)
    # extract files to destination
    with zipfile.ZipFile(source_file) as zf:
        for member in zf.infolist():
            words = member.filename.split('\\')
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                dest_dir = os.path.join(dest_dir, word)
            zf.extract(member, dest_dir)

def remove_zip_file(zip_file):
    """Try to remove a zip file."""
    try:
        os.remove(zip_file)
    except:
        print('Failed to remove downloaded zip file: {}.'.format(zip_file))


def download_repo_github(repo_url, target_directory):
    """Download a repo of a particular version from from github.

    Args:
        repo: The name of a repo to be downloaded (eg. 'lbt-grasshopper').
        [example]repo_url = "https://github.com/ladybug-tools/{}/archive/master.zip".format(repo)
        target_directory: the directory where the library should be downloaded to.
        version: The version of the repository to download. If None, the most
            recent version will be downloaded. (Default: None)
        """
    # download files
    repo_name = repo_url.split('/')[-1].split(".zip")[0]
    zip_file = os.path.join(target_directory, '%s.zip' % repo_name)
    print ('Downloading "{}"  github repository to: {} as {}'.format(repo_name, target_directory, zip_file))
    download_file_by_name(repo_url, target_directory, zip_file)

    #unzip the file
    unzip_file(zip_file, target_directory)

    # try to clean up the downloaded zip file
    try:
        os.remove(zip_file)
    except:
        print ('Failed to remove downloaded zip file: {}.'.format(zip_file))

    # return the directory where the unzipped files live
    return os.path.join(target_directory, '{}-master'.format(repo_name))
  
  
  
def unit_test():
    client = System.Net.WebClient()
    for i,x in enumerate(dir(client)):
        print ("{}:{}".format(i,x))
    
    print ("\n\n\n#############################")    
    url = "https://example.com"
    print(get_request(url))


    print ("\n\n\n#############################")
    url = "https://example.com"
    data = {'key1': 'value1', 'key2': 'value2'}
    print(post_request(url, data))
    
    print ("\n\n\n#############################")
    url = "https://via.placeholder.com/300/09f/fff.png"
    download_file_by_name(url, "{}\\Unit Test".format(FOLDER.get_download_folder()), "test.png")
    return


    rhino_repo_url = "https://github.com/zsenarchitect/EnneadTab-for-Rhino-master.zip"
    rhino_repo_url = "https://github.com/zsenarchitect/EnneadTab-for-Rhino/archive/master.zip"
    # https://github.com/github/codeql/archive/refs/heads/main.tar.gz
    # https://github.com/ladybug-tools/ladybug.git
    rhino_repo_url = "https://github.com/ladybug-tools/{}/archive/master.zip".format("ladybug")
    rhino_repo_url = "https://github.com/zsenarchitect/dice-rollerarchive/main.zip"
    print (download_repo_github(rhino_repo_url, "C:\\Users\\sen.zhang\\temp"))
  
  
###############################
if __name__ == "__main__":
    unit_test()