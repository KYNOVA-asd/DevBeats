"""Resolucion segura y centralizada de proyectos DevBeats."""

from pathlib import Path

CURRENT_PROJECT_FILE = ".devbeats-current"


def remember_project(project_dir: Path, workspace: Path | None = None) -> None:
    workspace = (workspace or Path.cwd()).resolve()
    project_dir = project_dir.resolve()
    try:
        stored = project_dir.relative_to(workspace).as_posix()
    except ValueError:
        stored = str(project_dir)
    (workspace / CURRENT_PROJECT_FILE).write_text(stored + "\n", encoding="utf-8")


def resolve_project(project: Path | None = None, workspace: Path | None = None) -> Path:
    workspace = (workspace or Path.cwd()).resolve()
    if project is not None:
        candidate = project if project.is_absolute() else workspace / project
        return candidate.resolve()

    if (workspace / "song.yaml").is_file():
        return workspace

    marker = workspace / CURRENT_PROJECT_FILE
    if marker.is_file():
        stored = Path(marker.read_text(encoding="utf-8").strip())
        return (stored if stored.is_absolute() else workspace / stored).resolve()

    raise FileNotFoundError(
        "No hay un proyecto activo. Ejecuta 'devbeats new NOMBRE' o usa --project."
    )

