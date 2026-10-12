"""Punto de entrada de la aplicacion Typer."""

import typer

from devbeats.cli.commands_compose import app as compose_app
from devbeats.cli.commands_ai import app as ai_app
from devbeats.cli.commands_project import app as project_app
from devbeats.cli.commands_search import app as search_app

app = typer.Typer(
    name="devbeats",
    help="Compone canciones de cuna como codigo y exportalas a MIDI/LMMS.",
    no_args_is_help=True,
)

# Los comandos quedan al nivel raiz: devbeats new, devbeats build, etc.
app.registered_commands.extend(project_app.registered_commands)
app.registered_commands.extend(compose_app.registered_commands)
app.registered_commands.extend(ai_app.registered_commands)
app.registered_commands.extend(search_app.registered_commands)


if __name__ == "__main__":
    app()

