from core.action_router.route_action import RouteDependencies, route_action
from core.command_parser.parse_command import parse_command


def handle_user_prompt(prompt: str, dependencies: RouteDependencies) -> str:
    parsed_result = parse_command(prompt)
    return route_action(parsed_result, dependencies)

