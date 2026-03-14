import sys


def main() -> None:
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
            print("PySide6 not found. Install it with:")
            print("  pip install PySide6")
            print()
            print("Or run in CLI mode:")
            print("  python main.py --cli")
            print()
            response = input("Run in CLI mode now? (y/n): ").strip().lower()
            if response in ("y", "yes"):
                from app.ui.cli import run_cli
                run_cli()
        else:
            raise


if __name__ == "__main__":
    main()

