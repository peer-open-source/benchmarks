"""Eigenvalue analysis of a multi-bay, multi-story frame.

Compares computed eigenvalues against published results from
Bathe & Wilson, Peterson, SAP2000, and SeismoStruct.
"""

import pytest
from math import asin

import xara


# reference data

REFERENCE_EIGENVALUES = {
    "Bathe&Wilson": [0.589541, 5.52695, 16.5878],
    "Peterson":     [0.589541, 5.52696, 16.5879],
    "SAP2000":      [0.589541, 5.52696, 16.5879],
    "SeismoStruct": [0.58955,  5.527,   16.588],
}

# Tolerances per mode (compared against SAP2000)
TOLERANCES = [9.99e-7, 9.99e-6, 9.99e-5]

# ── frame geometry / properties

BAY_WIDTH    = 20.0
STORY_HEIGHT = 10.0
NUM_BAY      = 10
NUM_FLOOR    = 9

A = 3.0       # ft^2
E = 432000.0  # k/ft^2
I = 1.0       # ft^4
M = 3.0       # kip·sec^2/ft^2

COORD_TRANSF = "Linear"
MASS_TYPE    = "-lMass"
N_GAUSS_PTS  = 3

NUM_EIGEN = 3

# Fiber section parameters chosen so A=3, I=1  (b=1.5, d=2.0)
FIBER_D       = 2.0
FIBER_B       = 1.5
NUM_FIBER_Y   = 2000  # enough fibres for ~1e-7 eigenvalue accuracy
NUM_FIBER_Z   = 1

# element types

ELEMENT_TYPES = [
    "elasticBeam",
    "forceBeamElasticSection",
    "dispBeamElasticSection",
    "forceBeamFiberSectionElasticMaterial",
    "dispBeamFiberSectionElasticMaterial",
]

SOLVER_TYPES = [
    "-genBandArpack",
    "-fullGenLapack",
]


# helpers

def _build_model():
    """Create nodes, constraints, materials, sections, and integration rules."""

    model = xara.Model(ndm=2, ndf=3)

    # material & sections
    model.uniaxialMaterial("Elastic", 1, E)
    model.section("Elastic", 1, E, A, I)

    model.section("Fiber", 2)
    half_d, half_b = FIBER_D / 2.0, FIBER_B / 2.0
    model.patch(
        "quad", 1, NUM_FIBER_Y, NUM_FIBER_Z,
        -half_d, -half_b,  half_d, -half_b,
         half_d,  half_b, -half_d,  half_b,
    )

    # nodes – one floor at a time
    tag = 1
    for j in range(NUM_FLOOR + 1):
        for i in range(NUM_BAY + 1):
            model.node(tag, i * BAY_WIDTH, j * STORY_HEIGHT)
            tag += 1

    # fix base row
    for i in range(1, NUM_BAY + 2):
        model.fix(i, 1, 1, 1)

    # geometric transformation & beam integrations
    model.geomTransf(COORD_TRANSF, 1)
    model.beamIntegration("Lobatto", 1, 1, N_GAUSS_PTS)  # elastic section
    model.beamIntegration("Lobatto", 2, 2, N_GAUSS_PTS)  # fiber  section
    return model


def _add_element(model, ele_type, tag, nd1, nd2):
    """Add a single beam/column element of the requested type."""
    transf_tag = 1
    if ele_type == "elasticBeam":
        model.element(
            "elasticBeamColumn", tag, nd1, nd2,
            A, E, I, 1, "-mass", M, MASS_TYPE,
        )
    elif ele_type == "forceBeamElasticSection":
        model.element(
            "forceBeamColumn", tag, nd1, nd2,
            transf_tag, 1, "-mass", M,
        )
    elif ele_type == "dispBeamElasticSection":
        model.element(
            "dispBeamColumn", tag, nd1, nd2,
            transf_tag, 1, "-mass", M, MASS_TYPE,
        )
    elif ele_type == "forceBeamFiberSectionElasticMaterial":
        model.element(
            "forceBeamColumn", tag, nd1, nd2,
            transf_tag, 2, "-mass", M,
        )
    elif ele_type == "dispBeamFiberSectionElasticMaterial":
        model.element(
            "dispBeamColumn", tag, nd1, nd2,
            transf_tag, 2, "-mass", M, MASS_TYPE,
        )
    else:
        raise ValueError(f"Unknown element type: {ele_type!r}")


def _add_frame_elements(model, ele_type):
    """Add all column and beam elements for the frame."""
    tag = 1
    nodes_per_floor = NUM_BAY + 1

    # columns
    for i in range(nodes_per_floor):
        nd1 = i + 1
        nd2 = nd1 + nodes_per_floor
        for _ in range(NUM_FLOOR):
            _add_element(model, ele_type, tag, nd1, nd2)
            tag += 1
            nd1 = nd2
            nd2 += nodes_per_floor

    # beams
    for j in range(1, NUM_FLOOR + 1):
        nd1 = nodes_per_floor * j + 1
        nd2 = nd1 + 1
        for _ in range(NUM_BAY):
            _add_element(model, ele_type, tag, nd1, nd2)
            tag += 1
            nd1 = nd2
            nd2 += 1


def _check_eigenvalues(eigenvalues):
    """Assert each eigenvalue is within tolerance of the SAP2000 reference."""
    ref = REFERENCE_EIGENVALUES["SAP2000"]
    for mode, (computed, expected, tol) in enumerate(
        zip(eigenvalues, ref, TOLERANCES), start=1
    ):
        assert abs(computed - expected) <= tol, (
            f"Mode {mode}: eigenvalue {computed} differs from SAP2000 "
            f"reference {expected} by {abs(computed - expected):.2e} "
            f"(tolerance {tol:.2e})"
        )


def _print_comparison(label, eigenvalues):
    """Print a comparison table (useful with ``pytest -s``)."""
    header = f"{'OpenSees':>15}" + "".join(
        f"{name:>15}" for name in REFERENCE_EIGENVALUES
    )
    print(f"\n\nEigenvalue comparison – {label}")
    print(header)
    for i in range(NUM_EIGEN):
        row = f"{eigenvalues[i]:>15.5f}" + "".join(
            f"{vals[i]:>15.5f}" for vals in REFERENCE_EIGENVALUES.values()
        )
        print(row)

#
# Tests
#
@pytest.mark.parametrize("element", ELEMENT_TYPES)
def test_eigenvalues_by_element(element):
    """Eigenvalues must match references for each element formulation."""
    model = _build_model()
    _add_frame_elements(model, element)

    eigenvalues = model.eigen(NUM_EIGEN)

    _print_comparison(f"element={element}", eigenvalues)
    _check_eigenvalues(eigenvalues)


@pytest.mark.parametrize("solver", SOLVER_TYPES)
def test_eigenvalues_by_solver(solver):
    """Eigenvalues must match references for each eigen-solver backend."""
    model = _build_model()
    _add_frame_elements(model, "elasticBeam")

    eigenvalues = model.eigen(solver, NUM_EIGEN)

    _print_comparison(f"solver={solver}", eigenvalues)
    _check_eigenvalues(eigenvalues)
