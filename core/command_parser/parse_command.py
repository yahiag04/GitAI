import re

from core.command_parser.models import ParseCommandResult, CommandAction


def parse_command(prompt: str) -> ParseCommandResult:
    normalized = prompt.strip().lower()

    # === COMMIT ===
    # "commit", "commit my changes", "commit changes", "save my work", etc.
    if re.match(r"^(commit|save)(\s+(my\s+)?(changes?|work))?$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="commit_changes"),
            requires_confirmation=False,
            reasoning="Committing changes.",
        )

    # "commit with message 'fix bug'" or "commit -m 'fix bug'"
    commit_msg = re.match(
        r'^(?:commit|save)(?:\s+(?:my\s+)?(?:changes?\s+)?)?'
        r'(?:with\s+message|message|-m)\s+["\']?(.+?)["\']?$',
        normalized,
    )
    if commit_msg:
        return ParseCommandResult(
            action=CommandAction(action="commit_changes", message=commit_msg.group(1)),
            requires_confirmation=False,
            reasoning="Committing changes with message.",
        )

    # === PUSH ===
    # "push", "push my project", "push changes", "upload"
    if re.match(r"^(push|upload)(\s+(my\s+)?(project|changes?|code))?$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="push_changes"),
            requires_confirmation=False,
            reasoning="Pushing to remote.",
        )

    # === CREATE BRANCH ===
    # "create branch feature-x", "new branch test", "create a branch called dev"
    branch_match = re.match(
        r"^(?:create|new|make)(?:\s+a)?\s+branch\s+(?:called\s+|named\s+)?([a-z0-9._/-]+)$",
        normalized,
    )
    if branch_match:
        return ParseCommandResult(
            action=CommandAction(action="create_branch", branch_name=branch_match.group(1)),
            requires_confirmation=False,
            reasoning=f"Creating branch '{branch_match.group(1)}'.",
        )

    # === SWITCH/CHECKOUT BRANCH ===
    # "switch to main", "checkout dev", "go to branch feature"
    checkout_match = re.match(
        r"^(?:switch\s+to|checkout|go\s+to)(?:\s+branch)?\s+([a-z0-9._/-]+)$",
        normalized,
    )
    if checkout_match:
        return ParseCommandResult(
            action=CommandAction(action="checkout_branch", branch_name=checkout_match.group(1)),
            requires_confirmation=False,
            reasoning=f"Switching to branch '{checkout_match.group(1)}'.",
        )

    # === CREATE REPOSITORY ===
    # "create repo my-app", "create a private repository called test"
    repo_match = re.match(
        r"^(?:create|new|make)(?:\s+a)?\s+(public\s+|private\s+)?"
        r"(?:repo|repository)\s+(?:called\s+|named\s+)?([a-z0-9._-]+)$",
        normalized,
    )
    if repo_match:
        visibility = (repo_match.group(1) or "public").strip()
        repo_name = repo_match.group(2)
        return ParseCommandResult(
            action=CommandAction(
                action="create_repository",
                repository_name=repo_name,
                visibility=visibility,
            ),
            requires_confirmation=False,
            reasoning=f"Creating {visibility} repository '{repo_name}'.",
        )

    # === OPEN PULL REQUEST ===
    # "open pr from dev to main", "create pull request from feature to main"
    pr_match = re.match(
        r"^(?:open|create|make)(?:\s+a)?\s+(?:pull\s+request|pr)\s+"
        r"from\s+([a-z0-9._/-]+)\s+to\s+([a-z0-9._/-]+)$",
        normalized,
    )
    if pr_match:
        return ParseCommandResult(
            action=CommandAction(
                action="open_pull_request",
                source_branch=pr_match.group(1),
                target_branch=pr_match.group(2),
            ),
            requires_confirmation=False,
            reasoning=f"Opening PR from '{pr_match.group(1)}' to '{pr_match.group(2)}'.",
        )

    # === DELETE BRANCH (DANGEROUS) ===
    # "delete branch old-feature", "remove branch test"
    delete_match = re.match(
        r"^(?:delete|remove)(?:\s+the)?\s+branch\s+(?:called\s+|named\s+)?([a-z0-9._/-]+)$",
        normalized,
    )
    if delete_match:
        branch = delete_match.group(1)
        return ParseCommandResult(
            action=CommandAction(action="delete_branch", branch_name=branch),
            requires_confirmation=True,
            reasoning=f"Deleting branch '{branch}'.",
            confirmation_message=f"This will delete branch '{branch}'. Are you sure? (yes/no)",
        )

    # === FORCE PUSH (DANGEROUS) ===
    if normalized in ("force push", "push --force", "push -f"):
        return ParseCommandResult(
            action=CommandAction(action="force_push"),
            requires_confirmation=True,
            reasoning="Force pushing.",
            confirmation_message="Force push will overwrite remote history. Are you sure? (yes/no)",
        )

    # === STATUS ===
    if normalized in ("status", "show status", "git status", "what changed"):
        return ParseCommandResult(
            action=CommandAction(action="show_status"),
            requires_confirmation=False,
            reasoning="Showing repository status.",
        )

    # === NOT RECOGNIZED ===
    return ParseCommandResult(
        action=None,
        requires_confirmation=False,
        reasoning=f"Sorry, I don't understand '{prompt}'. Try commands like:\n"
                  f"  - commit my changes\n"
                  f"  - push\n"
                  f"  - create branch feature-x\n"
                  f"  - switch to main\n"
                  f"  - status",
    )

