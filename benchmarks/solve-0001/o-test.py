import xara

ops = xara.Model(ndm=2, ndf=3)
L = 100
E = 29000
A = 20
I = 1400

ops.node(1, (0,0))
ops.fix(1,1,1,1)
ops.node(2, (L,0))
ops.fix(2,1,1,1)

ops.geomTransf('Linear',1)
ops.element('elasticBeamColumn',1,1,2,A,E,I,1)

ops.timeSeries('Constant',1)
ops.pattern('Plain',1,1)
ops.sp(2,2,1.0) # Unit displacement at node 2, DOF 2

ops.constraints('Transformation')
#ops.system('BandSPD')
#ops.system('ProfileSPD')
ops.system("Umfpack")

ops.analysis('Static')
ops.analyze(1)
ops.reactions()
