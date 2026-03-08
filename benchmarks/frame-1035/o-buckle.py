import opensees.openseespy as ops
import matplotlib.pyplot as plt

plt.rc('text',usetex=True)
plt.rc('font',family='serif')

m = 1
kN = 1

mm = 0.001*m
GPa = kN/mm**2
MPa = 0.001*GPa

# T-section
b = 150*mm
dw = 300*mm
tw = 6*mm
tf = 10*mm

y0 = dw/4 + tf/2

# J = (b*tf**3 + dw*tw**3) / 3
J = 7.937366000041271e-08

E = 200000*MPa
G = 80000*MPa

plt.figure(1)

for ie,ele in enumerate(['dispBeamColumn','dispBeamColumnAsym']):

    for iL,L in enumerate([6*m]):
        ops.wipe()
        ops.model('basic','-ndm',3,'-ndf',6)

        ops.uniaxialMaterial('Elastic',1,E)
        ops.section('Fiber',1,'-GJ',G*J)
        ops.patch('rect',1,10,2,-dw,-tw/2,0,tw/2)
        ops.patch('rect',1,2,10,0,-b/2,tf,b/2)

        ops.section('FiberAsym',2,y0,0,'-GJ',G*J)
        ops.patch('rect',1,10,2,-dw,-tw/2,0,tw/2)
        ops.patch('rect',1,2,10,0,-b/2,tf,b/2)

        if 'Asym' in ele:
            secTag = 2
        else:
            secTag = 1

        Np = 3
        ops.beamIntegration('Lobatto',1,secTag,Np)

        Nele = 20
        dL = L/Nele

        ops.geomTransf('Corotational',1,0,1,0)

        ops.node(0,0,0,0)
        ops.fix(0,1,1,1,1,0,0)
        for i in range(Nele):
            ops.node(i+1,(i+1)*dL,0,0)
            if 'Asym' in ele:
                ops.element(ele,i+1,i,i+1,1,1,'-shearCenter',y0,0)
            else:
                ops.element(ele,i+1,i,i+1,1,1)
        ops.fix(Nele,0,1,1,0,0,0)

        for nd in ops.getNodeTags():
            ops.mass(nd,1,1,1,1,1,1)
        
        ops.timeSeries('Linear',1)
        ops.pattern('Plain',1,1)
        ops.load(0,    0,0,0,0,-1,0)
        ops.load(Nele, 0,0,0,0, 1,0)


        Mmax = 60*kN*m
        dM = 0.1*kN*m
        Nsteps = int(Mmax/dM)

        ops.integrator('LoadControl',dM)
        ops.system('UmfPack')
        ops.analysis('Static')

        u = []
        M = []
        v = []
        for i in range(Nsteps):
            ok = ops.analyze(1)
            if ok < 0:
                break
            lam = ops.eigen('standard','symmBandLapack',1)[0]
            u.append(lam)
            lam2 = ops.eigen(1)[0]
            v.append(lam2)
            M.append(ops.getLoadFactor(1))
            if lam < 0 and lam2 < 0:
                break

        plt.plot(M,u,label=f'{ele}, symmBandLapack eigen')
        plt.plot(M,v,label=f'{ele}, Arpack (M=I) eigen')        
        
plt.figure(1)        
plt.xlabel('Applied Moment (kN-m)')
plt.ylabel('Lowest Eigenvalue')
plt.grid()
plt.xlim([0,60*kN*m])
plt.ylim(bottom=0)
plt.legend(loc='upper right')
plt.title(f'$L$={L} m, T-section, {Nele} corotational elements')
plt.tight_layout()

plt.show()