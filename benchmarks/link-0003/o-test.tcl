# https://openseesdigital.com/2025/02/23/two-node-links-awakening/

set kt 10.0   ;# Translational stiffness
set kr 20.0   ;# Rotational stiffness
set P  5.0    ;# Load
set L  10.0   ;# Link length
set c  0.5    ;# Shear distance

wipe
model basic -ndm 2 -ndf 3

node 0 0.0 0.0
fix 0 1 1 1

uniaxialMaterial Elastic 1 $kt
uniaxialMaterial Elastic 2 $kr

node 1 0.0 0.0
fix 1 0 1 0
element zeroLength 1 0 1 -mat 1 2 -dir 2 3 -orient 0 1 0  -1 0 0

node 2 0.0 $L
fix 2 0 1 0
element twoNodeLink 2 0 2 -mat 1 2 -dir 2 3 -shearDist $c

timeSeries Constant 1
pattern Plain 1 1 {
    load 1 $P 0.0 0.0
    load 2 $P 0.0 0.0
}

constraints Plain
numberer Plain
system BandGeneral
test NormUnbalance 1.0e-12 10
algorithm Newton
integrator LoadControl 1.0
analysis Static
analyze 1


# X-displacement
set u1 [nodeDisp 1 1]
set u2 [nodeDisp 2 1]

set exact1 [expr {$P/$kt}]
set exact2 [expr {$P/$kt + $P*$L*(1.0-$c)/$kr*$L*(1.0-$c)}]

set tol 1.0e-10
if {abs($u1 - $exact1) > $tol} {
    error "u1 check failed: got $u1 expected $exact1"
}
if {abs($u2 - $exact2) > $tol} {
    error "u2 check failed: got $u2 expected $exact2"
}

# Rotation
set u1 [nodeDisp 1 3]
set u2 [nodeDisp 2 3]

set exact1 0.0
set exact2 [expr {-$P*$L*(1.0-$c)/$kr}]


if {abs($u1 - $exact1) > $tol} {
    error "rot1 check failed: got $u1 expected $exact1"
}
if {abs($u2 - $exact2) > $tol} {
    error "rot2 check failed: got $u2 expected $exact2"
}
