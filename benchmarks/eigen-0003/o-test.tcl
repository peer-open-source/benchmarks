set A 216
set Iz 2592
set Iy 5832
set J 6085.12013626099
set E 3600
set G 1500
set L 96.0
set m [expr 4.968e-05*$L]

model Basic -ndm 3 -ndf 6

node 1  0 0 0 ; # Joint=1
node 2 $L 0 0 ; # Joint=2

fix 1  1 1 1 1 1 1 
fix 2  1 0 0 1 0 0; # -dof 1, 4

mass 1 $m $m $m 0 0 0
mass 2 $m $m $m 0 0 0


section Elastic 1 $E $A $Iz $Iy $J $G

# Elements
geomTransf Linear 1 0.0 0.0 1.0 
element forceBeamColumn 1 1 2  1 Legendre 1 8;


constraints Transformation 
system BandGeneral 
numberer RCM


analysis Static

set ev [eigen  -genBandArpack 2]

puts $ev
