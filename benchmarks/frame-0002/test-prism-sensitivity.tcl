
set L  5.0
set E  200000000000.0
set G   76923076923.07692
set A  0.016648999999999997
set Ay 1664.8999999999996
set Az 1664.8999999999996
set Iz 0.00040283077741666654
set Iy 0.00040283077741666654
set J  0.0008056615548333331

set H 300000.0

foreach element {PrismFrame ForceFrame} {
  puts "  $element"

  model Basic -ndm 3 -ndf 6
  node 1  0 0 0 
  node 2 $L 0 0 
  fix 1 1 1 1 1 1 1 

  section FrameElastic 1 -E $E -A $A -Ay $Ay -Az $Az -Iz $Iz -Iy $Iy -J $J -G $G

  geomTransf Linear 1 0 0 1 

  element $element 1 1 2 -section 1 -transform 1 -shear 0

  parameter 1 element 1 E 
  parameter 2 element 1 A 
  parameter 3 element 1 Iz 
  parameter 4 node 2 coord 1

  pattern Plain 1 Linear {
    load 2   0.0 1.0 0.0 0.0 0.0 0.0
  }

  constraints Plain 
  system ProfileSPD 
  integrator LoadControl $H 
  analysis Static 
  sensitivityAlgorithm -computeAtEachStep 
  analyze 1

  verify value [nodeDisp 2 2] [expr $H*($L**3)/(3*$E*$Iz)]

  verify value [sensNodeDisp 2 2 1 ] [expr -$H*$L**3/(3*($E**2)*$Iz)]     1e-10 "du/dE"
  verify value [sensNodeDisp 2 2 2 ] 0                                    1e-10 "du/dA"
  verify value [sensNodeDisp 2 2 3 ] [expr -$H*($L**3)/(3*$E*($Iz**2))]   1e-10 "du/dI"
  verify value [sensNodeDisp 2 2 4 ] [expr  $H*($L**2)/($E*$Iz)]          1e-10 "du/dL"

  #$H*$L**3/(3*$E*I))      "u"
  #  $L**3/(3*$E*I))       "du/dH"
  wipe

}

