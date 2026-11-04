"""Tests de l'algorithme de triangulation."""

import math
import random

import pytest

from triangulator.algorithm import triangulate


def _area(points, triangle):
    """Aire d'un triangle donné par les indices de ses trois sommets."""
    (ax, ay), (bx, by), (cx, cy) = (points[i] for i in triangle)
    return abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2


def _regular_polygon(n):
    """Sommets d'un polygone régulier à n côtés, inscrit dans un cercle de rayon 1."""
    return [
        (math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n))
        for k in range(n)
    ]


def _random_points(seed, count=20):
    """Points aléatoires reproductibles grâce à une graine fixe."""
    rng = random.Random(seed)
    return [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(count)]


def test_three_points_give_one_triangle():
    """Trois points non alignés donnent un seul triangle."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangles = triangulate(points)
    assert len(triangles) == 1
    assert set(triangles[0]) == {0, 1, 2}


def test_square_gives_two_triangles():
    """Un carré donne deux triangles dont l'aire totale vaut celle du carré."""
    points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    triangles = triangulate(points)
    assert len(triangles) == 2
    assert sum(_area(points, t) for t in triangles) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "points",
    [[], [(0.0, 0.0)], [(0.0, 0.0), (1.0, 1.0)]],
)
def test_fewer_than_three_points_give_no_triangle(points):
    """Moins de trois points ne peuvent former aucun triangle."""
    assert triangulate(points) == []


def test_collinear_points_give_no_triangle():
    """Des points alignés ne forment aucun triangle."""
    points = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]
    assert triangulate(points) == []


@pytest.mark.parametrize("n", [3, 4, 5, 8, 12])
def test_regular_polygon_triangle_count(n):
    """Un polygone convexe à n sommets se découpe en n - 2 triangles."""
    assert len(triangulate(_regular_polygon(n))) == n - 2


@pytest.mark.parametrize("n", [3, 4, 5, 8, 12])
def test_regular_polygon_total_area(n):
    """La somme des aires des triangles égale l'aire du polygone."""
    points = _regular_polygon(n)
    expected = 0.5 * n * math.sin(2 * math.pi / n)
    total = sum(_area(points, t) for t in triangulate(points))
    assert total == pytest.approx(expected)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_all_indices_are_valid(seed):
    """Tous les indices des triangles désignent un point existant."""
    points = _random_points(seed)
    for triangle in triangulate(points):
        assert len(set(triangle)) == 3
        assert all(0 <= i < len(points) for i in triangle)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_no_triangle_has_zero_area(seed):
    """Aucun triangle ne doit être dégénéré, c'est-à-dire d'aire nulle."""
    points = _random_points(seed)
    for triangle in triangulate(points):
        assert _area(points, triangle) > 0


def test_duplicate_points_give_no_degenerate_triangle():
    """Des points en double ne doivent pas produire de triangle d'aire nulle."""
    points = [(0.0, 0.0), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    for triangle in triangulate(points):
        assert _area(points, triangle) > 0

def test_collinear_prefix_then_apex_and_extra_point():
    """Des points alignés au début, puis deux autres points, restent couverts."""
    points = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 1.0), (4.0, 0.0)]
    triangles = triangulate(points)
    assert len(triangles) == 3
    assert sum(_area(points, t) for t in triangles) == pytest.approx(2.0)


def test_third_point_on_the_right_side():
    """Un troisième point situé à droite du premier segment donne un triangle."""
    points = [(0.0, 0.0), (1.0, 0.0), (2.0, -1.0)]
    assert len(triangulate(points)) == 1