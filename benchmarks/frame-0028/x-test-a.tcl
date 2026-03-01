set L 48
set h 6
set w 0.001
set E 29000
set G 12000

set A  [expr {$h*$h}]
set Ay [expr {$A*500}]
set Az [expr {$A*500}]
set I  [expr {$h*$h*$h*$h/12}]
set J  [expr {$I*2}]
# Equivalent distributed couple
set m  [expr {($h/2)*$w}]

  model basic -ndm 3 -ndf 6
  node 1 0 0 0 
  node 2 [expr {$L/2}] 0 0 
  node 3 $L 0 0 
  fix 1 1 1 1 1 1 1 

  geomTransf Linear 1 0 -1 0 
  section ElasticFrame 1 \
        -E $E -G $G \
        -A $A -Ay $Ay -Az $Az \
        -J $J -Iy $I  -Iz $I

  element ExactFrame 1 {1 2 3} -section 1 -transform 1

  pattern Plain 1 Constant 

  eleLoad Frame Heaviside \
    -basis local \
    -force "$w 0 0" \
    -couple "0 -$m 0" \
    -pattern 1 \
    -elements 1

  # Analyze
  analysis Static
  analyze 1
  reactions


  verify value [nodeDisp 3 6] [expr {-($m*$L*$L/(2*$E*$I))}] 1e-4 "Displacement"
  verify value [nodeDisp 3 2] [expr {-($m*$L*$L*$L/(3*$E*$I))}] 1e-4 "Displacement"
  verify value [nodeReaction 1 6] [expr {$m*$L}] 1e-4
  wipe
