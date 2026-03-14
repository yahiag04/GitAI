# Git Assistant

A modern desktop application that lets you manage Git and GitHub using natural language. No more memorizing commands - just tell it what you want to do.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)

## Features

- **Natural Language Commands** - Type commands like "commit my changes" or "create a branch called feature-login"
- **AI-Powered Understanding** - Uses OpenAI or Anthropic to understand flexible, conversational input
- **Smart Commit Messages** - Automatically generates meaningful commit messages by analyzing your changes
- **Modern Desktop UI** - Clean, GitHub-inspired dark theme with chat interface
- **CLI Mode** - Full functionality available from the terminal
- **Safe by Default** - Dangerous operations (delete branch, force push) require confirmation

## Demo

```
> create a new branch for the login feature
Created and switched to branch 'login-feature'.

> status
On branch login-feature
Modified: src/auth.py, src/utils.py

> smart commit
Committed: a3f2b1c - Add user authentication with session handling
(AI-generated message)

> push
Pushed login-feature to origin.

> open pr from login-feature to main
Created PR #42: https://github.com/user/repo/pull/42
```

## Quick Start

### Installation

```bash
# Clone and install
git clone https://github.com/yourusername/git-assistant.git
cd git-assistant
pip install .

# With desktop UI support
pip install ".[desktop]"
```

Or install directly from GitHub:
```bash
pip install git+https://github.com/yourusername/git-assistant.git
```

### Configuration

Create a `.env` file in your home directory or project folder:

```bash
# Required for GitHub operations (create at https://github.com/settings/tokens)
GITHUB_TOKEN=your_github_token

# Optional: Enable AI features (at least one recommended)
# Get OpenAI key at: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_key

# Or get Anthropic key at: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_key
```

### Run

```bash
# Desktop app (requires PySide6)
git-assistant

# CLI mode
git-assistant --cli
```

You can also run directly with Python:
```bash
python main.py        # Desktop
python main.py --cli  # CLI
```

## Supported Commands

| Action | Example Commands |
|--------|------------------|
| **Commit** | `commit`, `commit my changes`, `save my work` |
| **Commit with message** | `commit with message "fix login bug"` |
| **Smart Commit** | `smart commit`, `ai commit` (generates message automatically) |
| **Push** | `push`, `push my changes`, `upload to remote` |
| **Pull** | `pull`, `get latest`, `fetch changes` |
| **Create Branch** | `create branch feature-x`, `make a new branch called hotfix` |
| **Switch Branch** | `switch to main`, `checkout develop` |
| **Merge** | `merge feature into main`, `merge develop` |
| **Stash** | `stash`, `stash my changes`, `save for later` |
| **Unstash** | `stash pop`, `unstash`, `apply stash` |
| **Status** | `status`, `show status` |
| **Diff** | `diff`, `show changes`, `what changed` |
| **Clone** | `clone user/repo`, `clone https://github.com/user/repo` |
| **Init** | `init`, `initialize` |
| **Create Repo** | `create repo my-app`, `create private repo secret-project` |
| **Open PR** | `open pr from feature to main` |
| **Delete Branch** | `delete branch old-feature` (requires confirmation) |
| **Force Push** | `force push` (requires confirmation) |

## AI Features

When an AI API key is configured:

1. **Flexible Input** - Say things like "can you please make me a new branch for the login feature" and it just works
2. **Smart Commits** - Analyzes your diff and writes descriptive commit messages
3. **Context Understanding** - Interprets variations and conversational phrasing

Without an API key, the app uses pattern matching which supports all commands in standard formats.

## Project Structure

```
git-assistant/
├── app/
│   ├── cli.py            # Main entry point
│   ├── controllers/      # Business logic
│   └── ui/
│       ├── cli.py        # Command-line interface
│       └── desktop/      # PySide6 desktop app
├── core/
│   ├── ai_service/       # OpenAI/Anthropic integration
│   ├── command_parser/   # Natural language parsing
│   ├── git_engine/       # Git operations (GitPython)
│   ├── github_service/   # GitHub API (PyGithub)
│   └── action_router/    # Command routing
├── tests/                # Test suite (48 tests)
├── main.py               # Direct execution entry point
├── pyproject.toml        # Package configuration
└── requirements.txt      # Dependencies
```

## Requirements

- Python 3.11+
- GitPython
- PyGithub
- PySide6 (optional, for desktop UI)
- python-dotenv
- certifi

## Development

```bash
# Install with dev dependencies
pip install -e ".[all]"

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_parse_command.py -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.
