"""
               ^ P
               |
               .<|o
             .
           .
   y ^   .
     | .
    _._ ---> x
    o o

"""
import pytest
import numpy as np
import xara

def diamond_solution(EI, EA, L, off=0):
    import numpy as np
    Le = L - 2*off
    dX = dY = Le/np.sqrt(2)
    Ag = np.array([[-dX/Le   ,  dY/Le   , 0,  dX/Le   ],
                   [-dY/Le**2, -dX/Le**2, 0,  dY/Le**2],
                   [-dY/Le**2, -dX/Le**2, 1,  dY/Le**2]])
    Ao = np.array([[0, 1,              0],
                   [1, 0,-off/np.sqrt(2)],
                   [0, 0,              1],
                   [0, 0, off/np.sqrt(2)]])

    A  = Ag@Ao
    Ke = np.array([[EA/Le,       0,       0],
                   [    0, 4*EI/Le, 2*EI/Le],
                   [    0, 2*EI/Le, 4*EI/Le]])

    K = A.T@Ke@A

    kuw = K[1:,0]
    return 1/np.linalg.solve(K, [1,0,0])
#   return K[0][0] - kuw.dot(np.linalg.solve(K[1:,1:], kuw))


def test():
    m = xara.Model(ndm=3, ndf=6)

    L   = 5
    off = 0.1*L
    X   = L / np.sqrt(2)
    E   = 30
    I   = 1
    A   = 500*I

    m.node(1, (0, 0, 0))
    m.node(2, (X, X, 0))
    m.fix(1,  (0, 1, 1,  1, 1, 1))
    m.fix(2,  (1, 0, 1,  1, 0, 0))


    m.geomTransf("Linear", 1, (0, 0, 1),
                offset={
                    1: ( off/np.sqrt(2), off/np.sqrt(2), 0),
                    2: (-off/np.sqrt(2),-off/np.sqrt(2), 0),
                }
    )

    section, element = "ElasticFrame", "ForceFrame"

    m.section(section, 1, E=E, A=A, Iy=I, Iz=I, G=1, J=3/2*I)
    m.element(element, 1, (1, 2), transform=1, section=1, shear=0)

    m.pattern("Plain", 1, "Linear", loads={2: (0, 1, 0,   0, 0, 0)})

    P = -4*L**2/(E*I)

    m.integrator("LoadControl", P)
    m.analysis("Static")
    m.test("NormDispIncr", 1e-8, 2)
    m.analyze(1)

    Uref = P/diamond_solution(E*I, E*A, L, off=off)/L

    print("Solution: ", Uref)
    print("Output: ")
    print(m.nodeDisp(1, 1)/L)
    assert m.nodeDisp(1, 1)/L == pytest.approx(Uref[1], rel=1e-6)

    print(m.nodeDisp(2, 6)/L)
    assert m.nodeDisp(2, 6)/L == pytest.approx(Uref[2], rel=1e-6)

    print(m.nodeDisp(2, 2)/L)
    assert m.nodeDisp(2,2)/L == pytest.approx(Uref[0], rel=1e-6)


if __name__ == "__main__":
    test()

