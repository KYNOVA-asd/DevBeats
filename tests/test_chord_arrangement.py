from devbeats.core.arranger import arrange_chord_sheet
from devbeats.core.chord_parser import normalize_chord, parse_chord_sheet


def test_chord_parser_and_arrangement() -> None:
    sheet = parse_chord_sheet(
        """Tono: Dm
[Verso]
Dm A4 Gm A4
Toro, me da pena te suplico perdonar
A4 Dm F#°
La paz llegara
"""
    )
    assert sheet.key == "Dm"
    assert sheet.phrases[0].chords[1].symbol == "Asus4"
    assert sheet.phrases[1].chords[-1].symbol == "F#dim"
    song = arrange_chord_sheet(sheet, "Toro")
    assert song.key == "Dm"
    assert [track.name for track in song.tracks] == ["Melodia guia", "Guitarra", "Bajo"]
    assert song.tracks[1].program == 24
    assert song.tracks[1].notes[1].start > song.tracks[1].notes[0].start
    assert all(track.notes for track in song.tracks)


def test_common_chord_normalization() -> None:
    assert normalize_chord("A4") == "Asus4"
    assert normalize_chord("F#°") == "F#dim"
