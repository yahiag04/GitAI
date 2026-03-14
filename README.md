# AI Git Desktop

Boilerplate Python costruito a partire da [ai_git_desktop_codex_spec.md](/Volumes/SSD1/Personal%20Projects/GitAI/ai_git_desktop_codex_spec.md).

Obiettivo: imparare a costruire il progetto per milestone, non riempire subito tutto di codice.

## Stack

- Python
- CLI prima, desktop UI dopo
- `GitPython` o `subprocess + git` per Git locale
- `PyGithub` per GitHub API
- `PySide6` piu' avanti, quando il core funziona

## Struttura

```text
app/
  controllers/
  ui/
core/
  action_router/
  command_parser/
  git_engine/
  github_service/
tests/
main.py
requirements.txt
```

## Ordine Di Lavoro

1. Completa il parser in [core/command_parser/parse_command.py](/Volumes/SSD1/Personal%20Projects/GitAI/core/command_parser/parse_command.py).
2. Collega il parser al router in [core/action_router/route_action.py](/Volumes/SSD1/Personal%20Projects/GitAI/core/action_router/route_action.py).
3. Implementa il service Git in [core/git_engine/service.py](/Volumes/SSD1/Personal%20Projects/GitAI/core/git_engine/service.py).
4. Solo dopo passa a GitHub e all'interfaccia grafica.

Questo ordine ti costringe a capire bene il dominio prima dell'UI.

## Prima Milestone

Supporta solo questi prompt:

- `commit my changes`
- `push my project`
- `create a branch called feature-login`

Se questi tre casi funzionano end-to-end, la base del progetto e' sana.

## Come Studiare Il Progetto

In ogni file trovi `TODO` o `EXERCISE`.
Usali come check-point.

1. Non scrivere tutto in una volta.
2. Implementa una feature piccola per intero.
3. Verifica a mano prima di passare allo step successivo.

## Primo Esercizio

Inizia da [core/command_parser/models.py](/Volumes/SSD1/Personal%20Projects/GitAI/core/command_parser/models.py) e [core/command_parser/parse_command.py](/Volumes/SSD1/Personal%20Projects/GitAI/core/command_parser/parse_command.py).

Prima devi capire:

- che forma ha un'azione
- quando il parser deve restituire `action=None`
- quali dati servono per `create_branch`

Poi implementi solo il riconoscimento dei tre prompt della prima milestone.

