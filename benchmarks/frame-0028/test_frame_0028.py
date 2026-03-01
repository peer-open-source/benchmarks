"""
Test distributed element loads.

A cantilever is subjected to a uniformly distributed axial
force at an offset from the neutral axis.

Two equivalent representations are tested:
    1) A uniformly distributed couple and axial force
    2) A uniformly distributed axial force with an offset
"""

import xara
from xara.load import FrameLoad
import math
isclose = lambda a,b,rel_tol=1e-9: math.isclose(a,b,rel_tol=rel_tol)

L = 48
E = 29000
h = 6
b = h
A = h*b
I = h**3*b/12

w = 0.1
m = (h/2)*w

def analyze(element, load_type="couple"):
    model = xara.Model(ndm=3, ndf=6)

    model.node(1, (0,0,0))
    model.node(2, (L,0,0))

    model.fix(1, (1,1,1, 1,1,1))

    model.geomTransf('Linear', 1, (0,0,1))

    model.section('ElasticFrame',1,
                  E=E,A=A,Iy=I,Iz=I,
                  G=12000,
                  J=2*I,
                  Ay=A*500,
                  Az=A*500)

    model.element(element, 1, [1,2], section=1, transform=1, shear=0)

    if load_type == "offset":
        load = FrameLoad(model,
                        shape='Heaviside', 
                        basis='local',
                        elements=[1],
                        couple=[0,0,-m],
                        offset=[0,h/2,0])
    elif load_type == "couple":
        load = FrameLoad(model,
                        shape='Heaviside', 
                        basis='local',
                        elements=[1],
                        force=[w, 0, 0],
                        couple=[0,0,-m],
                        offset=[0,0,0])
    
    xara.solve(model, [load])
    model.reactions()
    return model


def test():
    for load_type in ["offset", "couple"]:
        for element in ["ForceFrame"]:
            model = analyze(element, load_type=load_type)

            print("Displacements ", model.nodeDisp(2))
            u23 = model.nodeDisp(2,6)
            u22 = model.nodeDisp(2,2)
            print("Reactions ", model.nodeReaction(1))

            # Root moment
            assert isclose( m*L, model.nodeReaction(1,6)), (m*L, model.nodeReaction(1,6))
            # Tip rotation
            assert isclose(-m*L**2/(2*E*I), u23),   (-m*L**2/(2*E*I), u23)
            # Tip deflection
            assert isclose(-m*L**3/(3*E*I), u22),   (-m*L**3/(3*E*I), u22)

