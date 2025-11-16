# https://openseesdigital.com/2025/02/23/two-node-links-awakening/
set kt 10.0; # translational stiffness
set kr 20.0; # rotational stiffness
set P   5.0; # applied load
set L  10.0; # length of the link
set c  0.5; # shear distance

model basic -ndm 2 -ndf 3 
uniaxialMaterial Elastic 1 $kt
uniaxialMaterial Elastic 2 $kr

node 0 0  0 
node 1 0  0 
node 2 0 $L
fix 0 1 1 1
fix 1 0 1 0
fix 2 0 1 0

element zeroLength 1 0 1 -mat 1 2 -dir 2 3 -orient 0 1 0
element twoNodeLink 2 0 2 -mat 1 2 -dir 2 3 -shearDist $c 

pattern Plain 1 Constant {
    load 1 $P 0 0;
    load 2 $P 0 0;
}
analysis Static 
analyze 1 

verify value [nodeDisp 1 1] [expr $P/$kt] 1e-8
verify value [nodeDisp 2 1] [expr $P/$kt + $P*($L*(1.0 - $c))**2/$kr] 1e-8
verify value [nodeDisp 1 3] [expr 0.0] 1e-8
verify value [nodeDisp 2 3] [expr -$P*$L*(1.0-$c)/$kr] 1e-8
