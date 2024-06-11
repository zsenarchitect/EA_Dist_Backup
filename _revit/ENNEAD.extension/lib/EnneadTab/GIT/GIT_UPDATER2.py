"""LibGit2Sharp wrapper module for pyRevit.

Documentation:
    https://github.com/libgit2/libgit2sharp/wiki
"""

import os.path as op
from collections import OrderedDict

try:
    import clr # pyright: ignore
    import DateTime # pyright: ignore
    import DateTimeOffset # pyright: ignore
except:
    pass

import ENVIRONMENT_CONSTANTS
import USER_CONSTANTS

GIT_LIB = 'LibGit2Sharp'

LIBGIT_DLL = "{}\\{}.dll".format(ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER, GIT_LIB)
safe_strtype = lambda x: unicode(x)
try:
        
    clr.AddReferenceToFileAndPath(LIBGIT_DLL)

    import LibGit2Sharp as libgit   

except:
    pass

class EnneadTabGitAuthenticationError(Exception):
    """Git authentication error."""
    pass


class RepoInfo(object):
    """Repo wrapper for passing around repository information.

    Attributes:
        directory (str): repo directory
        name (str): repo name
        head_name (str): head branch name
        last_commit_hash (str): hash of head commit
        repo (str): ``LibGit2Sharp.Repository`` object
        branch (str): current branch name
        username (str): credentials - username
        password (str): credentials - password
    """
    def __init__(self, repo):
        self.directory = repo.Info.WorkingDirectory
        self.name = op.basename(op.normpath(self.directory))
        self.head_name = repo.Head.FriendlyName
        self.last_commit_hash = repo.Head.Tip.Id.Sha
        self.repo = repo
        self.branch = repo.Head.FriendlyName
        self.username = self.password = None

    def __repr__(self):
        return '<type \'RepoInfo\' head \'{}\' @ {}>'\
            .format(self.last_commit_hash, self.directory)


def _credentials_hndlr(username, password):
    userpass = libgit.UsernamePasswordCredentials()
    userpass.Username = username
    userpass.Password = password
    return userpass


def _get_credentials_hndlr(username, password):
    return libgit.Handlers. \
           CredentialsHandler(lambda url, uname, types:
                              _credentials_hndlr(username, password))


def _make_pull_options(repo_info):
    
    pull_ops = libgit.PullOptions()
    pull_ops.FetchOptions = libgit.FetchOptions()
    if repo_info.username and repo_info.password:
        

        pull_ops.FetchOptions.CredentialsProvider = \
            _get_credentials_hndlr(repo_info.username, repo_info.password)

    return pull_ops


def _make_fetch_options(repo_info):
    
    fetch_ops = libgit.FetchOptions()
    if repo_info.username and repo_info.password:
        

        fetch_ops.CredentialsProvider = \
            _get_credentials_hndlr(repo_info.username, repo_info.password)

    return fetch_ops


def _make_clone_options(username=None, password=None):
    
    clone_ops = libgit.CloneOptions()
    if username and password:
        
        clone_ops.CredentialsProvider = \
            _get_credentials_hndlr(username, password)

    return clone_ops


def _make_pull_signature():
    
    return libgit.Signature(USER_CONSTANTS.USER_NAME,
                            USER_CONSTANTS.USER_NAME,
                            DateTimeOffset(DateTime.Now))


def _process_git_error(exception_err):
    raise EnneadTabGitAuthenticationError(exception_err)
   

def get_repo(repo_dir):
    """Return repo object for given git repo directory.

    Args:
        repo_dir (str): full path of git repo directory

    Returns:
        (RepoInfo): repo object
    """
    repo = libgit.Repository(repo_dir)
    return RepoInfo(repo)


def git_pull(repo_info):
    """Pull the current head of given repo.

    Args:
        repo_info (RepoInfo): target repo object

    Returns:
        (RepoInfo): repo object with updated head
    """
    repo = repo_info.repo
    try:
        libgit.Commands.Pull(repo,
                             _make_pull_signature(),
                             _make_pull_options(repo_info))

       
        head_msg = safe_strtype(repo.Head.Tip.Message).replace('\n', '')

      
        return RepoInfo(repo)

    except Exception as pull_err:
       
        _process_git_error(pull_err)


def git_fetch(repo_info):
    """Fetch current branch of given repo.

    Args:
        repo_info (RepoInfo): target repo object

    Returns:
        (RepoInfo): repo object with updated head
    """
    repo = repo_info.repo
    try:
        libgit.Commands.Fetch(repo,
                              repo.Head.TrackedBranch.RemoteName,
                              [],
                              _make_fetch_options(repo_info),
                              'fetching pyrevit updates')

      
        head_msg = safe_strtype(repo.Head.Tip.Message).replace('\n', '')

       
        return RepoInfo(repo)

    except Exception as fetch_err:
      
        _process_git_error(fetch_err)


def git_clone(repo_url, clone_dir, username=None, password=None):
    """Clone git repository to given location.

    Args:
        repo_url (str): repo .git url
        clone_dir (str): destination path
        username (str): credentials - username
        password (str): credentials - password
    """
    try:
        libgit.Repository.Clone(repo_url,
                                clone_dir,
                                _make_clone_options(username=username,
                                                    password=password))

    

    except Exception as clone_err:
   
        _process_git_error(clone_err)


def compare_branch_heads(repo_info):
    """Compare local and remote branch heads and return ???

    Args:
        repo_info (RepoInfo): target repo object
    """
    # FIXME: need return type. possibly simplify
    repo = repo_info.repo
    repo_branches = repo.Branches

    

    for branch in repo_branches:
        if branch.FriendlyName == repo_info.branch and not branch.IsRemote:
            try:
                if branch.TrackedBranch:
                    

                    hist_div = repo.ObjectDatabase. \
                        CalculateHistoryDivergence(branch.Tip,
                                                   branch.TrackedBranch.Tip)
                    return hist_div
            except Exception as compare_err:
                print (compare_err)
        else:
            pass



def get_all_new_commits(repo_info):
    """Fetch and return new commits ahead of current head.

    Args:
        repo_info (RepoInfo): target repo object

    Returns:
        (OrderedDict[str, str]): ordered dict of commit hash:message
    """
    repo = repo_info.repo
    current_commit = repo_info.last_commit_hash

    ref_commit = repo.Lookup(libgit.ObjectId(current_commit),
                             libgit.ObjectType.Commit)

    # Let's only consider the refs that lead to this commit...
    refs = repo.Refs.ReachableFrom([ref_commit])

    # ...and create a filter that will retrieve all the commits...
    commit_filter = libgit.CommitFilter()
    commit_filter.IncludeReachableFrom = refs
    commit_filter.ExcludeReachableFrom = ref_commit
    commit_filter.SortBy = libgit.CommitSortStrategies.Time

    commits = repo.Commits.QueryBy(commit_filter)
    commitsdict = OrderedDict()
    for commit in commits:
        if commit in repo.Head.Commits \
                or commit in repo.Head.TrackedBranch.Commits:
            commitsdict[commit.Id.ToString()] = commit.MessageShort

    return commitsdict
