# Progress Notes

Last updated: 2026-03-14

## Current State

Full MVP implementation complete with AI-powered natural language understanding. The app can handle Git and GitHub commands in plain English.

### Implemented Features

1. **Git Engine** (`core/git_engine/service.py`)
   - `init_repo()` - Initialize a Git repository
   - `commit_changes(message)` - Stage and commit all changes
   - `push_changes()` - Push current branch to origin
   - `pull_changes()` - Pull latest from remote
   - `create_branch(name)` - Create and switch to a new branch
   - `checkout_branch(name)` - Switch to an existing branch
   - `delete_branch(name)` - Delete a local branch
   - `merge_branch(source, target)` - Merge branches
   - `stash_changes()` - Stash current changes
   - `stash_pop()` - Pop the latest stash
   - `stash_list()` - List all stashes
   - `force_push()` - Force push to remote
   - `add_remote(name, url)` - Add a remote
   - `get_status()` - Get repository status
   - `get_diff()` - Show changes
   - `clone_repo(url)` - Clone a repository

2. **GitHub Service** (`core/github_service/service.py`)
   - `create_repo(name, visibility)` - Create a GitHub repository
   - `create_pull_request(input)` - Open a pull request
   - `list_branches(owner, repo)` - List branches
   - `list_commits(owner, repo)` - List commits
   - `get_authenticated_user()` - Get current user
   - `delete_repo(owner, repo)` - Delete a repository

3. **AI Service** (`core/ai_service/service.py`)
   - AI-powered command parsing (OpenAI/Anthropic)
   - AI-generated commit messages
   - Automatic fallback to regex when no API key set

4. **Command Parser** (`core/command_parser/parse_command.py`)
   - **AI-First Parsing**: Uses LLM to understand natural language commands
   - **Regex Fallback**: Works without API keys using pattern matching
   - Supports flexible, conversational commands

5. **Action Router** (`core/action_router/route_action.py`)
   - Routes parsed commands to Git Engine or GitHub Service
   - Handles errors gracefully

6. **Desktop UI** (`app/ui/desktop/`)
   - Modern GitHub-inspired dark theme
   - Chat-style interface
   - Quick action buttons (Smart Commit, Commit, Push, Pull)
   - Repository status sidebar

7. **CLI** (`app/ui/cli.py`)
   - Interactive command loop
   - Confirmation prompts for dangerous operations

## Supported Commands

| Command | Examples |
|---------|----------|
| Commit | `commit`, `save my changes`, `commit my work` |
| Commit with message | `commit with message 'fix bug'`, `save changes message 'update'` |
| Smart Commit (AI) | `smart commit`, `ai commit`, `commit with ai` |
| Push | `push`, `push my project`, `upload changes` |
| Pull | `pull`, `get latest`, `fetch changes` |
| Create branch | `create branch feature-login`, `make a branch called test` |
| Switch branch | `switch to develop`, `checkout main`, `go to feature` |
| Merge | `merge dev into main`, `merge feature` |
| Stash | `stash`, `stash changes`, `save for later` |
| Stash pop | `stash pop`, `unstash`, `apply stash` |
| Stash list | `stash list`, `list stashes`, `show stashes` |
| Status | `status`, `show status`, `git status` |
| Diff | `diff`, `show changes`, `what changed` |
| Init | `init`, `initialize`, `start project` |
| Clone | `clone user/repo`, `clone https://github.com/user/repo` |
| Create repository | `create repo my-app`, `create private repo secret-app` |
| Open pull request | `open pr from dev to main`, `create pull request from feature to main` |
| Delete branch | `delete branch old-feature` (confirmation required) |
| Force push | `force push` (confirmation required) |

## AI-Powered Features

When `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set:

1. **Natural Language Understanding**: Commands like "please make a new branch for the login feature" are correctly interpreted
2. **Smart Commit Messages**: Analyzes your diff and generates meaningful commit messages
3. **Flexible Parsing**: Understands variations and conversational input

Without an API key, the app falls back to regex-based parsing which still supports all commands in standard formats.

## Requirements

- Python 3.11+
- GitPython
- PyGithub
- PySide6 (optional, for desktop UI)
- `GITHUB_TOKEN` environment variable for GitHub operations
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for AI features (optional)

## Running the Desktop App

```bash
python main.py
```

## Running the CLI

```bash
python main.py --cli
```

## Running Tests

```bash
pytest tests/ -v
```

All 48 tests pass.

## Next Steps (Future Features)

- AI explanation of Git errors
- Merge conflict resolution assistant
- Visual Git history graph
- Repository analytics

