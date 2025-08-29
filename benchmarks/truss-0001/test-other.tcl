# This Extends PlanarTruss.tcl verification test to:
#
#   1) run different element options to test: TrussSection and FiberSection2d And Uniaxial Section
#   2) run different solver options to test:

# Plane 3bar Truss Example

#
# planar 3 bar system, all bars same A & E, unit load P acing
#

verify about "2d Linear and Nonlinear Truss Example by Popov"

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
set F2    [expr  $F1*$cosA*$cosA]
set disp  [expr -$F1*$L/($A*$E)]



set b 1.0; set d $A;
set z $A; set y 1.0;

set numFiberY 10;  # note we only need so many to get the required accuracy on eigenvalue 1e-7!
set numFiberZ 1;

# create the finite element model
foreach sectType {Fiber Uniaxial} {

    verify about "Linear (Example 2.14) sectType: $sectType"
    

    wipe
    
    model Basic -ndm 2 -ndf 2
    
    set dX [expr $L*tan($alphaRad)]
    
    node 1    0.0          0.0
    node 2    $dX          0.0
    node 3 [expr 2.0*$dX]  0.0
    node 4    $dX         -$L     
    
    fix 1 1 1
    fix 2 1 1
    fix 3 1 1
    
    if {$sectType == "Uniaxial"} {
        uniaxialMaterial Elastic 1 [expr $A*$E]
        section Uniaxial 1 1 P
    } else {
        uniaxialMaterial Elastic 1 $E
        section Fiber 1 {	
    #       patch rect 1 $numFiberY $numFiberZ [expr -$z/2.0] [expr -$y/2.0] [expr $z/2.0] [expr $y/2.0]	    
            patch rect 1 $numFiberY $numFiberZ [expr -$z] [expr -$y] [expr 0.] [expr 0.]	    
        }
    }

    element Truss 1 1 4 1
    element Truss 2 2 4 1
    element Truss 3 3 4 1
    
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
    
    #
    # print table of camparsion
    #          
    
    eval "set comparisonResults {$F2 $F1 $F2}"
    set tol 1.0e-6

    for {set i 1} {$i<4} {incr i 1} {
        set exactResult [lindex $comparisonResults [expr $i-1]]
        verify value [eleResponse $i axialForce] $exactResult $tol
    }
    
    set osDisp [nodeDisp 4 2]
    verify value [nodeDisp 4 2] $disp $tol
    
    verify about "NonLinear (Example2.23), Section: $sectType"
    
    # Exact per Popov
    
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

    if {$sectType == "Uniaxial"} {
        uniaxialMaterial ElasticPP 1 [expr $A*$E] [expr $sigmaYP/$E]
        section Uniaxial 1 1 P
    } else {
        uniaxialMaterial ElasticPP 1 [expr $E] [expr $sigmaYP/$E]
        section Fiber 1 {	
            patch rect 1 $numFiberY $numFiberZ [expr -$z/2.0] [expr -$y/2.0] [expr $z/2.0] [expr $y/2.0]	    
        }
    }

    element Truss 1 1 4 1
    element Truss 2 2 4 1
    element Truss 3 3 4 1
    
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
    verify value [nodeDisp 4 2] $dispA $tol
    
    analyze 1
    verify value [nodeDisp 4 2] $dispB $tol
}

