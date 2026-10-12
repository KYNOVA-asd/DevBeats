"""Analizador de cancioneros sencillos con acordes sobre la letra."""

import re
from dataclasses import dataclass, field

CHORD_RE = re.compile(
    r"^[A-G](?:#|b)?(?:m|maj|min|dim|sus|add)?(?:2|4|5|6|7|9|11|13)?(?:°)?(?:/[A-G](?:#|b)?)?$",
    re.IGNORECASE,
)


@dataclass(slots=True)
class ChordPlacement:
    symbol: str
    start: float
    duration: float


@dataclass(slots=True)
class LyricPhrase:
    text: str
    section: str
    start: float
    duration: float
    chords: list[ChordPlacement] = field(default_factory=list)


@dataclass(slots=True)
class ChordSheet:
    key: str
    phrases: list[LyricPhrase]

    @property
    def total_beats(self) -> float:
        return max((phrase.start + phrase.duration for phrase in self.phrases), default=0.0)


def normalize_chord(symbol: str) -> str:
    value = symbol.strip()
    if value.endswith("°"):
        return value[:-1] + "dim"
    if re.fullmatch(r"[A-G](?:#|b)?4", value, re.IGNORECASE):
        return value[:-1] + "sus4"
    return value


def _chords_in_line(line: str) -> list[str]:
    tokens = line.split()
    if not tokens or not all(CHORD_RE.fullmatch(token) for token in tokens):
        return []
    return [normalize_chord(token) for token in tokens]


def parse_chord_sheet(text: str) -> ChordSheet:
    lines = text.replace("\r\n", "\n").split("\n")
    key = "C"
    section = "Cancion"
    phrases: list[LyricPhrase] = []
    beat = 0.0
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line or line.startswith("#"):
            continue
        tone_match = re.match(r"^(?:tono|key)\s*:\s*([A-G](?:#|b)?m?)$", line, re.IGNORECASE)
        if tone_match:
            key = tone_match.group(1)
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip() or section
            continue
        chords = _chords_in_line(line)
        if chords:
            lyric = ""
            lookahead = index
            while lookahead < len(lines) and not lines[lookahead].strip():
                lookahead += 1
            if lookahead < len(lines):
                candidate = lines[lookahead].strip()
                if not candidate.startswith("[") and not re.match(
                    r"^(?:tono|key)\s*:", candidate, re.IGNORECASE
                ) and not _chords_in_line(candidate):
                    lyric = candidate
                    index = lookahead + 1
            step = 4.0 / len(chords)
            placements = [
                ChordPlacement(symbol=symbol, start=beat + chord_index * step, duration=step)
                for chord_index, symbol in enumerate(chords)
            ]
            phrases.append(LyricPhrase(lyric, section, beat, 4.0, placements))
            beat += 4.0
            continue
        previous = phrases[-1].chords[-1].symbol if phrases and phrases[-1].chords else key
        phrases.append(
            LyricPhrase(line, section, beat, 4.0, [ChordPlacement(previous, beat, 4.0)])
        )
        beat += 4.0
    if not phrases:
        raise ValueError("El cancionero no contiene acordes o letra reconocibles")
    return ChordSheet(key=key, phrases=phrases)

