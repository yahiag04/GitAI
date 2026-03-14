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


def test_pull() -> None:
    result = parse_command("pull")
    assert result.action is not None
    assert result.action.action == "pull_changes"


def test_pull_changes() -> None:
    result = parse_command("pull changes")
    assert result.action is not None
    assert result.action.action == "pull_changes"


def test_get_latest() -> None:
    result = parse_command("get latest")
    assert result.action is not None
    assert result.action.action == "pull_changes"


def test_init() -> None:
    result = parse_command("init")
    assert result.action is not None
    assert result.action.action == "init_repo"


def test_initialize() -> None:
    result = parse_command("initialize")
    assert result.action is not None
    assert result.action.action == "init_repo"


def test_clone_full_url() -> None:
    result = parse_command("clone https://github.com/user/repo")
    assert result.action is not None
    assert result.action.action == "clone_repo"
    assert result.action.clone_url == "https://github.com/user/repo"


def test_clone_shorthand() -> None:
    result = parse_command("clone user/repo")
    assert result.action is not None
    assert result.action.action == "clone_repo"
    assert result.action.clone_url == "https://github.com/user/repo"


def test_smart_commit() -> None:
    result = parse_command("smart commit")
    assert result.action is not None
    assert result.action.action == "smart_commit"


def test_ai_commit() -> None:
    result = parse_command("ai commit")
    assert result.action is not None
    assert result.action.action == "smart_commit"


def test_commit_with_ai() -> None:
    result = parse_command("commit with ai")
    assert result.action is not None
    assert result.action.action == "smart_commit"


def test_show_diff() -> None:
    result = parse_command("diff")
    assert result.action is not None
    assert result.action.action == "show_diff"


def test_show_changes() -> None:
    result = parse_command("show changes")
    assert result.action is not None
    assert result.action.action == "show_diff"


def test_what_changed() -> None:
    result = parse_command("what changed")
    assert result.action is not None
    assert result.action.action == "show_diff"
