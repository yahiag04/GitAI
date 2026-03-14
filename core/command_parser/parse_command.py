import re

from core.command_parser.models import ParseCommandResult, CommandAction


def parse_command(prompt: str) -> ParseCommandResult:
    normalized_prompt = prompt.strip().lower()

    rules = [
        (r"^create a branch called (?P<branch_name>[a-z0-9._/-]+)$", "create_branch"),
        (r"^commit my changes$", "commit_changes"),
        (r"^push my project$", "push_changes")

    ]
    
    for pattern, action_name in rules:
        match = re.match(pattern, normalized_prompt)
        if match:
            if action_name == "create_branch":
                branch_name = match.group("branch_name")
                return ParseCommandResult(
                    action=CommandAction(
                        action=action_name,
                        branch_name=branch_name
                    ),
                    requires_confirmation=False,
                    reasoning=f"The user wants to create a branch called '{branch_name}'"
                )
            else:
                return ParseCommandResult(
                    action=CommandAction(action=action_name),
                    requires_confirmation=False,
                    reasoning=f"The user wants to {action_name.replace('_', ' ')}. This is a safe action that does not require confirmation."
                )

    # EXERCISE:
    # 1. start with exact matches for:
    #    - "commit my changes"
    #    - "push my project"
    # 2. then use a regex for:
    #    - "create a branch called <name>"
    # 3. only after that should you think about smarter NLP or LLM parsing.
    #
    # Suggested regex:
    # r"^create a branch called (?P<branch_name>[a-z0-9._/-]+)$"
    #
    # When you match a command, return a ParseCommandResult with:
    # - action set to a CommandAction instance
    # - requires_confirmation=False
    # - reasoning set to a short explanation
    #
    # When you do not match anything:
    # - action=None
    # - reasoning="Command not supported yet."


    return ParseCommandResult(
        action=None,
        requires_confirmation=False,
        reasoning="Command not supported yet.",
    )

