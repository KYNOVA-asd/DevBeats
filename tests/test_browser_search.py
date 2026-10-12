from devbeats.adapters.browser_search import build_search_url
from devbeats.core.profile import BrowserSearchProfile


def test_build_google_ai_search_url() -> None:
    url = build_search_url("cancion de cuna", BrowserSearchProfile())
    assert "q=cancion+de+cuna" in url
    assert "udm=50" in url
    assert "hl=es" in url
    assert "gl=MX" in url

