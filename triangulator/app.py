"""Application Flask du Triangulator."""

import os
import uuid

from flask import Flask, Response, jsonify

from triangulator.algorithm import triangulate
from triangulator.binary import decode_pointset, encode_triangles
from triangulator.pointset_client import (
    PointSetClient,
    PointSetManagerUnavailableError,
    PointSetNotFoundError,
)


def _error(status, code, message):
    """Réponse JSON d'erreur au format {code, message}."""
    response = jsonify({"code": code, "message": message})
    response.status_code = status
    return response


def _is_valid_uuid(value):
    """Vérification qu'un texte est un UUID écrit avec des tirets."""
    try:
        return str(uuid.UUID(value)) == value.lower()
    except ValueError:
        return False


def create_app(pointset_client) -> Flask:
    """Création de l'application Flask.

    `pointset_client` est injecté : en production c'est un vrai
    PointSetClient, dans les tests c'est un faux client (stub).
    """
    app = Flask(__name__)

    @app.get("/triangulation/<pointset_id>")
    def get_triangulation(pointset_id):
        """Route de triangulation d'un PointSet identifié par son UUID."""
        if not _is_valid_uuid(pointset_id):
            return _error(400, "INVALID_ID", "L'identifiant n'est pas un UUID.")
        try:
            data = pointset_client.get_pointset(pointset_id)
        except PointSetNotFoundError:
            return _error(404, "NOT_FOUND", "PointSet introuvable.")
        except PointSetManagerUnavailableError:
            return _error(503, "MANAGER_UNAVAILABLE", "PointSetManager injoignable.")
        try:
            points = decode_pointset(data)
            body = encode_triangles(points, triangulate(points))
        except Exception:
            return _error(500, "TRIANGULATION_FAILED", "Triangulation impossible.")
        return Response(body, status=200, mimetype="application/octet-stream")

    return app


def main() -> None:  # pragma: no cover
    """Lancement du serveur de développement."""
    manager_url = os.environ.get("POINTSET_MANAGER_URL", "http://localhost:5001")
    create_app(PointSetClient(manager_url)).run(port=5000)


if __name__ == "__main__":  # pragma: no cover
    main()