# Plane 3-bar Truss Example
#
# REFERENCES: 
#
# 1) Popov, E. "Engineering Mechanics of Solids", Prentice Hall, 1990.
#      Linear: Example 2.14 
#      NonLinear: Example 2.23 
#
verify about "Linear Truss (Example 2.14)"
#
# planar 3 bar system, all bars same A & E, unit load P acing
#
set A 10.0
set E 3000.
set L 200.0
set alpha 30.0
set P 200.0

set sigmaYP 60.0

set pi [expr 2.0*asin(1.0)]
set alphaRad [expr $alpha*$pi/180.]
set cosA [expr cos($alphaRad)]
set sinA [expr sin($alphaRad)]

# EXACT RESULTS per Popov
set F1    [expr $P/(2*$cosA*$cosA*$cosA + 1)]
set F2    [expr $F1*$cosA*$cosA]
set disp  [expr -$F1*$L/($A*$E)]

# create the finite element model
wipe

model Basic -ndm 2 -ndf 2

set dX [expr $L*tan($alphaRad)]

node 1    0.0          0.0
node 2    $dX          0.0
node 3 [expr 2.0*$dX]  0.0
node 4    $dX          -$L

fix 1 1 1
fix 2 1 1
fix 3 1 1

uniaxialMaterial Elastic 1 $E
element Truss 1 1 4 $A 1
element Truss 2 2 4 $A 1
element Truss 3 3 4 $A 1

timeSeries Linear 1
pattern Plain 1 1 {
    load 4 0. -$P
}

numberer Plain
constraints Plain
algorithm Linear
system ProfileSPD
integrator LoadControl 1.0
analysis Static
analyze 1


# determine PASS/FAILURE of test
set testOK 0

#
# print table of camparsion
#          

eval "set comparisonResults {$F2 $F1 $F2}"
set tol 1.0e-6
for {set i 1} {$i<4} {incr i 1} {
    set exactResult [lindex $comparisonResults [expr $i-1]]
    set eleForce [eleResponse $i axialForce]
    verify value $eleForce $exactResult $tol
}

verify value [nodeDisp 4 2] $disp $tol "displacements"


#
#
#
verify about "NonLinear (Example 2.23)"
#
# Exact per Popov
#
set PA [expr ($sigmaYP*$A) * (1.0+2*$cosA*$cosA*$cosA)]
set dispA [expr $PA/$P*$disp]

set PB [expr ($sigmaYP*$A) * (1.0+2*$cosA)]
set dispB [expr $dispA / ($cosA*$cosA)]

# create the new finite element model for nonlinear case
#   will apply failure loads and calculate displacements

wipe

model Basic -ndm 2 -ndf 2

node 1    0.0          0.0
node 2    $dX          0.0
node 3 [expr 2.0*$dX]  0.0
node 4    $dX         -$L     

fix 1 1 1
fix 2 1 1
fix 3 1 1

uniaxialMaterial ElasticPP 1 $E [expr $sigmaYP/$E]
element Truss 1 1 4 $A 1
element Truss 2 2 4 $A 1
element Truss 3 3 4 $A 1

eval "timeSeries Path 1 -dt 1.0 -values {0.0 $PA $PB $PB}"
pattern Plain 1 1 {
    load 4 0. -1.0
}

numberer Plain
constraints Plain
algorithm Linear
system ProfileSPD
integrator LoadControl 1.0
analysis Static
analyze 1

set osDispA [nodeDisp 4 2]
#print node 4
#print ele

analyze 1
set osDispB [nodeDisp 4 2]

set osDisp [nodeDisp 4 2]

verify value $osDispA $dispA $tol "elastic limit state"
verify value $osDispB $dispB $tol "collapse limit state"

