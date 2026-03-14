from dataclasses import dataclass

from core.command_parser.models import ParseCommandResult
from core.git_engine.service import GitEngine
from core.github_service.service import GitHubService


@dataclass(slots=True)
class RouteDependencies:
    git_engine: GitEngine
    github_service: GitHubService


def route_action(result: ParseCommandResult, dependencies: RouteDependencies) -> str:
    if result.action is None:
        return result.reasoning

    if result.requires_confirmation:
        return result.confirmation_message or "Confirmation required."

    if result.action.action == "commit_changes":
        # TODO: call dependencies.git_engine.commit_changes(...)
        return "TODO: commit the current changes."

    if result.action.action == "push_changes":
        # TODO: call dependencies.git_engine.push_changes()
        return "TODO: push the current branch."

    if result.action.action == "create_branch":
        # TODO: call dependencies.git_engine.create_branch(result.action.branch_name)
        return "TODO: create the requested branch."

    if result.action.action == "create_repository":
        # TODO: combine local Git setup and GitHub repo creation.
        return "TODO: create and publish a repository."

    if result.action.action == "open_pull_request":
        # TODO: call dependencies.github_service.create_pull_request(...)
        return "TODO: open a pull request."

    _ = dependencies
    return "Unsupported action."

