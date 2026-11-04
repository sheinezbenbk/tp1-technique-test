"""Tests du client HTTP du PointSetManager, sans réseau réel."""

from urllib import error

import pytest

from triangulator.pointset_client import (
    PointSetClient,
    PointSetManagerUnavailableError,
    PointSetNotFoundError,
)


class FakeResponse:
    """Fausse réponse HTTP utilisable avec un bloc with."""

    def __init__(self, data):
        """Crée la fausse réponse avec les octets à renvoyer."""
        self.data = data

    def read(self):
        """Octets de la réponse."""
        return self.data

    def __enter__(self):
        """Entrée dans le bloc with."""
        return self

    def __exit__(self, *args):
        """Sortie du bloc with, sans masquer d'erreur."""
        return False


def test_get_pointset_returns_bytes_and_uses_right_url(monkeypatch):
    """Une réponse réussie renvoie les octets, depuis la bonne adresse."""
    urls = []

    def fake_urlopen(url, timeout):
        urls.append(url)
        return FakeResponse(b"abc")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = PointSetClient("http://manager:5001/")
    assert client.get_pointset("some-id") == b"abc"
    assert urls == ["http://manager:5001/pointset/some-id"]


def test_http_404_raises_not_found(monkeypatch):
    """Une réponse 404 du PointSetManager lève PointSetNotFoundError."""

    def fake_urlopen(url, timeout):
        raise error.HTTPError(url, 404, "Not Found", None, None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(PointSetNotFoundError):
        PointSetClient("http://manager").get_pointset("x")


def test_http_503_raises_unavailable(monkeypatch):
    """Une réponse 503 du PointSetManager lève PointSetManagerUnavailableError."""

    def fake_urlopen(url, timeout):
        raise error.HTTPError(url, 503, "Unavailable", None, None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(PointSetManagerUnavailableError):
        PointSetClient("http://manager").get_pointset("x")


@pytest.mark.parametrize("failure", [error.URLError("refused"), TimeoutError()])
def test_network_failure_raises_unavailable(monkeypatch, failure):
    """Un serveur injoignable ou trop lent lève PointSetManagerUnavailableError."""

    def fake_urlopen(url, timeout):
        raise failure

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(PointSetManagerUnavailableError):
        PointSetClient("http://manager").get_pointset("x")