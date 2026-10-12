from devbeats.core.generator import generate_lullaby
from devbeats.core.models import Metadata, Song


def test_generator_is_deterministic() -> None:
    song = Song(metadata=Metadata(title="Test"), bars=4, seed=7)
    first = generate_lullaby(song)
    second = generate_lullaby(song)
    assert first == second
    assert [track.name for track in first.tracks] == ["Melodia", "Acordes"]
    assert len(first.tracks[0].notes) == 16
    assert len(first.tracks[1].notes) == 12

