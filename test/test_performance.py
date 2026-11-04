"""Tests de performance, lents et exclus de make unit_test."""

import random
import statistics
import struct
import time

import pytest

from triangulator.algorithm import triangulate
from triangulator.binary import decode_pointset, encode_pointset, encode_triangles

# Étiquette appliquée à tous les tests de ce fichier.
pytestmark = pytest.mark.performance

REPEAT = 5


def _random_points(count):
    """Points aléatoires reproductibles grâce à une graine fixe."""
    rng = random.Random(42)
    return [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(count)]


def _pointset_bytes(points):
    """Octets d'un PointSet, fabriqués à la main selon le format de l'énoncé."""
    body = struct.pack("<I", len(points))
    for x, y in points:
        body += struct.pack("<ff", x, y)
    return body


def _fan_triangles(count):
    """Triangles en éventail autour du point 0, pour tester l'encodage."""
    return [(0, i, i + 1) for i in range(1, count - 1)]


def _median_time(func):
    """Médiane du temps d'exécution de func sur plusieurs essais, en secondes."""
    durations = []
    for _ in range(REPEAT):
        start = time.perf_counter()
        func()
        durations.append(time.perf_counter() - start)
    return statistics.median(durations)


@pytest.mark.parametrize("count", [100, 10_000])
def test_decode_pointset_speed(count):
    """Mesure du décodage d'un PointSet de 100 puis 10 000 points."""
    data = _pointset_bytes(_random_points(count))
    duration = _median_time(lambda: decode_pointset(data))
    print(f"decode {count} points : {duration:.4f} s")
    assert duration < 1.0


@pytest.mark.parametrize("count", [100, 10_000])
def test_encode_pointset_speed(count):
    """Mesure de l'encodage d'un PointSet de 100 puis 10 000 points."""
    points = _random_points(count)
    duration = _median_time(lambda: encode_pointset(points))
    print(f"encode {count} points : {duration:.4f} s")
    assert duration < 1.0


@pytest.mark.parametrize("count", [100, 10_000])
def test_encode_triangles_speed(count):
    """Mesure de l'encodage de triangles pour 100 puis 10 000 points."""
    points = _random_points(count)
    triangles = _fan_triangles(count)
    duration = _median_time(lambda: encode_triangles(points, triangles))
    print(f"encode {len(triangles)} triangles : {duration:.4f} s")
    assert duration < 1.0


@pytest.mark.parametrize("count", [100, 500, 1000])
def test_triangulate_speed(count):
    """Mesure de la triangulation en fonction du nombre de points N."""
    points = _random_points(count)
    duration = _median_time(lambda: triangulate(points))
    print(f"triangulate {count} points : {duration:.4f} s")
    assert duration < 10.0