import opensees.openseespy as ops
 
ops.wipe()
ops.model('basic','-ndm',1,'-ndf',1)
 
ops.node(0,0); ops.fix(0,1)
ops.node(1,0)
ops.node(2,0)
 
ops.uniaxialMaterial('Steel01',1,10,10,0.1)
ops.uniaxialMaterial('Steel01',2,4,2,0.5)
ops.uniaxialMaterial('Steel01',3,7,7,0)
 
# Spring elements
ops.element('zeroLength',1,0,1,'-mat',1,'-dir',1)
ops.element('zeroLength',2,1,2,'-mat',2,'-dir',1)
ops.element('zeroLength',3,0,2,'-mat',3,'-dir',1)
 
# Dummy elastic material
ops.uniaxialMaterial('Elastic',0,0)
 
# Diagonal '-1' stiffness
ops.uniaxialMaterial('Penalty',4,0,-1,'-noStress')
ops.element('zeroLength',4,0,1,'-mat',4,'-dir',1)
 
# Off-diagonal '+0.5' stiffness
ops.uniaxialMaterial('Penalty',5,0,-0.5,'-noStress')
ops.element('zeroLength',5,1,2,'-mat',5,'-dir',1)
ops.uniaxialMaterial('Penalty',6,0,0.5,'-noStress')
ops.element('zeroLength',6,0,1,'-mat',6,'-dir',1)
ops.element('zeroLength',7,0,2,'-mat',6,'-dir',1)
 
ops.timeSeries('Constant',1)
ops.pattern('Plain',1,1)
ops.load(1,6)
ops.load(2,12)

ops.test('RelativeNormUnbalance',1e-4,150,1)
ops.algorithm('KrylovNewton') # Or whatever
ops.analysis('Static')
 
ops.analyze(1)

print(ops.nodeDisp(1))
print(ops.nodeDisp(2))
