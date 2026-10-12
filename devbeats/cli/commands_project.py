"""Comandos para crear e inspeccionar proyectos."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from devbeats.cli.project_paths import remember_project, resolve_project
from devbeats.core.models import Metadata, Song

app = typer.Typer()
console = Console()


@app.command("new")
def new_project(
    name: str = typer.Argument(..., help="Nombre o ruta del nuevo proyecto."),
    force: bool = typer.Option(False, "--force", help="Reemplaza solo song.yaml si existe."),
) -> None:
    """Crea un proyecto Lullaby y lo establece como proyecto activo."""
    project_dir = (Path.cwd() / name).resolve()
    song_file = project_dir / "song.yaml"
    if song_file.exists() and not force:
        raise typer.BadParameter(f"Ya existe {song_file}. Usa --force para reemplazarlo.")

    project_dir.mkdir(parents=True, exist_ok=True)
    song = Song(
        metadata=Metadata(title=project_dir.name, description="Cancion de cuna creada con DevBeats"),
        tempo=68,
        key="C",
        bars=8,
        seed=42,
    )
    song.to_yaml(song_file)
    remember_project(project_dir)
    console.print(
        Panel.fit(
            f"[bold green]Proyecto creado[/bold green]\n{song_file}\n\n"
            "Siguiente paso: [cyan]python -m devbeats.main build[/cyan]",
            title="DevBeats",
        )
    )


@app.command("status")
def status(project: Path | None = typer.Option(None, "--project", "-p")) -> None:
    """Muestra la configuracion del proyecto activo."""
    try:
        project_dir = resolve_project(project)
        song = Song.from_yaml(project_dir / "song.yaml")
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1) from exc
    console.print(
        Panel.fit(
            f"[bold]{song.metadata.title}[/bold]\n"
            f"Proyecto: {project_dir}\nTempo: {song.tempo} BPM\n"
            f"Tonalidad: {song.key}\nCompases: {song.bars}\nPistas: {len(song.tracks)}",
            title="Estado",
        )
    )

