"""Tests for AI-powered command parsing."""
import pytest
from unittest.mock import patch, MagicMock

from core.command_parser.parse_command import parse_command, _try_ai_parse
from core.ai_service.service import AIService


def test_ai_parse_returns_none_when_unavailable() -> None:
    """When no API key is set, AI parsing should return None."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = False
        mock_get.return_value = mock_service

        result = _try_ai_parse("commit my changes")
        assert result is None


def test_ai_parse_fallback_to_regex() -> None:
    """When AI unavailable, should fallback to regex parsing."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = False
        mock_get.return_value = mock_service

        result = parse_command("commit my changes", use_ai=True)
        assert result.action is not None
        assert result.action.action == "commit_changes"


def test_ai_parse_successful() -> None:
    """When AI is available, should use AI parsing result."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.parse_command.return_value = {
            "action": "create_branch",
            "branch_name": "my-awesome-feature",
            "requires_confirmation": False,
            "reasoning": "Creating a new feature branch"
        }
        mock_get.return_value = mock_service

        result = parse_command("please make a branch for my awesome feature", use_ai=True)
        assert result.action is not None
        assert result.action.action == "create_branch"
        assert result.action.branch_name == "my-awesome-feature"


def test_ai_parse_unrecognized_command() -> None:
    """When AI doesn't recognize command, should return no action."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.parse_command.return_value = {
            "action": None,
            "reasoning": "This doesn't appear to be a Git command"
        }
        mock_get.return_value = mock_service

        result = parse_command("what's the weather like?", use_ai=True)
        assert result.action is None
        assert "Git command" in result.reasoning


def test_ai_parse_dangerous_action() -> None:
    """AI should correctly identify dangerous actions requiring confirmation."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.parse_command.return_value = {
            "action": "delete_branch",
            "branch_name": "old-feature",
            "requires_confirmation": True,
            "reasoning": "Deleting a branch is a destructive operation"
        }
        mock_get.return_value = mock_service

        result = parse_command("remove the old-feature branch", use_ai=True)
        assert result.action is not None
        assert result.action.action == "delete_branch"
        assert result.requires_confirmation is True
        assert "old-feature" in result.confirmation_message


def test_ai_parse_force_push() -> None:
    """AI should correctly identify force push as dangerous."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.parse_command.return_value = {
            "action": "force_push",
            "requires_confirmation": True,
            "reasoning": "Force pushing can overwrite remote history"
        }
        mock_get.return_value = mock_service

        result = parse_command("push --force to origin", use_ai=True)
        assert result.action is not None
        assert result.action.action == "force_push"
        assert result.requires_confirmation is True
        assert "overwrite" in result.confirmation_message.lower()


def test_ai_parse_natural_language_commit() -> None:
    """AI should understand natural language commit requests."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.parse_command.return_value = {
            "action": "commit_changes",
            "message": "fixed login validation",
            "requires_confirmation": False,
            "reasoning": "Committing with the specified message"
        }
        mock_get.return_value = mock_service

        result = parse_command("save my work with message fixed login validation", use_ai=True)
        assert result.action is not None
        assert result.action.action == "commit_changes"
        assert result.action.message == "fixed login validation"


def test_ai_parse_pr_with_natural_language() -> None:
    """AI should understand natural language PR creation."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.parse_command.return_value = {
            "action": "open_pull_request",
            "source_branch": "feature-auth",
            "target_branch": "main",
            "requires_confirmation": False,
            "reasoning": "Opening a pull request"
        }
        mock_get.return_value = mock_service

        result = parse_command("I want to merge my feature-auth branch into main", use_ai=True)
        assert result.action is not None
        assert result.action.action == "open_pull_request"
        assert result.action.source_branch == "feature-auth"
        assert result.action.target_branch == "main"


def test_ai_service_fallback_on_api_error() -> None:
    """When AI API fails, should fallback to regex."""
    with patch('core.command_parser.parse_command._get_ai_service') as mock_get:
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.parse_command.return_value = None  # API error returns None
        mock_get.return_value = mock_service

        # Should fallback to regex
        result = parse_command("commit", use_ai=True)
        assert result.action is not None
        assert result.action.action == "commit_changes"
