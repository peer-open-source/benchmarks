# _shell_0002_patch.py
"""
Shared distorted five-element patch definition for benchmark shell-0002.

This file is imported by both the pytest benchmark and the standalone plotting
script so that the geometry is defined in exactly one place.
"""

from __future__ import annotations

import numpy as np
import xara


SECTION_TAG = 1

E_MOD = 200_000.0
NU = 0.25
THICKNESS = 0.2

ELEMENT_ORDER = {
    "ASDShellQ4": 1,
    "ShellMITC4": 1,
    "HeterosisPlate": 2,
    "ShellMITC9": 2,
}


# Enclosing-topology patch: outer boundary plus distorted inner quadrilateral.
OUTER_BL = (0.00, 0.00)
OUTER_BR = (3.40, 0.00)
OUTER_TR = (3.40, 3.00)
OUTER_TL = (0.00, 3.00)

INNER_BL = (1.12, 1.05)
INNER_BR = (2.24, 1.00)
INNER_TR = (2.15, 2.08)
INNER_TL = (1.02, 2.14)

PATCH_BLOCKS = {
    "center": [INNER_BL, INNER_BR, INNER_TR, INNER_TL],
    "bottom": [OUTER_BL, OUTER_BR, INNER_BR, INNER_BL],
    "right": [INNER_BR, OUTER_BR, OUTER_TR, INNER_TR],
    "top": [INNER_TL, INNER_TR, OUTER_TR, OUTER_TL],
    "left": [OUTER_BL, INNER_BL, INNER_TL, OUTER_TL],
}


def q4_surface_points(corners: list[tuple[float, float]]) -> dict[int, list[float]]:
    """Return Q4 surface control points from four counter-clockwise corners."""
    return {
        index + 1: [float(x), float(y), 0.0]
        for index, (x, y) in enumerate(corners)
    }


def q9_surface_points(corners: list[tuple[float, float]]) -> dict[int, list[float]]:
    """Return Q9 surface control points from four counter-clockwise corners."""
    p1, p2, p3, p4 = [np.asarray(point, dtype=float) for point in corners]

    points = [
        p1,
        p2,
        p3,
        p4,
        0.5 * (p1 + p2),
        0.5 * (p2 + p3),
        0.5 * (p3 + p4),
        0.5 * (p4 + p1),
        0.25 * (p1 + p2 + p3 + p4),
    ]

    return {
        index + 1: [float(point[0]), float(point[1]), 0.0]
        for index, point in enumerate(points)
    }


def surface_points(
    corners: list[tuple[float, float]],
    mesh_order: int,
) -> dict[int, list[float]]:
    """Return surface control points for the requested mesh order."""
    if mesh_order == 1:
        return q4_surface_points(corners)

    if mesh_order == 2:
        return q9_surface_points(corners)

    raise ValueError(f"Unsupported mesh order: {mesh_order}")


def build_model(element_name: str, mesh_order: int) -> xara.Model:
    """Build the distorted five-element patch."""
    model = xara.Model(ndm=3, ndf=6)
    model.section("ElasticShell", SECTION_TAG, E_MOD, NU, THICKNESS)

    for corners in PATCH_BLOCKS.values():
        model.surface(
            (1, 1),
            element=element_name,
            args={"section": SECTION_TAG},
            order=mesh_order,
            points=surface_points(corners, mesh_order),
        )

    return model


def element_coordinates(model: xara.Model, element_tag: int) -> tuple[list[int], np.ndarray]:
    """Return element connectivity and xy coordinates."""
    connectivity = [int(tag) for tag in model.eleNodes(element_tag)]
    coordinates = np.array(
        [model.nodeCoord(node_tag)[:2] for node_tag in connectivity],
        dtype=float,
    )

    return connectivity, coordinates