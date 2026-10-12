"""Modelos de dominio y persistencia YAML."""

from pathlib import Path
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Note(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pitch: str = Field(pattern=r"^[A-G](?:#|b)?-?\d$")
    start: float = Field(ge=0, description="Inicio en pulsos.")
    duration: float = Field(gt=0, description="Duracion en pulsos.")
    velocity: int = Field(default=64, ge=1, le=127)


class Track(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    instrument: str = "music_box"
    program: int = Field(default=10, ge=0, le=127)
    channel: int = Field(default=0, ge=0, le=15)
    notes: list[Note] = Field(default_factory=list)


class Metadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    composer: str = "DevBeats"
    description: str = ""


class SongPlan(BaseModel):
    """Plan estructurado producido por un supervisor de IA."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)
    tempo: int = Field(default=68, ge=50, le=90)
    bars: int = Field(default=8, ge=4, le=32)
    seed: int = Field(default=42, ge=0, le=2_147_483_647)
    mood: str = Field(default="dulce", min_length=1, max_length=80)
    research_summary: str = Field(default="", max_length=1000)


class Song(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: Metadata
    tempo: int = Field(default=68, ge=30, le=240)
    key: str = Field(default="C", pattern=r"^[A-G](?:#|b)?m?$")
    time_signature: str = "4/4"
    bars: int = Field(default=8, ge=1, le=128)
    seed: int = 42
    humanize: bool = True
    tracks: list[Track] = Field(default_factory=list)

    @field_validator("time_signature")
    @classmethod
    def valid_time_signature(cls, value: str) -> str:
        if value != "4/4":
            raise ValueError("El MVP soporta unicamente compas 4/4")
        return value

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Song":
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"No existe el archivo de cancion: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls.model_validate(data)

    def to_yaml(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.model_dump(mode="json", exclude_none=True)
        path.write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        return path

