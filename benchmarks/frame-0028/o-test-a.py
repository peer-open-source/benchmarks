import opensees.openseespy as ops
from math import isclose

L = 48
E = 29000
h = 6
A = h*h
I = h**4/12

w = 0.001
m = (h/2)*w

ops.model("basic", ndm=3, ndf=6)

ops.node(1, (0,0,0))
ops.node(2, (L/2,0,0))
ops.node(3, (L,0,0))
ops.fix(1, (1,1,1, 1,1,1))

ops.geomTransf("Linear",1, (0,0,1))

ops.section("ElasticFrame",1,
            E=E,
            A=A,
            Iy=I,
            Iz=I,
            G=12000,
            J=2*I,
            Ay=A*500,
            Az=A*500)

ops.element("ExactFrame",1, [1,2,3], section=1, transform=1)

ops.pattern("Plain",1,"Constant")
ops.eleLoad("Frame",
            "Uniform", # Uniformly distributed load
            basis = "local",
            force = [w, 0, 0],
            couple= [0,0,-m],
            pattern=1,
            elements=1
)

ops.analysis("Static")
ops.analyze(1)
ops.reactions()

print(ops.nodeDisp(3))
u23 = ops.nodeDisp(3,6)
u22 = ops.nodeDisp(3,2)
print(u23,u22)
print(ops.nodeReaction(1))

assert isclose( m*L,ops.nodeReaction(1,6),rel_tol=1e-4), (m*L, ops.nodeReaction(1,6))
assert isclose(-m*L**2/(2*E*I), u23, rel_tol=1e-4), (-m*L*L/(2*E*I), u23)
assert isclose(-m*L**3/(3*E*I), u22, rel_tol=1e-4), (-m*L*L*L/(3*E*I), u22)

