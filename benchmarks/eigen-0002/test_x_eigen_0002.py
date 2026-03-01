# https://github.com/OpenSees/OpenSees/issues/1293
import xara

def test():
    model = xara.Model(ndm=1,ndf=1)

    model.node(0,0); model.fix(0,1)
    model.node(1,0); model.mass(1,1.0)
    model.node(2,0); model.mass(2,1.0)
    model.node(3,0); model.mass(3,1.0)
    model.node(4,0); model.mass(4,1.0)

    k = 610
    model.uniaxialMaterial('Elastic',1,k)

    model.element('ZeroLength',1, (0,1), mat=1, dir=1)
    model.element('ZeroLength',2, (1,2), mat=1, dir=1)
    model.element('ZeroLength',3, (0,3), mat=1, dir=1)
    model.element('ZeroLength',4, (3,4), mat=1, dir=1)

    Nmodes = 3
    w2 = model.eigen('fullGenLapack',Nmodes)
#   w2 = model.eigen(Nmodes)

    print(w2)

    N = model.systemSize()
    for n in range(Nmodes):
        for i in range(N):
            print(model.nodeEigenvector(i+1,n+1,1))
        print()

