# Chopra Example 5.4
#
# Constant average acceleration
#

set dt 0.1
set N  10


set k 10
set m 0.2533
set z 0.05
set wn 6.283

#
# Define model with k
#
wipe
model basic -ndm 1 -ndf 1;

node 1 0;
node 2 0 -mass $m;

fix 1 1;

uniaxialMaterial Elastic 1 $k;
element zeroLength 1 1 2 -mat 1 -dir 1;
rayleigh [expr 2.0*$wn*$z] 0.0 0.0 0.0


timeSeries Path  1  -dt  $dt  -values {*}{
   0.0000
   5.0000
   8.6603
  10.0000
   8.6603
   5.0000
   0.0000
   0.0000
   0.0000
   0.0000
   0.0000
}

pattern UniformExcitation 1 1 -accel 1 -factor [expr -1/$m];

#
# Define analysis options
#
algorithm Newton
test NormDispIncr 1e-14 2 0
integrator Newmark 0.5 0.25;
analysis Transient;

analyze $N $dt;

verify value [nodeAccel 2] 47.3701 1e-2
verify value [nodeVel 2]   -3.5026 1e-2
verify value [nodeDisp 2]  -1.1441 1e-2
#
