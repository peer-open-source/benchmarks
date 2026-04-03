#
# Simply supported beam with distributed loads. Euler-bernoulli theory
#

verify about "3D Frame with distributed loads"

set E  30000.0
set A  20.0
set Iz 1400.0
set Iy 1200.0
set G  18000.0
set J  [expr $Iz+$Iy]

set L  100.0
set beta 0.2
set lp [expr $beta*$L]

# Point loads
set Py 200.0
set Pz 250.0
set N  150.0
set aL 0.6
set a  [expr $aL*$L]

# Distributed loads
set wy 3.0
set wz 4.0
set wx 2.0

set nIP 5

set elements {6 6} ;

proc printRow {quantity expected computed} {
  verify error $computed $expected 2e-2 $quantity
}

wipe
foreach element $elements {

    model basic -ndm 3 -ndf 6

    node 1 0.0 0.0 0.0
    node 2  $L 0.0 0.0

    fix 1 1 1 1 1 0 0
    fix 2 0 1 1 0 0 0  

    set sec 1
    section ElasticFrame 1 $E $A $Iz $Iy $G $J
    
    geomTransf Linear 1 0 0 1
    
    switch $element {
      6 {
          puts "   ForceFrame"
          element ForceFrame 1 1 2 $nIP 1 1  -shear 0
      }
    }
    
    pattern Plain 1 "Constant" {
        set Py2 [expr $Py/2]
        set Pz2 [expr $Pz/2]
        set N2  [expr $N/2]
        eleLoad Frame Point -element {1} -offset "$aL 0 0" -force "$N2 $Py2 $Pz2"
        eleLoad Frame Point -element {1} -offset "$aL 0 0" -force "$N2 $Py2 $Pz2"
  
        set wy2 [expr $wy/2]
        set wz2 [expr $wz/2]
        set wx2 [expr $wx/2]
        eleLoad Frame Uniform -element {1} -force "$wx2 $wy2 $wz2"
        eleLoad Frame Uniform -element {1} -force "$wx2 $wy2 $wz2"
    }

    set niter 4
    test NormUnbalance 1.0e-10 $niter ; #4
    algorithm Newton
    integrator LoadControl 1.0
    constraints Plain
    system ProfileSPD
    numberer Plain
    analysis Static

    verify value [analyze 2] 0


    set d1 [expr $aL*$N*$L/($E*$A)]
    set d2 [expr $wx*pow($L,2)/(2*$E*$A)]

#   printRow "axial" [expr $d1+$d2] [nodeDisp 2 1]

    set Vy [expr $Py*(1-$aL)]
    set Vz [expr $Pz*(1-$aL)]

    #
    set d1 [expr -$Vy/(6*$E*$Iz*$L)*($a*$a*$L-2*$a*$L*$L)]
    set d2 [expr $wy*pow($L,3)/(24*$E*$Iz)]

    printRow "theta_zi" [expr $d1+$d2] [nodeDisp 1 6]

    set d1 [expr -$Vy/(6*$E*$Iz*$L)*($a*$a*$L+$a*$L*$L)]

    printRow "theta_zj" [expr $d1-$d2] [nodeDisp 2 6]

    #
    set d1 [expr $Vz/(6*$E*$Iy*$L)*($a*$a*$L-2*$a*$L*$L)]
    set d2 [expr -$wz*pow($L,3)/(24*$E*$Iy)]

    printRow "theta_yi" [expr $d1+$d2] [nodeDisp 1 5]

    set d1 [expr -$Vz/(6*$E*$Iy*$L)*($a*$a*$L+$a*$L*$L)]

    printRow "theta_yj" [expr (-1*$d1)-($d2)] [nodeDisp 2 5]

    wipe
}
