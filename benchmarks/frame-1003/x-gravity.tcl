
foreach element {ExactFrame ForceFrame} {
  model Basic -ndm 3 -ndf 6
  node 1 0.0 0 0 
  node 2 0.025 0 0 
  node 3 0.05 0 0 
  node 4 0.075 0 0 
  node 5 0.1 0 0 
  node 6 0.125 0 0 
  node 7 0.15 0 0 
  node 8 0.175 0 0 
  node 9 0.2 0 0 
  node 10 0.225 0 0 
  node 11 0.25 0 0 
  node 12 0.275 0 0 
  node 13 0.3 0 0 
  node 14 0.325 0 0 
  node 15 0.35 0 0 
  node 16 0.375 0 0 
  node 17 0.4 0 0 
  node 18 0.425 0 0 
  node 19 0.45 0 0 
  node 20 0.475 0 0 
  node 21 0.5 0 0 
  fix 1 1 1 1 1 0 0 
  fix 21 0 1 1 1 0 0 

  section ElasticFrame 1 -E 220000000000.0 -G 86614173228.34645 \
    -A 0.005 -Iy 4.166666666666666e-08 -Iz 0.00010416666666666665 -J 4.4163560812272547e-07 \
    -Cw 8.637324011818135e-10 -Ry -1.1651800045506732e-15 -Rz -1.9949319973733282e-17 -Sy 0.0 -Sz 0.0

  geomTransf Corotational02 1 0 0 1 

  element $element 1 {1 2} -section 1 -shear 1 -transform 1
  element $element 2 {2 3} -section 1 -shear 1 -transform 1
  element $element 3 {3 4} -section 1 -shear 1 -transform 1
  element $element 4 {4 5} -section 1 -shear 1 -transform 1
  element $element 5 {5 6} -section 1 -shear 1 -transform 1
  element $element 6 {6 7} -section 1 -shear 1 -transform 1
  element $element 7 {7 8} -section 1 -shear 1 -transform 1
  element $element 8 {8 9} -section 1 -shear 1 -transform 1
  element $element 9 {9 10} -section 1 -shear 1 -transform 1
  element $element 10 {10 11} -section 1 -shear 1 -transform 1
  element $element 11 {11 12} -section 1 -shear 1 -transform 1
  element $element 12 {12 13} -section 1 -shear 1 -transform 1
  element $element 13 {13 14} -section 1 -shear 1 -transform 1
  element $element 14 {14 15} -section 1 -shear 1 -transform 1
  element $element 15 {15 16} -section 1 -shear 1 -transform 1
  element $element 16 {16 17} -section 1 -shear 1 -transform 1
  element $element 17 {17 18} -section 1 -shear 1 -transform 1
  element $element 18 {18 19} -section 1 -shear 1 -transform 1
  element $element 19 {19 20} -section 1 -shear 1 -transform 1
  element $element 20 {20 21} -section 1 -shear 1 -transform 1

  pattern Plain 1 Linear 
  eleLoad Frame Uniform \
    -basis reference \
    -force {0 0 4000000.0} -pattern 1 \
    -elements {1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20}

  system BandGeneral 
  integrator LoadControl 0.025 
  test Energy 1e-16 15 1
  algorithm Newton 
  analysis Static 
  analyze 40
  verify error [nodeDisp 11 3] 0.1605 1e-2 uz
  wipe
}

