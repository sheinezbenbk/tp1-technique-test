"""Conversion entre la représentation binaire et les objets Python.

Format PointSet : 4 octets (unsigned long) pour le nombre de points N,
puis N fois 8 octets (float X, float Y).

Format Triangles : le format PointSet, puis 4 octets pour le nombre de
triangles T, puis T fois 12 octets (3 indices, unsigned long chacun).
Tous les nombres sont en little-endian.
"""

import struct


def decode_pointset(data: bytes) -> list[tuple[float, float]]:
    """Décodage d'un PointSet binaire en liste de points (x, y).

    Lève ValueError si les octets sont trop courts ou de taille incohérente.
    """
    if len(data) < 4:
        raise ValueError("PointSet trop court : en-tête incomplet.")
    (count,) = struct.unpack_from("<I", data, 0)
    if len(data) != 4 + 8 * count:
        raise ValueError(
            "La taille du PointSet ne correspond pas au nombre de points."
        )
    values = struct.unpack_from(f"<{2 * count}f", data, 4)
    return list(zip(values[::2], values[1::2], strict=True))


def encode_pointset(points: list[tuple[float, float]]) -> bytes:
    """Encodage d'une liste de points (x, y) au format binaire PointSet."""
    flat = [coordinate for point in points for coordinate in point]
    return struct.pack(f"<I{len(flat)}f", len(points), *flat)


def encode_triangles(
    points: list[tuple[float, float]],
    triangles: list[tuple[int, int, int]],
) -> bytes:
    """Encodage de points et de triangles au format binaire Triangles."""
    flat = [index for triangle in triangles for index in triangle]
    return encode_pointset(points) + struct.pack(
        f"<I{len(flat)}I", len(triangles), *flat
    )