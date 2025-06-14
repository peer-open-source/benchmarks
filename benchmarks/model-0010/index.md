---
title: Linear Elastic Planar Shear Walls
description: Verification of Linear Elastic Planar Shear Wall
---


Multiple Shear Wall building models with lengths of 120", 240" and 360" lengths. 
Buildings of 1 story, 3 Story and 6 story are modelled. 
Each buildings story height is 120" All walls 12". 
All materials elastic with modulus of elasticity of 3000 ksi and poisson's ration of 0.2. 
At each floor in the buildings all nodes at the floor level are constrained to
move horizontally together.

Loading: For each building a 100k load is applied at top left node.
Results: compare nodal displacement at node were load is applied to Etabs and SAP, results verified using SAP.

> NOTE: The discretization of the SAP and ETABS models are not known at this time

# References

1) ETABS Software Verification Examples, Computers and Structures, Inc, 2003 (Example 15A)

