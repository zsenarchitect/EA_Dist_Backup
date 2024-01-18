import subprocess
import os

def create_git_archive(repo_path, output_path, branch="HEAD"):
    # Change directory to the repo_path
    os.chdir(repo_path)

    # Build the git archive command
    command = "git archive --format zip --output \"{0}\" {1}".format(output_path, branch)

    try:
        # Execute the command
        subprocess.check_call(command, shell=True)
        print ("Archive created successfully at {0}".format(output_path))
    except subprocess.CalledProcessError as e:
        print ("An error occurred: {0}".format(e))
    
    
def main():
    repo_path = r"C:\Users\sen.zhang\github\EnneadTab-for-Rhino"
    output_path = "https://github.com/zsenarchitect/EnneadTab-for-Rhino/archive/main.zip"  # Replace with your desired output path
    create_git_archive(repo_path, output_path)


if __name__ == "__main__":
    main()