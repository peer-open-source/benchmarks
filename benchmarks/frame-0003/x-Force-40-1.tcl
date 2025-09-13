#
# AISC Benchmark Problem, Case 1 (with shear)
#
# AISC 360-16, Commentary Figure C-C2.2
#
# Pinned-pinned column with uniform lateral load of 0.200 kip/ft and varying axial load
#
model Basic -ndm 3 -ndf 6
# Linearly spaced nodes from 0 to 336.0*inch
node  1   0.0 0 0 
node  2   8.4 0 0 
node  3  16.8 0 0 
node  4  25.2 0 0 
node  5  33.6 0 0 
node  6  42.0 0 0 
node  7  50.4 0 0 
node  8  58.8 0 0 
node  9  67.2 0 0 
node 10  75.6 0 0 
node 11  84.0 0 0 
node 12  92.4 0 0 
node 13 100.8 0 0 
node 14 109.2 0 0 
node 15 117.6 0 0 
node 16 126.0 0 0 
node 17 134.4 0 0 
node 18 142.8 0 0 
node 19 151.2 0 0 
node 20 159.6 0 0 
node 21 168.0 0 0 
node 22 176.4 0 0 
node 23 184.8 0 0 
node 24 193.2 0 0 
node 25 201.6 0 0 
node 26 210.0 0 0 
node 27 218.4 0 0 
node 28 226.8 0 0 
node 29 235.2 0 0 
node 30 243.6 0 0 
node 31 252.0 0 0 
node 32 260.4 0 0 
node 33 268.8 0 0 
node 34 277.2 0 0 
node 35 285.6 0 0 
node 36 294.0 0 0 
node 37 302.4 0 0 
node 38 310.8 0 0 
node 39 319.2 0 0 
node 40 327.6 0 0 
node 41 336.0 0 0

fix  1 1 1 1 1 0 0 
fix 41 0 1 1 1 0 0 

section ElasticFrame 1 -Iy 484.0 -Iz 51.4 -A 14.1 -Az 4.692 -Ay 4.777849999999999 -J 1.45 -Cw 2240.0 -E 29000.0 -G 11200.0

geomTransf Corotational02 1 0 0 1 
element ForceFrame  1 { 1  2} -section 1 -shear 1 -transform 1
element ForceFrame  2 { 2  3} -section 1 -shear 1 -transform 1
element ForceFrame  3 { 3  4} -section 1 -shear 1 -transform 1
element ForceFrame  4 { 4  5} -section 1 -shear 1 -transform 1
element ForceFrame  5 { 5  6} -section 1 -shear 1 -transform 1
element ForceFrame  6 { 6  7} -section 1 -shear 1 -transform 1
element ForceFrame  7 { 7  8} -section 1 -shear 1 -transform 1
element ForceFrame  8 { 8  9} -section 1 -shear 1 -transform 1
element ForceFrame  9 { 9 10} -section 1 -shear 1 -transform 1
element ForceFrame 10 {10 11} -section 1 -shear 1 -transform 1
element ForceFrame 11 {11 12} -section 1 -shear 1 -transform 1
element ForceFrame 12 {12 13} -section 1 -shear 1 -transform 1
element ForceFrame 13 {13 14} -section 1 -shear 1 -transform 1
element ForceFrame 14 {14 15} -section 1 -shear 1 -transform 1
element ForceFrame 15 {15 16} -section 1 -shear 1 -transform 1
element ForceFrame 16 {16 17} -section 1 -shear 1 -transform 1
element ForceFrame 17 {17 18} -section 1 -shear 1 -transform 1
element ForceFrame 18 {18 19} -section 1 -shear 1 -transform 1
element ForceFrame 19 {19 20} -section 1 -shear 1 -transform 1
element ForceFrame 20 {20 21} -section 1 -shear 1 -transform 1
element ForceFrame 21 {21 22} -section 1 -shear 1 -transform 1
element ForceFrame 22 {22 23} -section 1 -shear 1 -transform 1
element ForceFrame 23 {23 24} -section 1 -shear 1 -transform 1
element ForceFrame 24 {24 25} -section 1 -shear 1 -transform 1
element ForceFrame 25 {25 26} -section 1 -shear 1 -transform 1
element ForceFrame 26 {26 27} -section 1 -shear 1 -transform 1
element ForceFrame 27 {27 28} -section 1 -shear 1 -transform 1
element ForceFrame 28 {28 29} -section 1 -shear 1 -transform 1
element ForceFrame 29 {29 30} -section 1 -shear 1 -transform 1
element ForceFrame 30 {30 31} -section 1 -shear 1 -transform 1
element ForceFrame 31 {31 32} -section 1 -shear 1 -transform 1
element ForceFrame 32 {32 33} -section 1 -shear 1 -transform 1
element ForceFrame 33 {33 34} -section 1 -shear 1 -transform 1
element ForceFrame 34 {34 35} -section 1 -shear 1 -transform 1
element ForceFrame 35 {35 36} -section 1 -shear 1 -transform 1
element ForceFrame 36 {36 37} -section 1 -shear 1 -transform 1
element ForceFrame 37 {37 38} -section 1 -shear 1 -transform 1
element ForceFrame 38 {38 39} -section 1 -shear 1 -transform 1
element ForceFrame 39 {39 40} -section 1 -shear 1 -transform 1
element ForceFrame 40 {40 41} -section 1 -shear 1 -transform 1


pattern Plain 1 Constant 
eleLoad Frame Heaviside -basis global -force {0 0 0.016666666666666666} -pattern 1 \
  -elements {1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40}

system Umfpack 
test Energy 1e-18 10 2 
algorithm Newton 
analysis Static 
analyze 1 
loadConst  -time 0
nodeDisp 21 3 
pattern Plain 2 Linear {
  load 41 -1 0 0 0 0 0 ;
}
integrator LoadControl 150.0 
analyze 1 
nodeDisp 21 3 

analyze 1
nodeDisp 21 3 

analyze 1 
nodeDisp 21 3 
