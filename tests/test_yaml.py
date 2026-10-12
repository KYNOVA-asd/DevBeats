from devbeats.core.models import Metadata, Song


def test_yaml_roundtrip(tmp_path) -> None:
    original = Song(metadata=Metadata(title="Cancion"))
    path = original.to_yaml(tmp_path / "song.yaml")
    assert Song.from_yaml(path) == original

