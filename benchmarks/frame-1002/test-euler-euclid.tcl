set E 29000.0
set G 11153.846153846154
set A    33.4452
set Iy 2255.8332985200004
set Iz   93.72731163999973
set J    12.819369381331398

foreach element {ForceFrame PrismFrame} {
  wipe
  model  -ndm 3 -ndf 6

  section ElasticFrame 1 \
    -E 29000.0 \
    -G 11153.846153846154 \
    -A  33.44520000000007 \
    -Ay 33.44520000000007 \
    -Az 33.44520000000007 \
    -Iz 2255.8332985200004 \
    -Iy 93.72731163999973 \
    -J  12.819369381331398

  geomTransf Corotational02 1 0 0 1 

  node 0   0.0   0 0
  node 1  27.025 0 0 
  node 2  54.050 0 0 
  node 3  81.075 0 0 
  node 4 108.100 0 0 
  node 5 135.125 0 0 
  node 6 162.150 0 0 
  node 7 189.175 0 0 
  node 8 216.200 0 0 
  fix  0 1 1 1 1 1 1 
  fix  8 0 0 0 0 0 0 

  element $element 1  0 1 -section 1 -transform 1 -shear 0
  element $element 2  1 2 -section 1 -transform 1 -shear 0
  element $element 3  2 3 -section 1 -transform 1 -shear 0
  element $element 4  3 4 -section 1 -transform 1 -shear 0
  element $element 5  4 5 -section 1 -transform 1 -shear 0
  element $element 6  5 6 -section 1 -transform 1 -shear 0
  element $element 7  6 7 -section 1 -transform 1 -shear 0
  element $element 8  7 8 -section 1 -transform 1 -shear 0

  pattern Plain 1 Linear {
    load 8 0 1 0 0 0 0
  }

  #
  # Analysis
  #
  system Umfpack 
  integrator LoadControl 1.6666666666666665 
  test Residual 1e-08 10 0 
  algorithm Newton 
  analysis Static 

  set avg_iter 0

  for {set i 0} {$i < 201} {incr i} {
    nodeDisp 8 1 
    nodeDisp 8 2 
    if {[analyze 1] != 0} {
      break
    }
    set n "[numIter].0"
    set avg_iter [expr $avg_iter+($n-$avg_iter)/($i+1)]
  }

  puts "  average iterations = $avg_iter"
  verify value $avg_iter 2.9701492537313423
}
