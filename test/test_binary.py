"""Tests unitaires de la conversion binaire."""

import struct

from triangulator.binary import decode_pointset


def test_decode_empty_pointset():
    """Décodage d'un PointSet vide : 4 octets à zéro donnent une liste vide."""
    data = struct.pack("<I", 0)
    assert decode_pointset(data) == []


def test_decode_two_points():
    """Décodage d'un PointSet de deux points connus."""
    data = (
        struct.pack("<I", 2)
        + struct.pack("<ff", 1.0, 2.0)
        + struct.pack("<ff", 3.5, -4.0)
    )
    assert decode_pointset(data) == [(1.0, 2.0), (3.5, -4.0)]