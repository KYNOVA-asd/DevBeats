from devbeats.core.music_theory import lullaby_chords, note_to_midi


def test_note_to_midi() -> None:
    assert note_to_midi("C4") == 60
    assert note_to_midi("A4") == 69


def test_lullaby_progression() -> None:
    assert [name for name, _ in lullaby_chords(5)] == ["C", "G", "Am", "F", "C"]

