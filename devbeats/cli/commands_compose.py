"""Comandos que generan y exportan composiciones."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from devbeats.adapters.lmms_builder import export_lmms_project
from devbeats.adapters.midi_exporter import export_midi
from devbeats.cli.project_paths import resolve_project
from devbeats.core.generator import generate_lullaby
from devbeats.core.models import Song

app = typer.Typer()
console = Console()


def _load_and_generate(project: Path | None) -> tuple[Path, Song]:
    project_dir = resolve_project(project)
    source = project_dir / "song.yaml"
    if not source.is_file():
        raise FileNotFoundError(f"No se encontro {source}")
    return project_dir, generate_lullaby(Song.from_yaml(source))


def _track_table(song: Song) -> Table:
    table = Table(title=f"{song.metadata.title} · {song.tempo} BPM · {song.key} mayor")
    table.add_column("Pista", style="cyan")
    table.add_column("Instrumento")
    table.add_column("Notas", justify="right", style="green")
    table.add_column("Canal", justify="right")
    for track in song.tracks:
        table.add_row(track.name, track.instrument, str(len(track.notes)), str(track.channel + 1))
    return table


@app.command("build")
def build(project: Path | None = typer.Option(None, "--project", "-p")) -> None:
    """Genera una Lullaby y produce output.mid y output.mmp."""
    try:
        project_dir, song = _load_and_generate(project)
        midi_path = export_midi(song, project_dir / "output.mid")
        lmms_path = export_lmms_project(song, project_dir / "output.mmp")
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    console.print(_track_table(song))
    console.print(f"[bold green]MIDI:[/bold green] {midi_path}")
    console.print(f"[bold green]LMMS experimental:[/bold green] {lmms_path}")


@app.command("export")
def export(
    format_: str = typer.Option("midi", "--format", "-f", help="midi, lmms o all"),
    project: Path | None = typer.Option(None, "--project", "-p"),
) -> None:
    """Exporta nuevamente el proyecto en el formato solicitado."""
    format_ = format_.lower()
    if format_ not in {"midi", "lmms", "all"}:
        raise typer.BadParameter("--format debe ser midi, lmms o all")
    try:
        project_dir, song = _load_and_generate(project)
        if format_ in {"midi", "all"}:
            console.print(f"[green]Creado:[/green] {export_midi(song, project_dir / 'output.mid')}")
        if format_ in {"lmms", "all"}:
            console.print(f"[green]Creado:[/green] {export_lmms_project(song, project_dir / 'output.mmp')}")
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1) from exc

