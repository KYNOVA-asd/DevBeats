"""Comandos que generan y exportan composiciones."""

from pathlib import Path
import subprocess

import typer
from rich.console import Console
from rich.table import Table

from devbeats.adapters.lmms_builder import export_lmms_project
from devbeats.adapters.midi_exporter import export_midi
from devbeats.cli.project_paths import resolve_project
from devbeats.cli.project_paths import remember_project
from devbeats.cli.commands_ai import _safe_folder_name
from devbeats.core.arranger import arrange_chord_sheet
from devbeats.core.chord_parser import parse_chord_sheet
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
    table = Table(title=f"{song.metadata.title} · {song.tempo} BPM · Tono {song.key}")
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


@app.command("import-chords")
def import_chords(
    source: Path = typer.Argument(..., exists=True, dir_okay=True, readable=True),
    title: str | None = typer.Option(None, "--title", help="Titulo de la cancion."),
    tempo: int = typer.Option(72, "--tempo", min=40, max=200),
    output_dir: Path = typer.Option(Path("canciones"), "--output-dir"),
    edit_if_missing: bool = typer.Option(
        False,
        "--edit-if-missing",
        help="Crea source.txt y abre Bloc de notas cuando no existe.",
    ),
    edit: bool = typer.Option(
        False,
        "--edit",
        help="Abre el cancionero en Bloc de notas antes de generar.",
    ),
) -> None:
    """Convierte letra y acordes en MIDI/MMP para escuchar en LMMS."""
    try:
        opened_editor = False
        if source.is_dir():
            candidates = list(source.rglob("source.txt"))
            if title:
                wanted = _safe_folder_name(title)
                exact = [candidate for candidate in candidates if candidate.parent.name.lower() == wanted]
                matching = [candidate for candidate in candidates if wanted in candidate.parent.name.lower()]
                if len(exact) == 1:
                    candidates = exact
                elif len(matching) == 1:
                    candidates = matching
            if not candidates:
                if not edit_if_missing:
                    raise ValueError(f"No se encontro ningun source.txt dentro de {source}")
                if not title:
                    raise ValueError("Escribe un titulo para crear el nuevo cancionero")
                new_source = source / _safe_folder_name(title) / "source.txt"
                new_source.parent.mkdir(parents=True, exist_ok=True)
                new_source.write_text(
                    "Tono: Dm\n\n"
                    "[Verso]\n"
                    "# Pega una linea de acordes y debajo su linea de letra.\n"
                    "# Ejemplo: Dm  Gm  Asus4  Dm\n"
                    "# Guarda el archivo y cierra el Bloc de notas para continuar.\n",
                    encoding="utf-8",
                )
                console.print(f"[yellow]Cancionero creado:[/yellow] {new_source}")
                console.print("[yellow]Pega tu letra y acordes, guarda y cierra el Bloc de notas.[/yellow]")
                subprocess.run(["notepad.exe", str(new_source)], check=True)
                opened_editor = True
                candidates = [new_source]
            if len(candidates) > 1:
                choices = ", ".join(str(candidate) for candidate in candidates[:5])
                raise ValueError(
                    "Hay varios source.txt. Escribe un titulo que coincida con la carpeta "
                    f"o proporciona el archivo completo. Opciones: {choices}"
                )
            source = candidates[0]
            console.print(f"[cyan]Cancionero encontrado:[/cyan] {source}")
        if edit and not opened_editor:
            console.print("[yellow]Edita, guarda y cierra el Bloc de notas para continuar.[/yellow]")
            subprocess.run(["notepad.exe", str(source)], check=True)
        text = source.read_text(encoding="utf-8")
        sheet = parse_chord_sheet(text)
        song_title = title or source.stem.replace("-", " ").title()
        project_dir = (Path.cwd() / output_dir / _safe_folder_name(song_title)).resolve()
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "source.txt").write_text(text, encoding="utf-8")
        song = arrange_chord_sheet(sheet, song_title, tempo=tempo)
        song.to_yaml(project_dir / "song.yaml")
        midi_path = export_midi(song, project_dir / "output.mid")
        lmms_path = export_lmms_project(song, project_dir / "output.mmp")
        remember_project(project_dir)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        console.print(f"[bold red]No fue posible importar el cancionero:[/bold red] {exc}")
        raise typer.Exit(1) from exc
    console.print(_track_table(song))
    console.print(f"[bold green]MIDI para LMMS:[/bold green] {midi_path}")
    console.print(f"[bold green]Proyecto MMP:[/bold green] {lmms_path}")

