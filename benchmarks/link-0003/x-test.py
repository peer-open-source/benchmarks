# https://openseesdigital.com/2025/02/23/two-node-links-awakening/
import xara
from math import isclose

kt = 10 # Translational stiffness
kr = 20 # Rotational stiffness
P = 5   # Load
L = 10  # Link length
c = 0.5 # Shear distance

if __name__ == "__main__":

    model = xara.Model(ndm=2, ndf=3)

    model.uniaxialMaterial('Elastic',1,kt)
    model.uniaxialMaterial('Elastic',2,kr)

    model.node(0,0,0)
    model.node(2,0,L)
    model.node(1,0,0)
    model.fix(0,1,1,1)
    model.fix(1,0,1,0)
    model.fix(2,0,1,0)

    model.element('zeroLength',1,0,1,'-mat',1,2,'-dir',2,3,'-orient',0,1,0)
    model.element('twoNodeLink',2,0,2,'-mat',1,2,'-dir',2,3,'-shearDist',c)

    model.pattern('Plain',1,"Constant")
    model.load(1,P,0,0, pattern=1)
    model.load(2,P,0,0, pattern=1)

    model.analysis('Static')
    model.analyze(1)

    # X-displacement
    u1 = model.nodeDisp(1,1)
    u2 = model.nodeDisp(2,1)

    assert isclose(u1,P/kt)
    assert isclose(u2,P/kt + P*L*(1-c)/kr*L*(1-c))

    # Rotation
    u1 = model.nodeDisp(1,3)
    u2 = model.nodeDisp(2,3)

    assert isclose(u1,0,abs_tol=1e-10)
    assert isclose(u2,-P*L*(1-c)/kr)

