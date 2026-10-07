"""Conversion entre la représentation binaire et les objets Python.

Format Pointset : 4 octets (unsigned long) pour le nombre de points N,
puis N fois 8 octets (float X, float Y).

Format Triangles : le format PointSet, puis 4 octets pour le nombre 
de triangles T puis T fois 12 octets (3 indices, unsigned long chacun).
"""

def decode_pointset(data: bytes) -> list[tuple[float, float]]: 
    """Décodage d'un PointSet binaire en liste de points (x, y)."""
    raise NotImplementedError

def encode_pointset(points: list[tuple[float, float]]) -> bytes:
    """Encodage d'une liste de points (x, y) en PointSet binaire."""
    raise NotImplementedError

def encode_triangles(
        points: list[tuple[float, float]], 
        triangles: list[tuple[int, int, int]],
) -> bytes:
    """Encodage de points et de triangles au format binaire Triangles."""
    raise NotImplementedError
