
model  -ndm 3 -ndf 6
node 1 0.0 0 0 
node 2 0.0625 0 0 
node 3 0.125 0 0 
node 4 0.1875 0 0 
node 5 0.25 0 0 
node 6 0.3125 0 0 
node 7 0.375 0 0 
node 8 0.4375 0 0 
node 9 0.5 0 0 

fix 1 1 1 1 1 0 0 
fix 9 0 1 1 1 0 0 
material J2 1 -E 220000000000.0 -G 86614173228.34645 -Fy 413685441.48 -Fs 413685441.48 -Hiso 9997398169.1 -Hsat 16

section ShearFiber 1 -GJ 0
fiber  -area 0.000125 -y -0.012500000000000002 -z -0.0016666666666666668 -warp {{1.607450000329358e-05 0.005475421932095159 0.011483540411649784} {0 0.0 0}} -material 1 -section 1
fiber  -area 7.812500000000002e-05 -y 0.026041666666666668 -z 0.0016666666666666668 -warp {{4.321514136503465e-05 -0.006285227609041044 -0.02351551123918272} {0 0.0 0}} -material 1 -section 1
fiber  -area 0.000125 -y -0.03541666666666667 -z -0.0016666666666666668 -warp {{5.421077231830088e-05 0.0036843030486055648 0.032088937989396826} {0 0.0 0}} -material 1 -section 1
fiber  -area 7.8125e-05 -y 0.040625 -z 0.0016666666666666668 -warp {{6.888144895296951e-05 -0.0029482638278111057 -0.03705668266255069} {0 0.0 0}} -material 1 -section 1
fiber  -area 0.000125 -y 0.014583333333333332 -z -0.0016666666666666668 -warp {{-1.94738191949817e-05 0.0042404895818615165 -0.016936937994868617} {0 0.0 0}} -material 1 -section 1
fiber  -area 0.00015625 -y 0.002083333333333333 -z 0.0016666666666666668 -warp {{3.9938399876149333e-07 -0.004360090568130914 -0.0008108502136328084} {0 0.0 0}} -material 1 -section 1
fiber  -area 9.375e-05 -y -0.02291666666666667 -z 0.0016666666666666668 -warp {{-3.758447917597459e-05 -0.006111163070533127 0.025966771664935145} {0 0.0 0}} -material 1 -section 1
fiber  -area 9.375000000000002e-05 -y -0.043750000000000004 -z 0.0016666666666666668 -warp {{-5.510467686894079e-05 -0.0016044726251488821 0.04200539237768641} {0 0.0 0}} -material 1 -section 1
fiber  -area 6.250000000000003e-05 -y 0.03229166666666667 -z -0.0016666666666666668 -warp {{-4.450046555907564e-05 0.005381950474960816 -0.03445349069293446} {0 0.0 0}} -material 1 -section 1
fiber  -area 6.249999999999999e-05 -y 0.04583333333333334 -z -0.0016666666666666668 -warp {{-5.9207904517633025e-05 0.001833164659856833 -0.04303346827213562} {0 0.0 0}} -material 1 -section 1

geomTransf Linear 1 0 0 1 
element ExactFrame 1 {1 2} -section 1 -shear 1 -transform 1
element ExactFrame 2 {2 3} -section 1 -shear 1 -transform 1
element ExactFrame 3 {3 4} -section 1 -shear 1 -transform 1
element ExactFrame 4 {4 5} -section 1 -shear 1 -transform 1
element ExactFrame 5 {5 6} -section 1 -shear 1 -transform 1
element ExactFrame 6 {6 7} -section 1 -shear 1 -transform 1
element ExactFrame 7 {7 8} -section 1 -shear 1 -transform 1
element ExactFrame 8 {8 9} -section 1 -shear 1 -transform 1
pattern Plain 1 Linear 
eleLoad Frame Heaviside -basis local -force {0 0 20000.0} -pattern 1 -elements {1 2 3 4 5 6 7 8}

system Umfpack 
integrator LoadControl 0.05 
test Energy 1e-16 10 0 
algorithm Newton 
analysis Static 
analyze 20

nodeDisp 5 3 

reactions  
nodeResponse 1 3 reactionForce 
nodeResponse 2 3 reactionForce 
nodeResponse 3 3 reactionForce 
nodeResponse 4 3 reactionForce 
nodeResponse 5 3 reactionForce 
nodeResponse 6 3 reactionForce 
nodeResponse 7 3 reactionForce 
nodeResponse 8 3 reactionForce 
nodeResponse 9 3 reactionForce 

