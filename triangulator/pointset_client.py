"""Client HTTP vers le PointSetManager."""

from urllib import error, request

TIMEOUT_SECONDS = 5


class PointSetNotFoundError(Exception):
    """Le PointSetManager n'a pas trouvé le PointSet demandé (404)."""


class PointSetManagerUnavailableError(Exception):
    """Le PointSetManager n'est pas disponible (503)."""


class PointSetClient:
    """Client qui récupère des PointSets depuis le PointSetManager."""

    def __init__(self, base_url: str) -> None:
        """Initialise le client PointSetClient."""
        self.base_url = base_url.rstrip("/")

    def get_pointset(self, pointset_id: str) -> bytes:
        """Récupère un PointSet par son ID.

        Lève PointSetNotFoundError si le PointSet n'est pas trouvé et
        PointSetManagerUnavailableError si le service n'est pas disponible.
        """
        url = f"{self.base_url}/pointset/{pointset_id}"
        try:
            with request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
                return response.read()
        except error.HTTPError as exc:
            if exc.code == 404:
                raise PointSetNotFoundError(pointset_id) from exc
            raise PointSetManagerUnavailableError(str(exc)) from exc
        except OSError as exc:
            raise PointSetManagerUnavailableError(str(exc)) from exc