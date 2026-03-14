from dataclasses import dataclass

from core.command_parser.models import ParseCommandResult
from core.git_engine.service import GitEngine
from core.github_service.service import GitHubService, PullRequestInput


@dataclass(slots=True)
class RouteDependencies:
    git_engine: GitEngine
    github_service: GitHubService


def route_action(result: ParseCommandResult, dependencies: RouteDependencies) -> str:
    if result.action is None:
        return result.reasoning

    if result.requires_confirmation:
        return result.confirmation_message or "Confirmation required."

    action = result.action

    try:
        if action.action == "commit_changes":
            message = action.message
            return dependencies.git_engine.commit_changes(message)

        if action.action == "push_changes":
            return dependencies.git_engine.push_changes()

        if action.action == "create_branch":
            if action.branch_name is None:
                return "Error: Branch name is required."
            return dependencies.git_engine.create_branch(action.branch_name)

        if action.action == "checkout_branch":
            if action.branch_name is None:
                return "Error: Branch name is required."
            return dependencies.git_engine.checkout_branch(action.branch_name)

        if action.action == "delete_branch":
            if action.branch_name is None:
                return "Error: Branch name is required."
            return dependencies.git_engine.delete_branch(action.branch_name)

        if action.action == "force_push":
            return dependencies.git_engine.force_push()

        if action.action == "show_status":
            return dependencies.git_engine.get_status()

        if action.action == "create_repository":
            if action.repository_name is None:
                return "Error: Repository name is required."

            # Get the authenticated GitHub user
            owner = dependencies.github_service.get_authenticated_user()
            visibility = action.visibility or "public"

            # Create GitHub repository
            repo_info = dependencies.github_service.create_repo(
                name=action.repository_name,
                visibility=visibility,
            )

            # Initialize local repo if not already initialized
            init_result = dependencies.git_engine.init_repo()

            # Add remote
            remote_url = repo_info.ssh_url
            dependencies.git_engine.add_remote("origin", remote_url)

            # Stage and commit if there are files
            commit_result = dependencies.git_engine.commit_changes("Initial commit")

            # Push to remote
            push_result = dependencies.git_engine.push_changes()

            return (
                f"Created repository: {repo_info.html_url}\n"
                f"{init_result}\n"
                f"{commit_result}\n"
                f"{push_result}"
            )

        if action.action == "open_pull_request":
            if action.source_branch is None or action.target_branch is None:
                return "Error: Source and target branches are required."

            # Get owner and repo from current remote
            # For MVP, we'll require these to be specified
            # In future, we can parse from git remote
            owner = dependencies.github_service.get_authenticated_user()

            # Extract repo name from working directory
            repo_name = dependencies.git_engine.working_directory.name

            pr_input = PullRequestInput(
                owner=owner,
                repo=repo_name,
                title=action.title or f"Merge {action.source_branch} into {action.target_branch}",
                head=action.source_branch,
                base=action.target_branch,
            )

            pr_info = dependencies.github_service.create_pull_request(pr_input)
            return f"Created PR #{pr_info.number}: {pr_info.html_url}"

    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

    return "Unsupported action."

