"""Algorithme de triangulation d'un ensemble de points 2D.

Principe : les points distincts sont triés de gauche à droite. Chaque
nouveau point est relié aux côtés de l'enveloppe convexe qu'il voit.
"""


def _cross(o, a, b):
    """Produit vectoriel (a - o) x (b - o) : positif si le virage est à gauche."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _unique_sorted_indices(points):
    """Retourne les indices des points distincts, triés."""
    first_seen = {}
    for index, point in enumerate(points):
        first_seen.setdefault(point, index)
    return sorted(first_seen.values(), key=lambda i: points[i])


def _add_point(points, hull, triangles, new):
    """Ajout d'un point à l'enveloppe, avec les triangles qu'il crée."""
    size = len(hull)
    target = points[new]
    visible = [
        _cross(points[hull[i]], points[hull[(i + 1) % size]], target) < 0
        for i in range(size)
    ]
    if not any(visible):  # pragma: no cover
        return hull
    start = next(i for i in range(size) if visible[i] and not visible[i - 1])
    length = 0
    while visible[(start + length) % size]:
        length += 1
    for step in range(length):
        a = hull[(start + step) % size]
        b = hull[(start + step + 1) % size]
        triangles.append((a, new, b))
    kept = [hull[(start + length + j) % size] for j in range(size - length + 1)]
    return [*kept, new]


def triangulate(points: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    """Triangulation d'un ensemble de points.

    Retourne une liste de triangles. Chaque triangle est un triplet
    d'indices qui référencent des positions dans la liste `points`.
    Les points en double et les points alignés ne créent aucun triangle plat.
    """
    order = _unique_sorted_indices(points)
    if len(order) < 3:
        return []
    first, second = points[order[0]], points[order[1]]
    split = None
    for position in range(2, len(order)):
        if _cross(first, second, points[order[position]]) != 0:
            split = position
            break
    if split is None:
        return []
    apex = order[split]
    prefix = order[:split]
    left = _cross(first, second, points[apex]) > 0
    triangles = []
    for a, b in zip(prefix, prefix[1:], strict=False):
        triangles.append((a, b, apex) if left else (b, a, apex))
    hull = [*prefix, apex] if left else [*reversed(prefix), apex]
    for new in order[split + 1 :]:
        hull = _add_point(points, hull, triangles, new)
    return triangles

