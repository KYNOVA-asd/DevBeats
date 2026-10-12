"""Arreglos MIDI sencillos a partir de letra y acordes."""

import math
import random
import re

from devbeats.core.chord_parser import ChordSheet
from devbeats.core.models import Metadata, Note, Song, Track

PITCH_CLASS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,
               "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8,
               "A": 9, "A#": 10, "Bb": 10, "B": 11}
SHARP_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def _midi_to_pitch(number: int) -> str:
    return f"{SHARP_NAMES[number % 12]}{number // 12 - 1}"


def _chord_midis(symbol: str) -> tuple[list[int], int]:
    match = re.match(r"^([A-G](?:#|b)?)(.*)$", symbol)
    if not match:
        raise ValueError(f"Acorde no soportado: {symbol}")
    root_name, quality = match.groups()
    root = 48 + PITCH_CLASS[root_name]
    if quality.startswith("m") and not quality.startswith("maj"):
        intervals = [0, 3, 7]
    elif quality.startswith("dim"):
        intervals = [0, 3, 6]
    elif quality.startswith("sus4"):
        intervals = [0, 5, 7]
    elif quality.startswith("sus2"):
        intervals = [0, 2, 7]
    elif quality.startswith("7"):
        intervals = [0, 4, 7, 10]
    else:
        intervals = [0, 4, 7]
    return [root + interval for interval in intervals], root - 12


def arrange_chord_sheet(sheet: ChordSheet, title: str, tempo: int = 72, seed: int = 42) -> Song:
    chords: list[Note] = []
    bass: list[Note] = []
    guide: list[Note] = []
    rng = random.Random(seed)
    minor_scale = ("D4", "F4", "G4", "A4", "C5", "D5")
    for phrase in sheet.phrases:
        for placement in phrase.chords:
            chord_midis, bass_midi = _chord_midis(placement.symbol)
            # Un pequeno desfase ascendente imita el ataque de un rasgueo.
            for string_index, midi_note in enumerate(chord_midis):
                strum_delay = string_index * 0.035
                chords.append(Note(
                    pitch=_midi_to_pitch(midi_note),
                    start=round(placement.start + strum_delay, 4),
                    duration=max(0.25, placement.duration - 0.12 - strum_delay),
                    velocity=max(38, 54 - string_index * 3),
                ))
            bass.append(Note(pitch=_midi_to_pitch(bass_midi), start=placement.start,
                             duration=max(0.25, placement.duration - 0.1), velocity=54))
        if phrase.text:
            words = len(re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]+", phrase.text))
            count = min(8, max(2, words))
            step = phrase.duration / count
            previous = 0
            for index in range(count):
                options = [i for i in range(len(minor_scale)) if abs(i - previous) <= 2]
                chosen = rng.choice(options)
                previous = chosen
                guide.append(Note(pitch=minor_scale[chosen], start=round(phrase.start + index * step, 4),
                                  duration=round(step * 0.82, 4), velocity=66))
    return Song(
        metadata=Metadata(title=title, description="Arreglo creado desde letra y acordes"),
        tempo=tempo, key=sheet.key, bars=max(1, math.ceil(sheet.total_beats / 4)), seed=seed,
        tracks=[
            Track(name="Melodia guia", instrument="flute", program=73, channel=0, notes=guide),
            # Programa General MIDI 24 (base cero): Acoustic Guitar (nylon).
            Track(name="Guitarra", instrument="acoustic_guitar_nylon", program=24, channel=1, notes=chords),
            Track(name="Bajo", instrument="acoustic_bass", program=32, channel=2, notes=bass),
        ],
    )

