import xara
from math import isclose

k = 10 # Spring stiffness
P = 5  # Load
L = 10 # Link length

def test():
    model = xara.Model("basic", ndm=2, ndf=3)
    model.uniaxialMaterial("Elastic",1, k)

    model.node(0,0,0)
    model.fix(0,1,1,1)


    model.node(1,0,0)
    model.fix(1,1,0,1)
    model.element("zeroLength",1,(0,1), mat=1, dir=1, orient=(0,1,0))

    model.node(2,0,L)
    model.fix(2,1,0,1)
    model.element("twoNodeLink",2,(0,2), mat=1, dir=1)

    model.timeSeries("Constant",1)
    model.pattern("Plain",1,"Constant")
    model.load(1,0,P,0)
    model.load(2,0,P,0)

    model.analysis("Static")
    model.analyze(1)

    u1 = model.state.u(1,2)
    u2 = model.state.u(2,2)

    assert isclose(u1,P/k)
    assert isclose(u2,P/k)

    print(u1,u2)


if __name__ == "__main__":
    test()