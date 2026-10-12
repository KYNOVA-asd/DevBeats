"""Adaptador de Gemini para la futura capa de direccion musical."""

import os
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from devbeats.core.models import SongPlan


class GeminiConfigurationError(ValueError):
    """La configuracion del proveedor no es valida."""


@dataclass(slots=True)
class GeminiSupervisor:
    api_key: str
    model: str
    search_grounded: bool = False

    @classmethod
    def from_environment(cls, env_file: str | Path | None = None) -> "GeminiSupervisor":
        load_dotenv(dotenv_path=env_file, override=False)
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
        if not api_key or api_key == "pega_aqui_tu_api_key":
            raise GeminiConfigurationError("Configura GEMINI_API_KEY en el archivo .env")
        if not model:
            raise GeminiConfigurationError("GEMINI_MODEL no puede estar vacio")
        return cls(api_key=api_key, model=model)

    def test_connection(self) -> str:
        """Realiza una peticion corta, adecuada para diagnostico."""
        client = genai.Client(api_key=self.api_key)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = client.interactions.create(
                    model=self.model,
                    input=(
                        "Eres el director musical de DevBeats. Responde en una sola frase "
                        "breve en espanol confirmando que puedes revisar una cancion de cuna."
                    ),
                )
                break
            except Exception as exc:  # El SDK expone distintos errores HTTP por version.
                last_error = exc
                error_text = str(exc)
                is_temporary = any(code in error_text for code in ("500", "503", "INTERNAL", "UNAVAILABLE"))
                if not is_temporary or attempt == 2:
                    raise RuntimeError(f"La peticion fallo tras {attempt + 1} intento(s): {exc}") from exc
                time.sleep(attempt + 1)
        else:  # pragma: no cover - proteccion defensiva
            raise RuntimeError(f"La peticion fallo: {last_error}")
        text = (response.output_text or "").strip()
        if not text:
            raise RuntimeError("Gemini respondio sin contenido de texto")
        return text

    def plan_song(self, request: str, use_google_search: bool = True) -> SongPlan:
        """Investiga rasgos generales y devuelve un plan original validado."""
        clean_request = request.strip()
        if not clean_request:
            raise ValueError("La peticion musical no puede estar vacia")

        prompt = f"""
Actua como director musical de DevBeats. Investiga solo si aporta valor y crea
un plan para una cancion de cuna ORIGINAL en Do mayor, compas 4/4 y destinada
a un bebe. No copies melodias, letras ni progresiones distintivas protegidas.
Peticion del usuario: {clean_request}

Devuelve exclusivamente un objeto JSON valido, sin Markdown, con estas claves:
title (texto corto), description (texto), tempo (entero 50-90), bars (entero
4-32), seed (entero positivo), mood (texto corto), research_summary (texto que
explique rasgos generales usados, sin reproducir material protegido).
""".strip()

        tools = [{"type": "google_search"}] if use_google_search else None
        try:
            response = self._interaction(prompt, tools=tools)
            self.search_grounded = bool(tools)
        except RuntimeError as exc:
            if not tools or "429" not in str(exc):
                raise
            # La composicion no se bloquea si el proyecto no tiene cuota de Search.
            response = self._interaction(prompt, tools=None)
            self.search_grounded = False
        raw = (response.output_text or "").strip()
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise RuntimeError("Gemini no devolvio un plan JSON reconocible")
        try:
            return SongPlan.model_validate(json.loads(match.group(0)))
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(f"El plan de Gemini no es valido: {exc}") from exc

    def _interaction(self, prompt: str, tools: list[dict[str, str]] | None = None):
        """Ejecuta una interaccion con reintentos para fallos temporales."""
        client = genai.Client(api_key=self.api_key)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                kwargs = {"model": self.model, "input": prompt}
                if tools:
                    kwargs["tools"] = tools
                return client.interactions.create(**kwargs)
            except Exception as exc:
                last_error = exc
                error_text = str(exc)
                is_temporary = any(code in error_text for code in ("500", "503", "INTERNAL", "UNAVAILABLE"))
                if not is_temporary or attempt == 2:
                    raise RuntimeError(f"La peticion fallo tras {attempt + 1} intento(s): {exc}") from exc
                time.sleep(attempt + 1)
        raise RuntimeError(f"La peticion fallo: {last_error}")

