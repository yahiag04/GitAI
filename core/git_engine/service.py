from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from git import Repo, InvalidGitRepositoryError


@dataclass
class GitEngine:
    working_directory: Path
    _repo: Optional[Repo] = field(default=None, repr=False)

    def _get_repo(self) -> Repo:
        """Get or initialize the Git repository."""
        if self._repo is None:
            try:
                self._repo = Repo(self.working_directory)
            except InvalidGitRepositoryError:
                raise ValueError(
                    f"No Git repository found at {self.working_directory}. "
                    "Use init_repo() first."
                )
        return self._repo

    def init_repo(self, project_path: Path | None = None) -> str:
        """Initialize a local Git repository."""
        target_path = project_path or self.working_directory
        target_path.mkdir(parents=True, exist_ok=True)

        try:
            Repo(target_path)
            return f"Repository already exists at {target_path}"
        except InvalidGitRepositoryError:
            self._repo = Repo.init(target_path)
            self.working_directory = target_path
            return f"Initialized empty Git repository at {target_path}"

    def commit_changes(self, message: str | None = None) -> str:
        """Stage all changes and commit."""
        repo = self._get_repo()

        # Stage all changes (tracked and untracked)
        repo.git.add(A=True)

        # Check if there are changes to commit
        if not repo.is_dirty(untracked_files=True) and not repo.index.diff("HEAD"):
            return "Nothing to commit, working tree clean."

        # Generate default message if not provided
        if message is None:
            message = "Update files"

        # Commit the staged changes
        commit = repo.index.commit(message)
        return f"Committed: {commit.hexsha[:7]} - {message}"

    def push_changes(self, remote_name: str = "origin") -> str:
        """Push the current branch to remote."""
        repo = self._get_repo()

        if remote_name not in [r.name for r in repo.remotes]:
            return f"No remote named '{remote_name}' configured."

        remote = repo.remote(remote_name)
        current_branch = repo.active_branch.name

        # Push to remote
        push_info = remote.push(current_branch)

        if push_info:
            return f"Pushed {current_branch} to {remote_name}."
        return f"Push completed for {current_branch}."

    def create_branch(self, branch_name: str) -> str:
        """Create a new branch and switch to it."""
        repo = self._get_repo()

        # Check if branch already exists
        if branch_name in [b.name for b in repo.branches]:
            return f"Branch '{branch_name}' already exists."

        # Create and checkout the new branch
        repo.create_head(branch_name)
        repo.heads[branch_name].checkout()
        return f"Created and switched to branch '{branch_name}'."

    def checkout_branch(self, branch_name: str) -> str:
        """Switch to an existing branch."""
        repo = self._get_repo()

        if branch_name not in [b.name for b in repo.branches]:
            return f"Branch '{branch_name}' does not exist."

        repo.heads[branch_name].checkout()
        return f"Switched to branch '{branch_name}'."

    def delete_branch(self, branch_name: str) -> str:
        """Delete a local branch."""
        repo = self._get_repo()

        if branch_name not in [b.name for b in repo.branches]:
            return f"Branch '{branch_name}' does not exist."

        # Cannot delete the current branch
        if repo.active_branch.name == branch_name:
            return f"Cannot delete the currently checked out branch '{branch_name}'."

        repo.delete_head(branch_name, force=True)
        return f"Deleted branch '{branch_name}'."

    def merge_branch(self, source_branch: str, target_branch: str | None = None) -> str:
        """Merge source branch into target branch (or current branch)."""
        repo = self._get_repo()

        # If target not specified, merge into current branch
        if target_branch is None:
            target_branch = repo.active_branch.name

        # Check source branch exists
        if source_branch not in [b.name for b in repo.branches]:
            return f"Branch '{source_branch}' does not exist."

        # Checkout target branch if not current
        current = repo.active_branch.name
        if current != target_branch:
            if target_branch not in [b.name for b in repo.branches]:
                return f"Branch '{target_branch}' does not exist."
            repo.heads[target_branch].checkout()

        try:
            # Perform merge
            repo.git.merge(source_branch)
            return f"Merged '{source_branch}' into '{target_branch}'."
        except Exception as e:
            if "CONFLICT" in str(e) or "conflict" in str(e).lower():
                return f"Merge conflict! Resolve conflicts manually and commit."
            return f"Merge failed: {e}"

    def stash_changes(self, message: str | None = None) -> str:
        """Stash current changes."""
        repo = self._get_repo()

        # Check if there are changes to stash
        if not repo.is_dirty(untracked_files=True):
            return "No changes to stash."

        if message:
            repo.git.stash("push", "-m", message)
            return f"Stashed changes: {message}"
        else:
            repo.git.stash("push")
            return "Stashed changes."

    def stash_pop(self) -> str:
        """Pop the most recent stash."""
        repo = self._get_repo()

        try:
            repo.git.stash("pop")
            return "Applied and removed latest stash."
        except Exception as e:
            if "No stash" in str(e):
                return "No stash entries found."
            return f"Failed to pop stash: {e}"

    def stash_list(self) -> str:
        """List all stashes."""
        repo = self._get_repo()

        try:
            stashes = repo.git.stash("list")
            if not stashes:
                return "No stashes found."
            return stashes
        except Exception:
            return "No stashes found."

    def force_push(self, remote_name: str = "origin") -> str:
        """Force push the current branch to remote."""
        repo = self._get_repo()

        if remote_name not in [r.name for r in repo.remotes]:
            return f"No remote named '{remote_name}' configured."

        remote = repo.remote(remote_name)
        current_branch = repo.active_branch.name

        # Force push
        remote.push(current_branch, force=True)
        return f"Force pushed {current_branch} to {remote_name}."

    def add_remote(self, name: str, url: str) -> str:
        """Add a remote to the repository."""
        repo = self._get_repo()

        if name in [r.name for r in repo.remotes]:
            # Update existing remote
            repo.delete_remote(name)

        repo.create_remote(name, url)
        return f"Added remote '{name}' -> {url}"

    def get_diff(self, staged_only: bool = False) -> str:
        """Get the diff of changes."""
        repo = self._get_repo()

        if staged_only:
            # Get diff of staged changes
            diff = repo.git.diff("--cached")
        else:
            # Get diff of all changes (staged + unstaged)
            diff = repo.git.diff("HEAD")

        if not diff:
            # Check for untracked files
            untracked = repo.untracked_files
            if untracked:
                diff_parts = []
                for f in untracked[:5]:  # Limit to first 5 files
                    try:
                        content = (self.working_directory / f).read_text()
                        # Truncate large files
                        if len(content) > 1000:
                            content = content[:1000] + "\n... (truncated)"
                        diff_parts.append(f"New file: {f}\n{content}")
                    except Exception:
                        diff_parts.append(f"New file: {f}")
                diff = "\n\n".join(diff_parts)

        return diff if diff else "No changes detected."

    def get_status(self) -> str:
        """Get the current repository status."""
        repo = self._get_repo()

        # Get current branch
        try:
            branch = repo.active_branch.name
        except TypeError:
            branch = "HEAD detached"

        # Get changed files
        changed = [item.a_path for item in repo.index.diff(None)]
        staged = [item.a_path for item in repo.index.diff("HEAD")]
        untracked = repo.untracked_files

        status_lines = [f"On branch {branch}"]

        if staged:
            status_lines.append(f"Staged: {', '.join(staged)}")
        if changed:
            status_lines.append(f"Modified: {', '.join(changed)}")
        if untracked:
            status_lines.append(f"Untracked: {', '.join(untracked)}")
        if not staged and not changed and not untracked:
            status_lines.append("Nothing to commit, working tree clean.")

        return "\n".join(status_lines)

    def pull_changes(self, remote_name: str = "origin") -> str:
        """Pull changes from remote."""
        repo = self._get_repo()

        if remote_name not in [r.name for r in repo.remotes]:
            return f"No remote named '{remote_name}' configured."

        remote = repo.remote(remote_name)
        current_branch = repo.active_branch.name

        # Pull from remote
        pull_info = remote.pull(current_branch)

        if pull_info:
            return f"Pulled latest changes from {remote_name}/{current_branch}."
        return f"Already up to date."

    def clone_repo(self, url: str, target_dir: Path | None = None) -> str:
        """Clone a repository from URL."""
        # Extract repo name from URL for default directory
        repo_name = url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        if target_dir is None:
            target_dir = self.working_directory / repo_name

        if target_dir.exists():
            return f"Directory '{target_dir}' already exists."

        # Clone the repository
        self._repo = Repo.clone_from(url, target_dir)
        self.working_directory = target_dir

        return f"Cloned {url} into {target_dir}"


def create_git_engine(working_directory: Path | None = None) -> GitEngine:
    return GitEngine(working_directory=working_directory or Path.cwd())

