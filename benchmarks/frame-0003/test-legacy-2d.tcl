#
# Simply supported beam with distributed loads
#

verify about "2D Frame element loads"
set E 30000.0
set A 20.0
set I 1400.0

set L  100.0
set beta 0.2
set lp [expr $beta*$L]

# Point loads
set P 200.0
set N 150.0
set aL 0.4
set a [expr $aL*$L]

# Distributed loads
set wt 3.0
set wa 2.0

set nIP 5

set elements {1 2 3 5}

foreach element $elements {
	
    model basic -ndm 2 -ndf 3
	
    node 1 0.0 0.0
    node 2  $L 0.0
    
    fix 1 1 1 0
    fix 2 0 1 0

    section Elastic 1 $E $A $I
    
    geomTransf Linear 1
    
    switch $element {
	1 {
	    puts "   ElasticBeamColumn"
	    element elasticBeamColumn 1 1 2 $A $E $I 1
	}
	2 {
	    puts "   DispBeamColumn"
	    element dispBeamColumn 1 1 2 $nIP 1 1
	}
	3 {
	    puts "   NonlinearBeamColumn"
	    element nonlinearBeamColumn 1 1 2 $nIP 1 1
	}
	4 {
	    puts "   BeamWithHinges"
	    element beamWithHinges 1 1 2 1 $lp 1 $lp $E $A $I 1
	}
	5 {
	    puts "   PrismFrame"
	    element PrismFrame 1 1 2 $A $E $I 1
	}
    }
    
    pattern Plain 1 "Constant" {
	set P2 [expr $P/2]
	set N2 [expr $N/2]
	
	eleLoad -ele 1 -type -beamPoint $P2 $aL $N2
	eleLoad -ele 1 -type -beamPoint $P2 $aL $N2

	set wt2 [expr $wt/2]
	set wa2 [expr $wa/2]
	
	eleLoad -ele 1 -type -beamUniform $wt2 $wa2
	eleLoad -ele 1 -type -beamUniform $wt2 $wa2
    }

    test NormUnbalance 1.0e-10 10 0
    algorithm Newton
    integrator LoadControl 1.0
    constraints Plain
    system ProfileSPD
    numberer Plain
    analysis Static
    
    verify value [analyze 2] 0
    

    set d1 [expr $aL*$N*$L/($E*$A)]
    set d2 [expr $wa*pow($L,2)/(2*$E*$A)]
#   verify "error" [nodeDisp 2 1] [expr $d1+$d2] 1e-2 "axial"

    set V1 [expr $P*(1-$aL)]
    set d1 [expr -$V1/(6*$E*$I*$L)*($a*$a*$L-2*$a*$L*$L)]
    set d2 [expr $wt*pow($L,3)/(24*$E*$I)]
    verify "error" [nodeDisp 1 3] [expr $d1+$d2] 2e-2 "rotation i"

    set d1 [expr -$V1/(6*$E*$I*$L)*($a*$a*$L+$a*$L*$L)]
    verify "error" [nodeDisp 2 3] [expr $d1-$d2] 2e-2 "rotation j"

    wipe
}
