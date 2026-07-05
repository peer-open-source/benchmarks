#!/usr/bin/env python
# coding: utf-8

# 
# ## Model
# 
# We begin by defining the model builder and creating the nodes of the brick:
# 
import xara
model = xara.Model(ndm=3, ndf=3)

model.node(1, (1.0, 0.0, 0.0))
model.node(2, (1.0, 1.0, 0.0))
model.node(3, (0.0, 1.0, 0.0))
model.node(4, (0.0, 0.0, 0.0))
model.node(5, (1.0, 0.0, 1.0))
model.node(6, (1.0, 1.0, 1.0))
model.node(7, (0.0, 1.0, 1.0))
model.node(8, (0.0, 0.0, 1.0))



# The boundary conditions are applied to simulate triaxial constraints, fixing displacements appropriately on different node sets:

model.fix( 1, (0, 1, 1))
model.fix( 2, (0, 0, 1))
model.fix( 3, (1, 0, 1))
model.fix( 4, (1, 1, 1))
model.fix( 5, (0, 1, 0))
model.fix( 6, (0, 0, 0))
model.fix( 7, (1, 0, 0))
model.fix( 8, (1, 1, 0))


# The Drucker–Prager material is defined with specified parameters for elasticity, yield surface, and hardening behavior:
# 
# 

# In[ ]:


# model.nDMaterial("DruckerPrager", 2,
#     K       = 27777.78 ,
#     G       =  9259.26 ,
#     Fy      =     5.0  ,
#     Rvol    =     0.398,
#     Rbar    =     0.398,
#     Fs      =     0.0  ,
#     Fo      =     0.0  ,
#     Hsat    =     0.0  ,
#     H       =     0.0  ,
#     theta   =     1.0  ,
#     delta2  =     0.0  ,
#     density =   1.7
# )

material = xara.MultiaxialMaterial("DruckerPrager", 
    K       = 27777.78 ,
    G       =  9259.26 ,
    Fy      =     5.0  ,
    Rvol    =     0.398,
    Rbar    =     0.398,
    Fs      =     0.0  ,
    Fo      =     0.0  ,
    Hsat    =     0.0  ,
    H       =     0.0  ,
    theta   =     1.0  ,
    delta2  =     0.0  ,
    density =     1.7
)
model.material(material)


# 
# The model includes a single `stdBrick` element to represent the soil specimen:
# 

# In[ ]:


model.element("stdBrick", 1, (1, 2, 3, 4, 5, 6, 7, 8), material, 0.0, 0.0, 0.0)


# 
# ## Recorders
# 
# Nodal displacements and Gauss point quantities such as stress, strain, and material state variables are recorded:
# 
# 
# ```tcl
# set step 0.1
# 
# recorder Node -file out/displacements1.out -time -dT $step -nodeRange 1 8 -dof 1 2 3 disp
# 
# recorder Element -ele 1 -time -file out/stress1.out  -dT $step material 2 stress
# recorder Element -ele 1 -time -file out/strain1.out  -dT $step material 2 strain
# recorder Element -ele 1 -time -file out/state1.out   -dT $step material 2 state
# ```
# 



# 
# ## Loading
# 
# Two loading patterns are defined: the first applies hydrostatic pressure, and the second imposes axial deviatoric stress:
# 
# ```tcl
# set p 10.0
# set pNode [expr -$p * 0.25]
# 
# pattern Plain 1 {Series -time {0 10 100} -values {0 1 1} -factor 1} {
#     load 1  $pNode    0.0 0.0
#     load 2  $pNode $pNode 0.0
#     load 3     0.0 $pNode 0.0
#     load 5  $pNode    0.0 0.0
#     load 6  $pNode $pNode 0.0
#     load 7     0.0 $pNode 0.0
# }
# 
# pattern Plain 2 {Series -time {0 10 100} -values {0 1 5} -factor 1} {
#     load 5  0.0 0.0 $pNode
#     load 6  0.0 0.0 $pNode
#     load 7  0.0 0.0 $pNode
#     load 8  0.0 0.0 $pNode
# }
# ```

p = 10.0
pNode = -p * 0.25


p1 = xara.StaticPattern(
    series=xara.TimeSeries(time=[0, 10, 100], values=[0, 1, 1]),
    loads=xara.NodalLoad(model, {
        1:  (pNode,   0.0, 0.0),
        2:  (pNode, pNode, 0.0),
        3:  (  0.0, pNode, 0.0),
        5:  (pNode,   0.0, 0.0),
        6:  (pNode, pNode, 0.0),
        7:  (  0.0, pNode, 0.0),
    })
)
model.pattern(p1)

p2 = xara.StaticPattern(
    series=xara.TimeSeries(time=[0, 10, 100], values=[0, 1, 5]),
    loads=xara.NodalLoad(model, {
        5:  (0.0, 0.0, pNode),
        6:  (0.0, 0.0, pNode),
        7:  (0.0, 0.0, pNode),
        8:  (0.0, 0.0, pNode),
    })
)
model.pattern(p2)

#
# ## Analysis
# 
# The analysis uses standard OpenSees commands to control the solution procedure and apply the loads incrementally:
# 
# 
# ```tcl
# integrator LoadControl 0.1
# numberer RCM
# system SparseGeneral
# constraints Transformation
# test NormDispIncr 1e-5 1 1
# algorithm Newton
# analysis Static
# 
# puts "starting the hydrostatic analysis..."
# set startT [clock seconds]
# analyze 1000
# set endT [clock seconds]
# 
# puts "triaxial shear application finished..., [getTime]"
# ```
# 

model.integrator("LoadControl", 0.1)
model.numberer("RCM")
model.system("SparseGeneral")
model.constraints("Transformation")
model.test("NormDispIncr", 1e-5, 1, 1)
model.algorithm("Newton")
model.analysis("Static")


model.analyze(1000)
print(model.getTime())
model.wipe()
