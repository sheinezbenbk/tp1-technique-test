"""Tests unitaires de la conversion binaire."""

import random
import struct

import pytest

from triangulator.binary import decode_pointset, encode_pointset, encode_triangles


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


def test_decode_header_too_short():
    """Décodage de moins de 4 octets : une ValueError est attendue."""
    with pytest.raises(ValueError):
        decode_pointset(b"\x01\x00")


def test_decode_truncated_points():
    """Décodage avec N=2 annoncé mais un seul point fourni : ValueError."""
    data = struct.pack("<I", 2) + struct.pack("<ff", 1.0, 2.0)
    with pytest.raises(ValueError):
        decode_pointset(data)


def test_encode_empty_pointset():
    """Encodage d'une liste vide : uniquement 4 octets à zéro."""
    assert encode_pointset([]) == struct.pack("<I", 0)


def test_encode_two_points():
    """Encodage de deux points connus vers les octets attendus."""
    expected = (
        struct.pack("<I", 2)
        + struct.pack("<ff", 1.0, 2.0)
        + struct.pack("<ff", 3.5, -4.0)
    )
    assert encode_pointset([(1.0, 2.0), (3.5, -4.0)]) == expected


def test_encode_triangles_one_triangle():
    """Encodage d'un triangle : sommets, nombre de triangles, puis indices."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    expected = (
        struct.pack("<I", 3)
        + struct.pack("<ff", 0.0, 0.0)
        + struct.pack("<ff", 1.0, 0.0)
        + struct.pack("<ff", 0.0, 1.0)
        + struct.pack("<I", 1)
        + struct.pack("<III", 0, 1, 2)
    )
    assert encode_triangles(points, [(0, 1, 2)]) == expected


@pytest.mark.parametrize("size", [0, 1, 2, 10, 500])
def test_roundtrip_decode_encode(size):
    """Décoder ce qu'on vient d'encoder redonne les points de départ."""
    rng = random.Random(42)
    # Des multiples de 0.25 sont représentables exactement en float 32 bits.
    points = [
        (rng.randint(-4000, 4000) / 4, rng.randint(-4000, 4000) / 4)
        for _ in range(size)
    ]
    assert decode_pointset(encode_pointset(points)) == points