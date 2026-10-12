"""Constructor XML experimental para proyectos LMMS sin comprimir (.mmp)."""

from pathlib import Path
from xml.etree import ElementTree as ET

from devbeats.core.models import Song
from devbeats.core.music_theory import note_to_midi

LMMS_TICKS_PER_BEAT = 48


def export_lmms_project(song: Song, destination: str | Path) -> Path:
    """Crea un MMP minimo; MIDI sigue siendo la ruta recomendada del MVP."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    root = ET.Element("lmms-project", {"version": "1.0", "type": "song", "creator": "DevBeats"})
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "bpm", {"value": str(song.tempo)})
    ET.SubElement(head, "timesig_numerator", {"value": "4"})
    ET.SubElement(head, "timesig_denominator", {"value": "4"})
    song_node = ET.SubElement(root, "song")
    track_container = ET.SubElement(song_node, "trackcontainer", {"type": "song"})

    for source in song.tracks:
        track = ET.SubElement(track_container, "track", {"name": source.name, "type": "0", "muted": "0", "solo": "0"})
        pattern = ET.SubElement(track, "pattern", {"name": source.name, "pos": "0", "muted": "0", "steps": "16"})
        for note in source.notes:
            ET.SubElement(
                pattern,
                "note",
                {
                    "key": str(note_to_midi(note.pitch) - 12),
                    "pos": str(round(note.start * LMMS_TICKS_PER_BEAT)),
                    "len": str(max(1, round(note.duration * LMMS_TICKS_PER_BEAT))),
                    "vol": str(round(note.velocity * 100 / 127)),
                    "pan": "0",
                },
            )

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)
    return destination.resolve()

