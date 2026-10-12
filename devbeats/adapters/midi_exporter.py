"""Exportacion del modelo de dominio a Standard MIDI File."""

from pathlib import Path

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from devbeats.core.models import Song
from devbeats.core.music_theory import note_to_midi

TICKS_PER_BEAT = 480


def _ticks(beats: float) -> int:
    return max(0, round(beats * TICKS_PER_BEAT))


def export_midi(song: Song, destination: str | Path) -> Path:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    midi = MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)

    conductor = MidiTrack()
    midi.tracks.append(conductor)
    conductor.append(MetaMessage("track_name", name=song.metadata.title, time=0))
    conductor.append(MetaMessage("set_tempo", tempo=bpm2tempo(song.tempo), time=0))
    conductor.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    conductor.append(MetaMessage("end_of_track", time=0))

    for source in song.tracks:
        track = MidiTrack()
        midi.tracks.append(track)
        track.append(MetaMessage("track_name", name=source.name, time=0))
        track.append(Message("program_change", channel=source.channel, program=source.program, time=0))

        # prioridad 0 apaga una nota antes de encender otra en el mismo tick.
        events: list[tuple[int, int, Message]] = []
        for note in source.notes:
            number = note_to_midi(note.pitch)
            start = _ticks(note.start)
            end = _ticks(note.start + note.duration)
            events.append((start, 1, Message("note_on", channel=source.channel, note=number, velocity=note.velocity)))
            events.append((end, 0, Message("note_off", channel=source.channel, note=number, velocity=0)))

        previous_tick = 0
        for absolute_tick, _, message in sorted(events, key=lambda item: (item[0], item[1])):
            message.time = absolute_tick - previous_tick
            previous_tick = absolute_tick
            track.append(message)
        track.append(MetaMessage("end_of_track", time=0))

    midi.save(destination)
    return destination.resolve()

