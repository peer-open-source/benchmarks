import xara
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

def analyze(element):
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

    model.timeSeries('Constant',1)
    model.pattern('Plain',1,"Constant")
    model.eleLoad("Frame",
                "Heaviside",
                basis = "local",
                # force = [w, 0,  0],
                couple= [0, 0, -m],
                # offset=[0, h/2, 0],
                pattern=1,
                elements=1
    )

    model.analysis('Static')
    model.analyze(1)
    model.reactions()
    return model



if __name__ == "__main__":
    model = analyze('ForceFrame')

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

