from dataclasses import dataclass
from typing import Literal, Optional


ActionName = Literal[
    "create_repository",
    "commit_changes",
    "push_changes",
    "create_branch",
    "open_pull_request",
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


@dataclass(slots=True)
class ParseCommandResult:
    action: Optional[CommandAction]
    requires_confirmation: bool
    reasoning: str
    confirmation_message: Optional[str] = None

