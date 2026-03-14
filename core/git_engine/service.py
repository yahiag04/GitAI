from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class GitEngine:
    working_directory: Path

    def init_repo(self, project_path: Path) -> None:
        raise NotImplementedError("TODO: initialize a local Git repository.")

    def commit_changes(self, message: str | None = None) -> None:
        raise NotImplementedError("TODO: stage and commit local changes.")

    def push_changes(self) -> None:
        raise NotImplementedError("TODO: push the current branch to origin.")

    def create_branch(self, branch_name: str) -> None:
        raise NotImplementedError("TODO: create a branch locally.")

    def checkout_branch(self, branch_name: str) -> None:
        raise NotImplementedError("TODO: switch to an existing branch.")


def create_git_engine(working_directory: Path | None = None) -> GitEngine:
    return GitEngine(working_directory=working_directory or Path.cwd())

