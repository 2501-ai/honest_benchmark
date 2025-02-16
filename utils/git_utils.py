import subprocess
import git

def get_git_branch():
    """Get the current git branch name."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return 'unknown'

def get_git_hash():
    """Get the current git commit hash."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return 'unknown'

def get_local_changes():
    """
    Get the number of tracked files with uncommitted changes in the git repository.
    Returns:
        int: Number of modified tracked files
        None: If unable to determine the state
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        # Count modified tracked files (excluding untracked files)
        return len(repo.index.diff(None))
    except Exception:
        # Return None if we can't determine the state
        return None
