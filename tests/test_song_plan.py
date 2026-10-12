from devbeats.core.models import SongPlan


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
