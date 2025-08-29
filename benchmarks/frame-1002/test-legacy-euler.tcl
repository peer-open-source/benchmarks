
model Basic -ndm 3 -ndf 6

set E 29000.0
set G 11153.846153846154
set A    33.4452
set Iy 2255.8332985200004
set Iz   93.72731163999973
set J    12.819369381331398

section Elastic 1 $E $A $Iy  $Iz $G $J

geomTransf Corotational 1 0 0 1 

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

element forceBeamColumn 1 0 1 5  1  1
element forceBeamColumn 2 1 2 5  1  1
element forceBeamColumn 3 2 3 5  1  1
element forceBeamColumn 4 3 4 5  1  1
element forceBeamColumn 5 4 5 5  1  1
element forceBeamColumn 6 5 6 5  1  1
element forceBeamColumn 7 6 7 5  1  1
element forceBeamColumn 8 7 8 5  1  1

pattern Plain 1 Linear {
  load 8 0 1 0 0 0 0
}

system BandGeneral 
constraints Plain
numberer RCM
integrator LoadControl 1.6666666666666665 
test NormUnbalance 1e-8 10 0
algorithm Newton 
analysis Static 

set avg_iter 0

for {set i 0} {$i < 201} {incr i} {
  analyze 1
  set n "[numIter].0"
  set avg_iter [expr $avg_iter+($n-$avg_iter)/($i+1)]
}

puts "average iterations = $avg_iter"
puts [nodeDisp 8 1]
puts [nodeDisp 8 2]

