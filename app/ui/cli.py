from app.controllers.assistant_controller import handle_user_prompt
from core.action_router.route_action import RouteDependencies
from core.git_engine.service import create_git_engine
from core.github_service.service import create_github_service


def run_cli() -> None:
    git_engine = create_git_engine()
    github_service = create_github_service()

    print("AI Git Desktop")
    print("Type a Git instruction in plain English.")
    print("Type 'exit' to quit.")

    while True:
        prompt = input("\n> ").strip()
        if prompt.lower() in {"exit", "quit"}:
            print("Bye.")
            return

        # TODO:
        # replace this simple loop with a proper chat/session model later.
        response = handle_user_prompt(
            prompt,
            RouteDependencies(git_engine=git_engine, github_service=github_service),
        )
        print(response)

