from app.controllers.assistant_controller import handle_user_prompt, handle_confirmed_action
from core.action_router.route_action import RouteDependencies
from core.command_parser.parse_command import parse_command
from core.git_engine.service import create_git_engine
from core.github_service.service import create_github_service


def run_cli() -> None:
    git_engine = create_git_engine()
    github_service = create_github_service()
    dependencies = RouteDependencies(git_engine=git_engine, github_service=github_service)

    print("AI Git Desktop")
    print("Type a Git instruction in plain English.")
    print("Type 'exit' to quit.")

    while True:
        prompt = input("\n> ").strip()
        if prompt.lower() in {"exit", "quit"}:
            print("Bye.")
            return

        # Parse the command
        parsed = parse_command(prompt)

        # Handle confirmation flow for dangerous actions
        if parsed.requires_confirmation:
            print(parsed.confirmation_message)
            confirmation = input("").strip().lower()
            if confirmation in ("yes", "y"):
                response = handle_confirmed_action(parsed, dependencies)
            else:
                response = "Action cancelled."
        else:
            response = handle_user_prompt(prompt, dependencies)

        print(response)

