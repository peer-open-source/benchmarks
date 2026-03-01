set L 48
set h 6
set N 0.01
set T 0.01
set E 29000
set G 12000

set A  [expr {$h*$h}]
set Ay [expr {$A*500}]
set Az [expr {$A*500}]
set I  [expr {$h*$h*$h*$h/12}]
set J  [expr {$I*2}]

foreach element {ExactFrame ForceFrame } {
  model basic -ndm 3 -ndf 6
  node 1 0 0 0 
  node 2 $L 0 0 
  fix 1 1 1 1 1 1 1 

  geomTransf Linear 1 0 -1 0 
  section ElasticFrame 1 \
        -E $E -G $G \
        -A $A -Ay $Ay -Az $Az \
        -J $J -Iy $I  -Iz $I

  element $element 1 {1 2} -section 1 -transform 1

  pattern Plain 1 Constant 

  eleLoad Frame Point \
    -basis local \
    -force "$N 0 0" \
    -couple "$T 0 0" \
    -offset "1 0 0" \
    -pattern 1 \
    -elements 1

  # Analyze
  analysis Static
  analyze 1
  reactions


  verify value [nodeDisp 2 1] [expr {$L*$N/($E*$A)}] 1e-4 "Displacement"
  verify value [nodeDisp 2 4] [expr {$L*$T/($G*$J)}] 1e-4 "Rotation"
  wipe
}
