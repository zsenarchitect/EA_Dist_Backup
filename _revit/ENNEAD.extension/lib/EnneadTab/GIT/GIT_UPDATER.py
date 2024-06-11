#! python3

# need to prepare pygit2 with default cpyhthon engine
# the good thing about pygit2 is that it does not require git installed on user computer

#try cpyhton first, if not working then make it exe. this time, transfer data by using Envirn Variable instead of temp json


try:
    import pygit2
except:
    pass

class GitRepoManager:
    def __init__(self, repo_url, local_path, username, access_token):
        self.repo_url = repo_url
        self.local_path = local_path
        self.username = username
        self.access_token = access_token

    def credentials_callback(self, url, username_from_url, allowed_types):
        return pygit2.UserPass(self.username, self.access_token)

    def clone_repository(self):
        print("Cloning repository...")
        remote_callbacks = pygit2.RemoteCallbacks(credentials=self.credentials_callback)
        self.repo = pygit2.clone_repository(self.repo_url, self.local_path, callbacks=remote_callbacks)
        print("Repository cloned successfully.")

    def pull_updates(self):
        print("Pulling updates from repository...")
        remote_callbacks = pygit2.RemoteCallbacks(credentials=self.credentials_callback)
        remote = self.repo.remotes["origin"]
        remote.fetch(callbacks=remote_callbacks)
        remote_master_id = self.repo.lookup_reference("refs/remotes/origin/master").target
        merge_result, _ = self.repo.merge_analysis(remote_master_id)
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            print("Already up to date.")
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            self.repo.checkout_tree(self.repo.get(remote_master_id))
            master_ref = self.repo.lookup_reference("refs/heads/master")
            master_ref.set_target(remote_master_id)
            self.repo.head.set_target(remote_master_id)
            print("Fast-forward merge completed.")
        else:
            print("Complex merge required, manual intervention needed.")


def sample():
    # Example usage
    repo_url = 'https://github.com/your-username/your-repo.git'
    local_path = 'path/to/your/local/repo'
    username = 'your_username'
    access_token = 'your_access_token'

    git_ops = GitRepoManager(repo_url, local_path, username, access_token)

    # To clone the repository
    git_ops.clone_repository()

    # To pull updates
    # git_ops.pull_updates()  # Uncomment this line to pull updates