#
# Cantilever beam with transverse tip load
#
# modeled with three dimensional brick elements
# 
import veux
import xara
from xara.helpers import find_node, find_nodes


import xara
from xara.helpers import find_node, find_nodes
import pytest


def create_model(element="stdBrick"):
    model = xara.Model(ndm=3, ndf=3)

    E = 100.0
    model.material("ElasticIsotropic", 1, E, 0.25, 1.27)

    L = 10.0
    b =  1.0
    d =  1.0
    P = 10.0

    # nz = 10
    # nx = 2
    # ny = 2
    nz = 40
    nx = 6
    ny = 6

    model.block3D(*(nx, ny, nz), *(1, 1), element, 1, {
                1: [-b/2, -d/2,  0.0],
                2: [ b/2, -d/2,  0.0],
                3: [ b/2,  d/2,  0.0],
                4: [-b/2,  d/2,  0.0],
                5: [-b/2, -d/2,   L ],
                6: [ b/2, -d/2,   L ],
                7: [ b/2,  d/2,   L ],
                8: [-b/2,  d/2,   L ]})

    model.fixZ(0.0, (1, 1, 1))

    model.pattern("Plain", 1, "Linear")

    tip_corners = [
        find_node(model, z=L, x=-b/2, y=-d/2),
        find_node(model, z=L, x= b/2, y=-d/2),
        find_node(model, z=L, x= b/2, y= d/2),
        find_node(model, z=L, x=-b/2, y= d/2)
    ]
    tip_edges = [
        *find_nodes(model, z=L, x=-b/2, y=None),
        *find_nodes(model, z=L, x= b/2, y=None),
        *find_nodes(model, z=L, x=None, y=-d/2),
        *find_nodes(model, z=L, x=None, y= d/2)
    ]
    tip_edges = [node for node in tip_edges if node not in tip_corners]

    tip_interior = [
        node for node in find_nodes(model, z=L)
        if node not in tip_corners and node not in tip_edges
    ]

    # Consistent nodal loads for 8-node bricks under uniform pressure.
    # Each bilinear quad face distributes load equally to its 4 corners,
    # so a node's total share equals (pressure * element_face_area / 4)
    # summed over the element faces it touches:
    #   corners  -> 1 face  -> weight 1
    #   edges    -> 2 faces -> weight 2
    #   interior -> 4 faces -> weight 4
    P_base = P / (4 * nx * ny)

    for node in tip_corners:
        model.load(node, (0.0, P_base, 0.0))
    for node in tip_edges:
        model.load(node, (0.0, 2 * P_base, 0.0))
    for node in tip_interior:
        model.load(node, (0.0, 4 * P_base, 0.0))

    model.integrator("LoadControl", 1.0)
    model.test("NormUnbalance", 1.0e-10, 2, 1)
    model.algorithm("Newton")
    model.constraints("Plain")
    model.system("Umfpack")
    model.analysis("Static")
    assert model.analyze(1) == 0

    Iy = b * d**3 / 12
    tip = find_node(model, z=L, x=0.0, y=0.0)

    return model, tip, P, L, E, Iy


def check_displacement(element):
    model, tip, P, L, E, Iy = create_model(element)

    # Euler-Bernoulli beam theory: delta = P*L^3 / (3*E*I)
    expected = P * L**3 / (3 * E * Iy)

    uy = model.nodeDisp(tip, 2)  # y-displacement

    print(element, uy)

    assert uy == pytest.approx(expected, rel=0.05)


def test():
    for element in ["SSPbrick"]:
        check_displacement(element)


if __name__ == "__main__":
    test()