"""Configuracion no secreta del comportamiento local de DevBeats."""

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class BrowserSearchProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    browser: Literal["edge", "default"] = "edge"
    engine: Literal["google_ai"] = "google_ai"
    base_url: HttpUrl = HttpUrl("https://www.google.com/search")
    query_parameter: str = "q"
    extra_parameters: dict[str, str] = Field(default_factory=lambda: {"udm": "50"})
    language: str = "es"
    country: str = "MX"


class DevBeatsProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    browser_search: BrowserSearchProfile = Field(default_factory=BrowserSearchProfile)
    ai_supervisor: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path = "devbeats.profile.yaml") -> "DevBeatsProfile":
        profile_path = Path(path)
        if not profile_path.is_file():
            return cls()
        data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
        return cls.model_validate(data)

