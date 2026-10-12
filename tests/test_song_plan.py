from devbeats.core.models import SongPlan
from devbeats.cli.commands_ai import _safe_folder_name


def test_song_plan_validation() -> None:
    plan = SongPlan(
        title="Luna suave",
        description="Cancion original para dormir.",
        tempo=64,
        bars=8,
        seed=12,
        mood="calmado",
    )
    assert plan.tempo == 64
    assert plan.bars == 8


def test_safe_folder_name_removes_accents_without_losing_letters() -> None:
    assert _safe_folder_name("Sueño Estelar") == "sueno-estelar"
    assert _safe_folder_name("Canción para Bebé") == "cancion-para-bebe"
