
model BasicBuilder -ndm 3 -ndf 6

set E  29000.0
set G  11200.0
set A   13.843100000000064
set Iy 473.65597600916794
set Iz  51.38797996416682
set J    1.2779522608827847

node 0  0.0 0 0 
node 1 55.2 0 0 
fix  0 1 1 1 1 1 1 

section Elastic 1 $E $A $Iz  $Iy $G $J
geomTransf Linear 1 0 0 1 
set section 1
set nip 5
set transform 1
element dispBeamColumn 1 0 1  $nip $section $transform

pattern Plain 1 Linear {
  load 1 0 0 1 0 0 0 ;
}


integrator LoadControl 10 
analysis Static 
test NormUnbalance 1e-10 3 
analyze 1 
