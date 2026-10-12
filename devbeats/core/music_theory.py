"""Primitivas musicales del MVP Lullaby en Do mayor."""

import re

NOTE_TO_SEMITONE = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

C_MAJOR_PENTATONIC = ("C4", "D4", "E4", "G4", "A4", "C5")
LULLABY_PROGRESSION = (
    ("C", ("C3", "E3", "G3")),
    ("G", ("G2", "B2", "D3")),
    ("Am", ("A2", "C3", "E3")),
    ("F", ("F2", "A2", "C3")),
)


def note_to_midi(pitch: str) -> int:
    """Convierte notacion cientifica (C4, F#3) a numero MIDI."""
    match = re.fullmatch(r"([A-G](?:#|b)?)(-?\d)", pitch)
    if not match:
        raise ValueError(f"Nota invalida: {pitch}")
    name, octave_text = match.groups()
    value = (int(octave_text) + 1) * 12 + NOTE_TO_SEMITONE[name]
    if not 0 <= value <= 127:
        raise ValueError(f"Nota fuera del rango MIDI: {pitch}")
    return value


def lullaby_chords(bars: int) -> list[tuple[str, tuple[str, ...]]]:
    """Repite C-G-Am-F hasta completar el numero de compases."""
    return [LULLABY_PROGRESSION[index % len(LULLABY_PROGRESSION)] for index in range(bars)]

