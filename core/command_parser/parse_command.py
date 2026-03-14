import re
from pathlib import Path
from typing import Optional

# Load .env before importing AI service
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from core.command_parser.models import ParseCommandResult, CommandAction
from core.ai_service.service import AIService, create_ai_service


# Global AI service instance (lazy loaded)
_ai_service: Optional[AIService] = None


def _get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = create_ai_service()
    return _ai_service


def parse_command(prompt: str, use_ai: bool = True) -> ParseCommandResult:
    """Parse a natural language command into a structured action.

    Args:
        prompt: The user's input
        use_ai: Whether to try AI parsing first (default True)

    Returns:
        ParseCommandResult with the parsed action
    """
    # Try AI parsing first if enabled and available
    if use_ai:
        ai_result = _try_ai_parse(prompt)
        if ai_result is not None:
            return ai_result

    # Fall back to regex parsing
    return _regex_parse(prompt)


def _try_ai_parse(prompt: str) -> Optional[ParseCommandResult]:
    """Try to parse the command using AI."""
    ai_service = _get_ai_service()

    if not ai_service.is_available():
        return None

    result = ai_service.parse_command(prompt)
    if result is None:
        return None

    # Convert AI response to ParseCommandResult
    action_name = result.get("action")
    if action_name is None:
        return ParseCommandResult(
            action=None,
            requires_confirmation=False,
            reasoning=result.get("reasoning", "I don't understand that command."),
        )

    # Build CommandAction from AI response
    try:
        action = CommandAction(
            action=action_name,
            branch_name=result.get("branch_name"),
            source_branch=result.get("source_branch"),
            target_branch=result.get("target_branch"),
            message=result.get("message"),
            clone_url=result.get("clone_url"),
            repository_name=result.get("repository_name"),
            visibility=result.get("visibility"),
        )

        requires_confirmation = result.get("requires_confirmation", False)
        reasoning = result.get("reasoning", "")

        # Generate confirmation message for dangerous actions
        confirmation_message = None
        if requires_confirmation:
            if action_name == "delete_branch":
                confirmation_message = f"This will delete branch '{action.branch_name}'. Are you sure? (yes/no)"
            elif action_name == "force_push":
                confirmation_message = "Force push will overwrite remote history. Are you sure? (yes/no)"
            else:
                confirmation_message = "This is a dangerous action. Are you sure? (yes/no)"

        return ParseCommandResult(
            action=action,
            requires_confirmation=requires_confirmation,
            reasoning=reasoning,
            confirmation_message=confirmation_message,
        )
    except Exception:
        return None


def _regex_parse(prompt: str) -> ParseCommandResult:
    """Parse command using regex patterns (fallback)."""
    normalized = prompt.strip().lower()

    # === SMART COMMIT (AI-generated message) ===
    if re.match(r"^(smart|ai|auto)\s+commit$", normalized) or \
       re.match(r"^commit\s+(with\s+)?(ai|auto|smart)$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="smart_commit"),
            requires_confirmation=False,
            reasoning="Generating AI commit message.",
        )

    # === COMMIT ===
    if re.match(r"^(commit|save)(\s+(my\s+)?(changes?|work))?$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="commit_changes"),
            requires_confirmation=False,
            reasoning="Committing changes.",
        )

    # Commit with message
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
    if re.match(r"^(push|upload)(\s+(my\s+)?(project|changes?|code))?$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="push_changes"),
            requires_confirmation=False,
            reasoning="Pushing to remote.",
        )

    # === CREATE BRANCH ===
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

    # === MERGE ===
    merge_match = re.match(
        r"^merge\s+([a-z0-9._/-]+)(?:\s+into\s+([a-z0-9._/-]+))?$",
        normalized,
    )
    if merge_match:
        source = merge_match.group(1)
        target = merge_match.group(2)
        return ParseCommandResult(
            action=CommandAction(
                action="merge_branch",
                source_branch=source,
                target_branch=target,
            ),
            requires_confirmation=False,
            reasoning=f"Merging '{source}' into '{target or 'current branch'}'.",
        )

    # === STASH ===
    if re.match(r"^(stash|stash\s+changes?|save\s+changes?\s+for\s+later)$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="stash_changes"),
            requires_confirmation=False,
            reasoning="Stashing current changes.",
        )

    if re.match(r"^(stash\s+pop|pop\s+stash|apply\s+stash|unstash|restore\s+stash)$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="stash_pop"),
            requires_confirmation=False,
            reasoning="Applying latest stash.",
        )

    if re.match(r"^(stash\s+list|list\s+stash(es)?|show\s+stash(es)?)$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="stash_list"),
            requires_confirmation=False,
            reasoning="Listing stashes.",
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
    if normalized in ("status", "show status", "git status"):
        return ParseCommandResult(
            action=CommandAction(action="show_status"),
            requires_confirmation=False,
            reasoning="Showing repository status.",
        )

    # === DIFF ===
    if normalized in ("diff", "show diff", "show changes", "what changed", "changes"):
        return ParseCommandResult(
            action=CommandAction(action="show_diff"),
            requires_confirmation=False,
            reasoning="Showing changes.",
        )

    # === PULL ===
    if re.match(r"^(pull|get\s+latest|fetch\s+changes?)(\s+(changes?|from\s+\w+))?$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="pull_changes"),
            requires_confirmation=False,
            reasoning="Pulling latest changes from remote.",
        )

    # === INIT ===
    if re.match(r"^(init|initialize|start\s+project|create\s+git\s+repo(\s+here)?)$", normalized):
        return ParseCommandResult(
            action=CommandAction(action="init_repo"),
            requires_confirmation=False,
            reasoning="Initializing a new Git repository.",
        )

    # === CLONE ===
    clone_match = re.match(
        r"^clone\s+(https?://[^\s]+|git@[^\s]+|[a-z0-9_-]+/[a-z0-9_.-]+)$",
        normalized,
    )
    if clone_match:
        url = clone_match.group(1)
        if not url.startswith(("http", "git@")):
            url = f"https://github.com/{url}"
        return ParseCommandResult(
            action=CommandAction(action="clone_repo", clone_url=url),
            requires_confirmation=False,
            reasoning=f"Cloning repository from {url}.",
        )

    # === NOT RECOGNIZED ===
    return ParseCommandResult(
        action=None,
        requires_confirmation=False,
        reasoning=f"I don't understand '{prompt}'. Try commands like:\n"
                  f"  - commit my changes\n"
                  f"  - push\n"
                  f"  - create branch feature-x\n"
                  f"  - merge dev into main\n"
                  f"  - status",
    )
