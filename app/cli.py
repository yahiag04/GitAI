import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Try to load .env from current directory or package directory
env_file = Path.cwd() / ".env"
if not env_file.exists():
    env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)


def main() -> None:
    """Main entry point for git-assistant."""
    # Check for --cli flag to run in CLI mode
    if "--cli" in sys.argv:
        from app.ui.cli import run_cli
        run_cli()
        return

    # Try to run desktop app, fall back to CLI if PySide6 not available
    try:
        from app.ui.desktop import run_desktop_app
        sys.exit(run_desktop_app())
    except ImportError as e:
        if "PySide6" in str(e):
            print("Desktop UI requires PySide6. Install it with:")
            print("  pip install 'git-assistant[desktop]'")
            print()
            print("Or run in CLI mode:")
            print("  git-assistant --cli")
            print()
            response = input("Run in CLI mode now? (y/n): ").strip().lower()
            if response in ("y", "yes"):
                from app.ui.cli import run_cli
                run_cli()
        else:
            raise


if __name__ == "__main__":
    main()
