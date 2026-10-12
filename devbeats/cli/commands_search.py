"""Comandos de investigacion musical mediante navegador."""

from pathlib import Path

import typer
from rich.console import Console

from devbeats.adapters.browser_search import BrowserLaunchError, open_search
from devbeats.core.profile import DevBeatsProfile

app = typer.Typer()
console = Console()


@app.command("search")
def search(
    query: str = typer.Argument(..., help="Tema musical que deseas investigar."),
    profile_file: Path = typer.Option(
        Path("devbeats.profile.yaml"), "--profile", help="Perfil de DevBeats."
    ),
) -> None:
    """Abre una investigacion musical en el modo IA de Google."""
    try:
        profile = DevBeatsProfile.from_yaml(profile_file)
        url = open_search(query, profile.browser_search)
    except (ValueError, BrowserLaunchError) as exc:
        console.print(f"[bold red]No fue posible abrir la busqueda:[/bold red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"[green]Busqueda abierta en el navegador:[/green] {url}")

