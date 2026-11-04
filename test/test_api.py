"""Tests de l'API HTTP du Triangulator, avec un faux PointSetManager."""

import struct

import pytest

from triangulator.app import create_app
from triangulator.pointset_client import (
    PointSetManagerUnavailableError,
    PointSetNotFoundError,
)

VALID_ID = "123e4567-e89b-12d3-a456-426614174000"
TRIANGLE = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]


class StubClient:
    """Faux client du PointSetManager : répond ce qu'on lui demande."""

    def __init__(self, data=None, error=None):
        """Crée le stub avec des octets à renvoyer ou une erreur à lever."""
        self.data = data
        self.error = error
        self.calls = [] 

    def get_pointset(self, pointset_id):
        """Réponse programmée, avec mémorisation des identifiants demandés."""
        self.calls.append(pointset_id)
        if self.error is not None:
            raise self.error
        return self.data


def _pointset_bytes(points):
    """Octets d'un PointSet, fabriqués à la main selon le format de l'énoncé."""
    body = struct.pack("<I", len(points))
    for x, y in points:
        body += struct.pack("<ff", x, y)
    return body


def _parse_triangles(body):
    """Lecture du format Triangles : renvoie les sommets et les triangles."""
    (n,) = struct.unpack_from("<I", body, 0)
    offset = 4
    points = [struct.unpack_from("<ff", body, offset + 8 * i) for i in range(n)]
    offset += 8 * n
    (t,) = struct.unpack_from("<I", body, offset)
    offset += 4
    triangles = [struct.unpack_from("<III", body, offset + 12 * i) for i in range(t)]
    assert len(body) == offset + 12 * t
    return points, triangles


def _client_for(stub):
    """Client de test Flask branché sur le stub."""
    return create_app(stub).test_client()


def _assert_error(response, status):
    """Vérifie le code HTTP et le corps JSON {code, message} d'une erreur."""
    assert response.status_code == status
    assert response.mimetype == "application/json"
    body = response.get_json()
    assert isinstance(body["code"], str)
    assert isinstance(body["message"], str)


def test_success_returns_200_and_octet_stream():
    """Un PointSet valide donne un 200 au format binaire."""
    client = _client_for(StubClient(data=_pointset_bytes(TRIANGLE)))
    response = client.get(f"/triangulation/{VALID_ID}")
    assert response.status_code == 200
    assert response.mimetype == "application/octet-stream"


def test_success_three_points_give_one_triangle():
    """Trois points donnent un triangle dont les indices sont valides."""
    client = _client_for(StubClient(data=_pointset_bytes(TRIANGLE)))
    response = client.get(f"/triangulation/{VALID_ID}")
    _, triangles = _parse_triangles(response.data)
    assert len(triangles) == 1
    assert set(triangles[0]) == {0, 1, 2}


def test_success_square_gives_two_triangles():
    """Un carré donne deux triangles."""
    client = _client_for(StubClient(data=_pointset_bytes(SQUARE)))
    response = client.get(f"/triangulation/{VALID_ID}")
    _, triangles = _parse_triangles(response.data)
    assert len(triangles) == 2


def test_success_returns_input_vertices_unchanged():
    """La première partie de la réponse reprend les sommets reçus."""
    client = _client_for(StubClient(data=_pointset_bytes(SQUARE)))
    response = client.get(f"/triangulation/{VALID_ID}")
    points, _ = _parse_triangles(response.data)
    assert points == SQUARE


def test_success_empty_pointset():
    """Un PointSet vide donne un 200 sans sommet ni triangle."""
    client = _client_for(StubClient(data=_pointset_bytes([])))
    response = client.get(f"/triangulation/{VALID_ID}")
    assert response.status_code == 200
    assert _parse_triangles(response.data) == ([], [])


def test_manager_is_asked_for_the_requested_id():
    """Le PointSetManager est interrogé une fois, avec l'identifiant de l'URL."""
    stub = StubClient(data=_pointset_bytes(TRIANGLE))
    _client_for(stub).get(f"/triangulation/{VALID_ID}")
    assert stub.calls == [VALID_ID]


@pytest.mark.parametrize(
    "bad_id",
    [
        "not-a-uuid",
        "123",
        "123e4567-e89b-12d3-a456-42661417400",
        "zzzzzzzz-e89b-12d3-a456-426614174000",
    ],
)
def test_invalid_id_returns_400(bad_id):
    """Un identifiant qui n'est pas un UUID donne un 400 en JSON."""
    client = _client_for(StubClient(data=_pointset_bytes(TRIANGLE)))
    _assert_error(client.get(f"/triangulation/{bad_id}"), 400)


def test_invalid_id_does_not_call_manager():
    """Un identifiant invalide est refusé sans interroger le PointSetManager."""
    stub = StubClient(data=_pointset_bytes(TRIANGLE))
    _client_for(stub).get("/triangulation/not-a-uuid")
    assert stub.calls == []


def test_unknown_pointset_returns_404():
    """Si le PointSetManager ne connaît pas l'identifiant, réponse 404."""
    client = _client_for(StubClient(error=PointSetNotFoundError()))
    _assert_error(client.get(f"/triangulation/{VALID_ID}"), 404)


def test_manager_unavailable_returns_503():
    """Si le PointSetManager est injoignable, réponse 503."""
    client = _client_for(StubClient(error=PointSetManagerUnavailableError()))
    _assert_error(client.get(f"/triangulation/{VALID_ID}"), 503)


def test_corrupted_pointset_returns_500():
    """Des octets illisibles reçus du PointSetManager donnent un 500."""
    corrupted = struct.pack("<I", 5)  # annonce 5 points, n'en fournit aucun
    client = _client_for(StubClient(data=corrupted))
    _assert_error(client.get(f"/triangulation/{VALID_ID}"), 500)


def test_triangulation_failure_returns_500(monkeypatch):
    """Si l'algorithme plante, réponse 500 plutôt qu'un crash du serveur."""
    client = _client_for(StubClient(data=_pointset_bytes(TRIANGLE)))

    def explode(points):
        raise RuntimeError("boom")

    monkeypatch.setattr("triangulator.app.triangulate", explode)
    _assert_error(client.get(f"/triangulation/{VALID_ID}"), 500)


def test_post_is_not_allowed():
    """La route n'accepte que GET : un POST donne un 405."""
    client = _client_for(StubClient(data=_pointset_bytes(TRIANGLE)))
    assert client.post(f"/triangulation/{VALID_ID}").status_code == 405