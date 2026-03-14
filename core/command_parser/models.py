from dataclasses import dataclass
from typing import Literal, Optional


ActionName = Literal[
    "create_repository",
    "commit_changes",
    "smart_commit",
    "push_changes",
    "pull_changes",
    "create_branch",
    "checkout_branch",
    "delete_branch",
    "open_pull_request",
    "force_push",
    "show_status",
    "show_diff",
    "init_repo",
    "clone_repo",
]


@dataclass(slots=True)
class CommandAction:
    action: ActionName
    repository_name: Optional[str] = None
    visibility: Optional[Literal["public", "private"]] = None
    message: Optional[str] = None
    branch_name: Optional[str] = None
    source_branch: Optional[str] = None
    target_branch: Optional[str] = None
    title: Optional[str] = None
    clone_url: Optional[str] = None


@dataclass(slots=True)
class ParseCommandResult:
    action: Optional[CommandAction]
    requires_confirmation: bool
    reasoning: str
    confirmation_message: Optional[str] = None

