# Progress Notes

Last updated: 2026-03-14

## Current State

- The project scaffold has been converted from TypeScript to Python.
- The current architecture is:
  - `app/controllers`
  - `app/ui`
  - `core/command_parser`
  - `core/action_router`
  - `core/git_engine`
  - `core/github_service`
- The parser milestone is done for the first three commands:
  - `commit my changes`
  - `push my project`
  - `create a branch called feature-login`

## Files Completed

- `core/command_parser/models.py`
- `core/command_parser/parse_command.py`
- `tests/test_parse_command.py`

## Notes

- `parse_command.py` now:
  - normalizes user input
  - matches exact commit and push commands
  - extracts branch names with regex
  - returns `action=None` for unsupported commands
- The parser no longer asks for confirmation for safe MVP actions.
- `py_compile` passes on the current Python files.
- `pytest` has not been run because it is not installed in the current environment.

## Next Step

Work on `core/action_router/route_action.py`.

Goal:

- map parsed actions to method calls on `git_engine`
- return simple user-facing success messages

For the current milestone, implement only:

- `commit_changes`
- `push_changes`
- `create_branch`

## Reminder For Next Session

Do not jump to GitHub or desktop UI yet.
Finish this order first:

1. action router
2. git engine
3. manual CLI flow
4. tests

