
model Basic -ndm 3 -ndf 6
node 1 0.0 0 0 
node 2 0.03125 0 0 
node 3 0.0625 0 0 
node 4 0.09375 0 0 
node 5 0.125 0 0 
node 6 0.15625 0 0 
node 7 0.1875 0 0 
node 8 0.21875 0 0 
node 9 0.25 0 0 
node 10 0.28125 0 0 
node 11 0.3125 0 0 
node 12 0.34375 0 0 
node 13 0.375 0 0 
node 14 0.40625 0 0 
node 15 0.4375 0 0 
node 16 0.46875 0 0 
node 17 0.5 0 0 
fix 1 1 1 1 1 0 0 
fix 17 1 1 1 1 0 0 

material ElasticIsotropic 1 -E 220000000000.0 -G 84615384615.38461
section ElasticFrame 1 -E 220000000000.0 -G 84615384615.38461 -A 0.0010000000000000002 -Ay 0.0010000000000000002 -Az 0.0010000000000000002 -Qy 9.26442286059391e-23 -Qz -4.235164736271502e-22 -Iy 8.333333333333335e-09 -Iz 8.333333333333335e-07 -J 7.12735330294834e-08 -Ry 1.665478532538768e-18 -Rz 1.9083652301639387e-18 -Sy 1.5900608571771286e-23 -Sz 4.280135669309531e-11
geomTransf Linear 1 0 0 1 

element ExactFrame 1 {1 2 3} -section 1 -shear 1 -transform 1
element ExactFrame 2 {3 4 5} -section 1 -shear 1 -transform 1
element ExactFrame 3 {5 6 7} -section 1 -shear 1 -transform 1
element ExactFrame 4 {7 8 9} -section 1 -shear 1 -transform 1
element ExactFrame 5 {9 10 11} -section 1 -shear 1 -transform 1
element ExactFrame 6 {11 12 13} -section 1 -shear 1 -transform 1
element ExactFrame 7 {13 14 15} -section 1 -shear 1 -transform 1
element ExactFrame 8 {15 16 17} -section 1 -shear 1 -transform 1
pattern Plain 1 Linear
eleLoad Frame Heaviside -basis local -force {0 0 20000.0} -pattern 1 -elements {1 2 3 4 5 6 7 8}
system Umfpack 
integrator LoadControl 0.05 
test Energy 1e-16 8 0
algorithm Newton 
analysis Static 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
analyze 1 
nodeDisp 9 3 
reactions  

