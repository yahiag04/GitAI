# Progress Notes

Last updated: 2026-03-14

## Current State

MVP implementation complete. The CLI can now handle natural language Git and GitHub commands.

### Implemented Features

1. **Git Engine** (`core/git_engine/service.py`)
   - `init_repo()` - Initialize a Git repository
   - `commit_changes(message)` - Stage and commit all changes
   - `push_changes()` - Push current branch to origin
   - `create_branch(name)` - Create and switch to a new branch
   - `checkout_branch(name)` - Switch to an existing branch
   - `delete_branch(name)` - Delete a local branch
   - `force_push()` - Force push to remote
   - `add_remote(name, url)` - Add a remote
   - `get_status()` - Get repository status

2. **GitHub Service** (`core/github_service/service.py`)
   - `create_repo(name, visibility)` - Create a GitHub repository
   - `create_pull_request(input)` - Open a pull request
   - `list_branches(owner, repo)` - List branches
   - `list_commits(owner, repo)` - List commits
   - `get_authenticated_user()` - Get current user
   - `delete_repo(owner, repo)` - Delete a repository

3. **Command Parser** (`core/command_parser/parse_command.py`)
   Supports natural language commands:
   - `commit my changes` / `commit changes with message 'fix bug'`
   - `push` / `push my project` / `push changes`
   - `create a branch called feature-login`
   - `create a repository called my-app`
   - `create a private repo called secret-app`
   - `open a pull request from dev to main`
   - `switch to develop` / `checkout branch main`
   - `delete branch old-feature` (requires confirmation)
   - `force push` (requires confirmation)

4. **Action Router** (`core/action_router/route_action.py`)
   - Routes parsed commands to Git Engine or GitHub Service
   - Handles errors gracefully

5. **CLI** (`app/ui/cli.py`)
   - Interactive command loop
   - Confirmation prompts for dangerous operations

## Supported Commands

| Command | Example |
|---------|---------|
| Commit | `commit my changes` |
| Commit with message | `commit changes with message 'fix bug'` |
| Push | `push my project` |
| Create branch | `create a branch called feature-login` |
| Switch branch | `switch to develop` |
| Create repository | `create a repository called my-app` |
| Create private repo | `create a private repo called secret-app` |
| Open pull request | `open a pull request from dev to main` |
| Delete branch | `delete branch old-feature` (confirmation required) |
| Force push | `force push` (confirmation required) |

## Requirements

- Python 3.11+
- GitPython
- PyGithub
- `GITHUB_TOKEN` environment variable for GitHub operations

## Running the CLI

```bash
python main.py
```

## Running Tests

```bash
pytest tests/ -v
```

All 15 tests pass.

## Desktop UI

The desktop application is now available using PySide6.

### Features
- Modern dark theme (Catppuccin-inspired)
- Chat-style interface for natural language commands
- Repository status sidebar
- Open any repository folder
- Confirmation dialogs for dangerous operations
- Background command execution (non-blocking UI)

### Running the Desktop App

```bash
python main.py
```

### Running the CLI

```bash
python main.py --cli
```

## Next Steps (Future Features)

- AI explanation of Git errors
- Automated commit message generation
- Merge conflict resolution assistant
- Visual Git history graph

