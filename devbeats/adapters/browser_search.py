"""Entrega consultas al navegador; no extrae ni raspa resultados de Google."""

import os
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import urlencode

from devbeats.core.profile import BrowserSearchProfile


class BrowserLaunchError(RuntimeError):
    """No fue posible entregar la consulta a un navegador."""


def build_search_url(query: str, profile: BrowserSearchProfile) -> str:
    clean_query = query.strip()
    if not clean_query:
        raise ValueError("La busqueda no puede estar vacia")
    parameters = {
        profile.query_parameter: clean_query,
        "hl": profile.language,
        "gl": profile.country,
        **profile.extra_parameters,
    }
    return f"{str(profile.base_url).rstrip('?')}?{urlencode(parameters)}"


def _edge_candidates() -> list[Path]:
    candidates: list[Path] = []
    for variable in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA"):
        root = os.getenv(variable)
        if root:
            candidates.append(Path(root) / "Microsoft" / "Edge" / "Application" / "msedge.exe")
    return candidates


def open_search(query: str, profile: BrowserSearchProfile) -> str:
    if not profile.enabled:
        raise BrowserLaunchError("La busqueda web esta desactivada en el perfil")
    url = build_search_url(query, profile)

    if profile.browser == "edge":
        edge = next((candidate for candidate in _edge_candidates() if candidate.is_file()), None)
        if edge is not None:
            subprocess.Popen([str(edge), url], close_fds=True)
            return url

    if not webbrowser.open_new_tab(url):
        raise BrowserLaunchError("Windows no pudo abrir el navegador predeterminado")
    return url

