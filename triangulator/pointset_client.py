"""Client HTTP vers le PointSetManager."""


class PointSetNotFoundError(Exception):
    """Le PointSetManager n'a pas trouvé le PointSet demandé (404)."""


class PointSetManagerUnavailableError(Exception):
    """Le PointSetManager n'est pas disponible (503)."""


class PointSetClient:
    """Client qui récupère des PointSets depuis le PointSetManager."""

    def __init__(self, base_url: str) -> None:
        """Initialise le client PointSetClient."""
        self.base_url = base_url

    def get_pointset(self, pointset_id: str) -> bytes:
        """Récupère un PointSet par son ID.

        Lève PointSetNotFoundError si le PointSet n'est pas trouvé et
        PointSetManagerUnavailableError si le service n'est pas disponible.
        """
        raise NotImplementedError