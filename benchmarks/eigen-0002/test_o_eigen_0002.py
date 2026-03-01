
import opensees.openseespy as ops

def test():
    ops.wipe()
    ops.model('basic','-ndm',1,'-ndf',1)

    ops.node(0,0); ops.fix(0,1)
    ops.node(1,0); ops.mass(1,1.0)
    ops.node(2,0); ops.mass(2,1.0)
    ops.node(3,0); ops.mass(3,1.0)
    ops.node(4,0); ops.mass(4,1.0)

    k = 610
    ops.uniaxialMaterial('Elastic',1,k)

    ops.element('zeroLength',1,0,1,'-mat',1,'-dir',1)
    ops.element('zeroLength',2,1,2,'-mat',1,'-dir',1)
    ops.element('zeroLength',3,0,3,'-mat',1,'-dir',1)
    ops.element('zeroLength',4,3,4,'-mat',1,'-dir',1)

    Nmodes = 3
    #w2 = ops.eigen('fullGenLapack',Nmodes)
    w2 = ops.eigen(Nmodes)

    print(w2)

    N = ops.systemSize()
    for n in range(Nmodes):
        for i in range(N):
            print(ops.nodeEigenvector(i+1,n+1,1))
        print()

