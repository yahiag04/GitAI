from core.command_parser.parse_command import parse_command


def test_unknown_command_returns_no_action() -> None:
    result = parse_command("do something unsupported")
    assert result.action is None
    assert "don't understand" in result.reasoning


def test_commit_command() -> None:
    result = parse_command("commit my changes")
    assert result.action is not None
    assert result.action.action == "commit_changes"
    assert result.requires_confirmation is False


def test_commit_simple() -> None:
    result = parse_command("commit")
    assert result.action is not None
    assert result.action.action == "commit_changes"


def test_commit_with_message() -> None:
    result = parse_command("commit with message 'fix bug'")
    assert result.action is not None
    assert result.action.action == "commit_changes"
    assert result.action.message == "fix bug"


def test_push_command() -> None:
    result = parse_command("push my project")
    assert result.action is not None
    assert result.action.action == "push_changes"
    assert result.requires_confirmation is False


def test_push_simple() -> None:
    result = parse_command("push")
    assert result.action is not None
    assert result.action.action == "push_changes"


def test_create_branch_command() -> None:
    result = parse_command("create branch feature-login")
    assert result.action is not None
    assert result.action.action == "create_branch"
    assert result.action.branch_name == "feature-login"
    assert result.requires_confirmation is False


def test_create_branch_with_called() -> None:
    result = parse_command("create a branch called test-branch")
    assert result.action is not None
    assert result.action.action == "create_branch"
    assert result.action.branch_name == "test-branch"


def test_create_repository() -> None:
    result = parse_command("create repo my-app")
    assert result.action is not None
    assert result.action.action == "create_repository"
    assert result.action.repository_name == "my-app"
    assert result.action.visibility == "public"


def test_create_private_repository() -> None:
    result = parse_command("create private repo secret-app")
    assert result.action is not None
    assert result.action.action == "create_repository"
    assert result.action.repository_name == "secret-app"
    assert result.action.visibility == "private"


def test_open_pull_request() -> None:
    result = parse_command("open pr from dev to main")
    assert result.action is not None
    assert result.action.action == "open_pull_request"
    assert result.action.source_branch == "dev"
    assert result.action.target_branch == "main"


def test_create_pull_request() -> None:
    result = parse_command("create pull request from feature to main")
    assert result.action is not None
    assert result.action.action == "open_pull_request"
    assert result.action.source_branch == "feature"
    assert result.action.target_branch == "main"


def test_checkout_branch() -> None:
    result = parse_command("switch to develop")
    assert result.action is not None
    assert result.action.action == "checkout_branch"
    assert result.action.branch_name == "develop"


def test_checkout_simple() -> None:
    result = parse_command("checkout main")
    assert result.action is not None
    assert result.action.action == "checkout_branch"
    assert result.action.branch_name == "main"


def test_delete_branch_requires_confirmation() -> None:
    result = parse_command("delete branch old-feature")
    assert result.action is not None
    assert result.action.action == "delete_branch"
    assert result.action.branch_name == "old-feature"
    assert result.requires_confirmation is True
    assert "old-feature" in result.confirmation_message


def test_force_push_requires_confirmation() -> None:
    result = parse_command("force push")
    assert result.action is not None
    assert result.action.action == "force_push"
    assert result.requires_confirmation is True
    assert "overwrite" in result.confirmation_message.lower()


def test_status() -> None:
    result = parse_command("status")
    assert result.action is not None
    assert result.action.action == "show_status"
