"""Generador determinista de melodias y acordes de cuna."""

import random

from devbeats.core.models import Note, Song, Track
from devbeats.core.music_theory import C_MAJOR_PENTATONIC, lullaby_chords


def _human_value(rng: random.Random, amount: float, enabled: bool) -> float:
    return rng.uniform(-amount, amount) if enabled else 0.0


def generate_lullaby(song: Song) -> Song:
    """Crea pistas de melodia y acordes sin mutar la configuracion recibida."""
    rng = random.Random(song.seed)
    melody_notes: list[Note] = []
    chord_notes: list[Note] = []
    previous_index = 0

    for bar, (_, chord) in enumerate(lullaby_chords(song.bars)):
        bar_start = bar * 4.0
        for pitch in chord:
            chord_notes.append(Note(pitch=pitch, start=bar_start, duration=3.85, velocity=42))

        # Cuatro negras suaves por compas. El movimiento limitado evita saltos bruscos.
        for beat in range(4):
            candidates = [
                index
                for index in range(len(C_MAJOR_PENTATONIC))
                if abs(index - previous_index) <= 2
            ]
            if beat == 0 and bar % 4 == 0:
                note_index = 0
            else:
                note_index = rng.choice(candidates)
            previous_index = note_index
            timing = _human_value(rng, 0.025, song.humanize)
            start = max(bar_start, bar_start + beat + timing)
            velocity = round(66 + _human_value(rng, 8, song.humanize))
            duration = 0.86 + _human_value(rng, 0.04, song.humanize)
            melody_notes.append(
                Note(
                    pitch=C_MAJOR_PENTATONIC[note_index],
                    start=round(start, 4),
                    duration=round(duration, 4),
                    velocity=max(45, min(85, velocity)),
                )
            )

    generated_tracks = [
        Track(name="Melodia", instrument="music_box", program=10, channel=0, notes=melody_notes),
        Track(name="Acordes", instrument="warm_pad", program=89, channel=1, notes=chord_notes),
    ]
    return song.model_copy(update={"tracks": generated_tracks}, deep=True)

