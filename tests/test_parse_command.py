from core.command_parser.parse_command import parse_command


def test_unknown_command_returns_no_action() -> None:
    result = parse_command("do something unsupported")
    assert result.action is None


# EXERCISE:
# add tests for:
# - "commit my changes"
# - "push my project"
# - "create a branch called feature-login"

def test_commit_command() -> None:
    result = parse_command("commit my changes")
    assert result.action is not None
    assert result.action.action == "commit_changes"
    assert result.requires_confirmation is False
    assert "commit their changes" in result.reasoning

def test_push_command() -> None:
    result = parse_command("push my project")
    assert result.action is not None
    assert result.action.action == "push_changes"
    assert result.requires_confirmation is False
    assert "push their changes" in result.reasoning

def test_create_branch_command() -> None:
    result = parse_command("create a branch called feature-login")
    assert result.action is not None
    assert result.action.action == "create_branch"
    assert result.action.branch_name == "feature-login"
    assert result.requires_confirmation is False
    assert "create a branch called 'feature-login'" in result.reasoning
