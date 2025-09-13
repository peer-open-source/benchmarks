#
# AISC Benchmark Problem, Case 1 (with shear)
#
# AISC 360-16, Commentary Figure C-C2.2
#
# Pinned-pinned column with uniform lateral load of 0.200 kip/ft and varying axial load
#
model Basic -ndm 3 -ndf 6
node 1 0.0 0 0 
node 2 56.0 0 0 
node 3 112.0 0 0 
node 4 168.0 0 0 
node 5 224.0 0 0 
node 6 280.0 0 0 
node 7 336.0 0 0 
fix 1 1 1 1 1 0 0 
fix 7 0 1 1 1 0 0 
section ElasticFrame 1 -Iy 484.0 -Iz 51.4 -A 14.1 -Az 4.692 -Ay 4.777849999999999 -J 1.45 -Cw 2240.0 -E 29000.0 -G 11200.0
geomTransf Corotational02 1 0 0 1 
element ExactFrame 1 {1 2 3 4} -section 1 -shear 1 -transform 1
element ExactFrame 2 {4 5 6 7} -section 1 -shear 1 -transform 1

# Constant distributed load
pattern Plain 1 Constant 
eleLoad Frame Heaviside -basis global -force {0 0 0.016666666666666666} -pattern 1 -elements {1 2}


system Umfpack 
test Energy 1e-18 5
algorithm Newton 
analysis Static

# Analyze with only distributed load
analyze 1 
loadConst  -time 0
verify value [nodeDisp 4 3] 0.202 1e-2

# Axial loading
pattern Plain 2 Linear {
  load 7 -1 0 0 0 0 0 ;
}
integrator LoadControl 150.0 

analyze 1 
verify value [nodeDisp 4 3] 0.230 1e-2


analyze 1
verify value [nodeDisp 4 3] 0.269 1e-2

analyze 1 
verify value [nodeDisp 4 3] 0.322 1e-2

