from core.action_router.route_action import RouteDependencies, route_action
from core.command_parser.models import ParseCommandResult
from core.command_parser.parse_command import parse_command


def handle_user_prompt(prompt: str, dependencies: RouteDependencies) -> str:
    parsed_result = parse_command(prompt)
    return route_action(parsed_result, dependencies)


def handle_confirmed_action(
    parsed_result: ParseCommandResult,
    dependencies: RouteDependencies,
) -> str:
    """Execute a dangerous action that has been confirmed by the user."""
    # Clear the confirmation flag since user confirmed
    confirmed_result = ParseCommandResult(
        action=parsed_result.action,
        requires_confirmation=False,
        reasoning=parsed_result.reasoning,
        confirmation_message=None,
    )
    return route_action(confirmed_result, dependencies)

