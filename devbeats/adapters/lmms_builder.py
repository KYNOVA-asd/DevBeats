"""Constructor de proyectos reproducibles para LMMS 1.2.x (.mmp)."""

from pathlib import Path
from xml.etree import ElementTree as ET

from devbeats.core.models import Song
from devbeats.core.music_theory import note_to_midi

LMMS_TICKS_PER_BEAT = 48


def _add_synth(instrument_track: ET.Element, track_index: int) -> None:
    """Anade un TripleOscillator integrado que no requiere SoundFont."""
    instrument = ET.SubElement(instrument_track, "instrument", {"name": "tripleoscillator"})
    wave = str(track_index % 3)
    ET.SubElement(instrument, "tripleoscillator", {
        "modalgo1": "2", "modalgo2": "2", "modalgo3": "2",
        "vol0": "70", "vol1": "20", "vol2": "10",
        "wavetype0": wave, "wavetype1": "0", "wavetype2": "0",
        "coarse0": "0", "coarse1": "-12", "coarse2": "-24",
        "pan0": "0", "pan1": "0", "pan2": "0",
        "finel0": "0", "finel1": "0", "finel2": "0",
        "finer0": "0", "finer1": "0", "finer2": "0",
        "phoffset0": "0", "phoffset1": "0", "phoffset2": "0",
        "stphdetun0": "0", "stphdetun1": "0", "stphdetun2": "0",
        "userwavefile0": "", "userwavefile1": "", "userwavefile2": "",
    })
    eldata = ET.SubElement(instrument_track, "eldata", {"fcut": "14000", "fres": "0.5", "ftype": "0", "fwet": "0"})
    envelope = {
        "lshp": "0", "ctlenvamt": "0", "lspd_denominator": "4", "hold": "0.5",
        "pdel": "0", "sustain": "0.5", "amt": "0", "lspd_syncmode": "0",
        "dec": "0.5", "x100": "0", "lspd": "0.1", "latt": "0",
        "userwavefile": "", "rel": "0.1", "lspd_numerator": "4", "att": "0",
        "lpdel": "0", "lamt": "0",
    }
    for tag in ("elvol", "elcut", "elres"):
        ET.SubElement(eldata, tag, envelope)
    ET.SubElement(instrument_track, "chordcreator", {"chordrange": "1", "chord-enabled": "0", "chord": "0"})
    ET.SubElement(instrument_track, "arpeggiator", {
        "arpmiss": "0", "arptime_numerator": "4", "arptime": "100", "arpgate": "100",
        "arpdir": "0", "arpcycle": "0", "arptime_syncmode": "0", "arp": "0",
        "arpskip": "0", "arptime_denominator": "4", "arpmode": "0",
        "arp-enabled": "0", "arprange": "1",
    })
    ET.SubElement(instrument_track, "midiport", {
        "fixedoutputnote": "-1", "outputprogram": "1", "inputchannel": "0",
        "outputchannel": "1", "inputcontroller": "0", "fixedoutputvelocity": "-1",
        "readable": "0", "writable": "0", "outputcontroller": "0",
        "fixedinputvelocity": "-1", "basevelocity": "63",
    })
    ET.SubElement(instrument_track, "fxchain", {"enabled": "0", "numofeffects": "0"})


def export_lmms_project(song: Song, destination: str | Path) -> Path:
    """Crea un MMP con instrumentos internos, listo para pulsar Play."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    root = ET.Element("lmms-project", {
        "version": "1.0", "type": "song", "creator": "DevBeats", "creatorversion": "1.2.2"
    })
    ET.SubElement(root, "head", {
        "timesig_denominator": "4", "mastervol": "100", "bpm": str(song.tempo),
        "masterpitch": "0", "timesig_numerator": "4",
    })
    song_node = ET.SubElement(root, "song")
    track_container = ET.SubElement(song_node, "trackcontainer", {
        "minimized": "0", "y": "5", "width": "900", "type": "song", "x": "5",
        "height": "500", "maximized": "0", "visible": "1",
    })

    for track_index, source in enumerate(song.tracks):
        track = ET.SubElement(track_container, "track", {"name": source.name, "type": "0", "muted": "0", "solo": "0"})
        instrument_track = ET.SubElement(track, "instrumenttrack", {
            "pitch": "0", "fxch": "0", "basenote": "57", "vol": "85",
            "pitchrange": "1", "usemasterpitch": "1", "pan": "0",
        })
        _add_synth(instrument_track, track_index)
        pattern = ET.SubElement(track, "pattern", {
            "name": source.name, "pos": "0", "muted": "0", "steps": "16", "type": "1"
        })
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

    ET.SubElement(song_node, "fxmixer", {
        "minimized": "0", "y": "510", "width": "543", "x": "5", "height": "333",
        "maximized": "0", "visible": "0",
    })
    ET.SubElement(song_node, "ControllerRackView", {
        "minimized": "0", "y": "310", "width": "350", "x": "680", "height": "200",
        "maximized": "0", "visible": "0",
    })
    ET.SubElement(song_node, "pianoroll", {
        "minimized": "0", "y": "5", "width": "860", "x": "5", "height": "480",
        "maximized": "0", "visible": "0",
    })
    ET.SubElement(song_node, "timeline", {
        "lp1pos": str(song.bars * 192), "lpstate": "0", "lp0pos": "0"
    })
    ET.SubElement(song_node, "controllers")

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    xml = ET.tostring(root, encoding="utf-8")
    destination.write_bytes(b'<?xml version="1.0"?>\n<!DOCTYPE lmms-project>\n' + xml)
    return destination.resolve()

