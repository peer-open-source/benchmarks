# 2D problem with 2 DOFs on both the constrained node and the retained nodes
# The embedding domain is a 1x1 triangle, and the constrained node is placed at its centroid.
# Here we apply a random displacement on each retained node,
# and the displacement of the constrained node should be the weighted average
# of the displacements at the 3 retained nodes, with an equal weight = 1/3.
import xara
from random import random as rand

model = xara.Model(ndm=2, ndf=2)

# define the embedding domain (a piece of a soild domain)
model.node(1, 0.0, 0.0)
model.node(2, 1.0, 0.0)
model.node(3, 0.0, 1.0)

# define the embedded node
model.node(4, 1.0/3.0, 1.0/3.0)

# define constraint element
model.element('ASDEmbeddedNodeElement', 1, 4, (1, 2, 3),  K=1.0e6)


# apply random imposed displacement in range 0.1-1.0
U1 = [0.1 + 0.9*rand(), 0.1 + 0.9*rand()]
U2 = [0.1 + 0.9*rand(), 0.1 + 0.9*rand()]
U3 = [0.1 + 0.9*rand(), 0.1 + 0.9*rand()]
print('Applying random X displacement:\nU1: {}\nU2: {}\nU3: {}\n\n'.format(U1,U2,U3))

model.pattern('Plain', 1, "Constant")
for i in range(1, 3):
   model.sp(1, i, U1[i - 1], pattern=1)
   model.sp(2, i, U2[i - 1], pattern=1)
   model.sp(3, i, U3[i - 1], pattern=1)


# run analysis
model.constraints('Transformation')
model.numberer('Plain')
model.system('FullGeneral')
model.test('NormUnbalance', 1e-08, 10, 1)
model.algorithm('Linear')
model.integrator('LoadControl', 1.0)
model.analysis('Static')
model.analyze(1)

# compute expected solution
UCref = [
   (U1[0] + U2[0] + U3[0])/3.0,
   (U1[1] + U2[1] + U3[1])/3.0
]
print('Expected displacement at constrained node is (U1+U2+U3)/3:\n{}\n\n'.format(UCref))

# read results
UC = model.state.u(node=4)
print('Obtained displacement at constrained node is UC:\n{}\n\n'.format(UC))

# check error
ER = [
   abs(UC[0] - UCref[0])/UCref[0],
   abs(UC[1] - UCref[1])/UCref[1]
]
print('Relative error is abs(UC-UCref)/UCref:\n{}\n\n'.format(ER))

