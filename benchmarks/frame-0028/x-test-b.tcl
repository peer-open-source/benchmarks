set L 48
set E 29000
set h 6
set A [expr {$h*$h}]
set I [expr {$h*$h*$h*$h/12}]
set w 0.001
set m [expr {($h/2)*$w}]

model basic -ndm 3 -ndf 6
node 1 0 0 0 
node 2 [expr {$L/2}] 0 0 
node 3 $L 0 0 
fix 1 1 1 1 1 1 1 

geomTransf Linear 1 0 0 1 
section ElasticFrame 1 -E 29000 -A 36 -Iy 108.0 -Iz 108.0 -G 12000 -J 216.0 -Ay 18000 -Az 18000

element ExactFrame 1 {1 2 3} -section 1 -transform 1

pattern Plain 1 Constant 

eleLoad Frame Heaviside \
  -basis local \
  -force "$w 0 0" \
  -offset "0 [expr {$h/2}] 0" \
  -pattern 1 \
  -elements 1

analysis Static 
analyze 1 
reactions  


verify value [nodeReaction 1 6] [expr {$m*$L}] 1e-4
verify value [nodeDisp 3 6] [expr {-($m*$L*$L/(2*$E*$I))}] 1e-4
verify value [nodeDisp 3 2] [expr {-($m*$L*$L*$L/(3*$E*$I))}] 1e-4
