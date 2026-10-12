"""Comandos de diagnostico y supervision mediante IA."""

import json
import re
import unicodedata
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from devbeats.adapters.gemini_supervisor import GeminiConfigurationError, GeminiSupervisor
from devbeats.adapters.lmms_builder import export_lmms_project
from devbeats.adapters.midi_exporter import export_midi
from devbeats.cli.project_paths import remember_project
from devbeats.core.generator import generate_lullaby
from devbeats.core.models import Metadata, Song

app = typer.Typer()
console = Console()


@app.command("ai-test")
def ai_test() -> None:
    """Comprueba la clave y realiza una peticion minima al director Gemini."""
    try:
        supervisor = GeminiSupervisor.from_environment()
        answer = supervisor.test_connection()
    except (GeminiConfigurationError, RuntimeError) as exc:
        console.print(f"[bold red]Gemini no disponible:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    console.print(
        Panel.fit(
            answer,
            title=f"Gemini conectado · {supervisor.model}",
            border_style="green",
        )
    )


def _safe_folder_name(title: str) -> str:
    ascii_title = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    name = re.sub(r"[^A-Za-z0-9_-]+", "-", ascii_title.strip()).strip("-").lower()
    return name or "cancion-ia"


@app.command("ai-plan")
def ai_plan(
    request: str = typer.Argument(..., help="Describe la cancion que deseas crear."),
    output_dir: Path = typer.Option(Path("canciones"), "--output-dir"),
    no_search: bool = typer.Option(False, "--no-search", help="No usa Google Search."),
) -> None:
    """Investiga, planifica y construye una cancion original completa."""
    try:
        supervisor = GeminiSupervisor.from_environment()
        with console.status("[bold cyan]El director investiga y prepara la cancion..."):
            plan = supervisor.plan_song(request, use_google_search=not no_search)
        if not no_search and not supervisor.search_grounded:
            console.print(
                "[yellow]Google Search no tenia cuota disponible; "
                "se continuo con Gemini sin busqueda.[/yellow]"
            )
        project_dir = (Path.cwd() / output_dir / _safe_folder_name(plan.title)).resolve()
        project_dir.mkdir(parents=True, exist_ok=True)
        song = Song(
            metadata=Metadata(title=plan.title, description=plan.description),
            tempo=plan.tempo,
            bars=plan.bars,
            seed=plan.seed,
        )
        song.to_yaml(project_dir / "song.yaml")
        (project_dir / "ai-plan.json").write_text(
            json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        generated = generate_lullaby(song)
        midi_path = export_midi(generated, project_dir / "output.mid")
        lmms_path = export_lmms_project(generated, project_dir / "output.mmp")
        remember_project(project_dir)
    except (GeminiConfigurationError, RuntimeError, ValueError) as exc:
        console.print(f"[bold red]No fue posible crear la cancion:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    console.print(
        Panel.fit(
            f"[bold green]{plan.title}[/bold green]\n"
            f"{plan.description}\n\n"
            f"Tempo: {plan.tempo} BPM · Compases: {plan.bars} · Ambiente: {plan.mood}\n"
            f"MIDI: {midi_path}\nLMMS: {lmms_path}\nPlan: {project_dir / 'ai-plan.json'}",
            title="Cancion creada por DevBeats",
            border_style="green",
        )
    )

