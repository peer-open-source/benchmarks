#
# - Clarke, M.J. and Hancock, G.J. (1990)
#   "A study of incremental‐iterative strategies for non‐linear analyses", 
#   International Journal for Numerical Methods in Engineering, 29(7), pp. 1365–1391. 
#   Available at: https://doi.org/10.1002/nme.1620290702.
#
set A  10000.0 
set E  200 
set Iy 100000000.0
set Iz 100000000.0 
set J  200000000.0 
set G  200 
set Ay 1000000.0 
set Az 1000000.0

foreach Frame {forceBeamColumn} {

  wipe

  model basic -ndm 3 -ndf 6

  node  1 -5000.0 0.0 0 
  node  2 -4009.568694135459 179.6181055187626 0 
  node  3 -3012.765365914115 319.6179637813475 0 
  node  4 -2011.1741391101941 419.7770864617414 0 
  node  5 -1006.386746445197 479.9363002877908 0 
  node  6  -200.0 500.0 0 
  node  7 1006.3867464451962 479.9363002877908 0 
  node  8 2011.1741391101934 419.7770864617414 0 
  node  9 3012.765365914115 319.6179637813475 0 
  node 10 4009.568694135459 179.6181055187626 0 
  node 11 5000.0 0.0 0 
  fix  1 1 1 1 1 1 0 
  fix 11 1 1 1 1 1 0

  fix  2  0 0 1 0 0 0
  fix  3  0 0 1 0 0 0
  fix  4  0 0 1 0 0 0
  fix  5  0 0 1 0 0 0
  fix  6  0 0 1 0 0 0
  fix  7  0 0 1 0 0 0
  fix  8  0 0 1 0 0 0
  fix  9  0 0 1 0 0 0
  fix 10  0 0 1 0 0 0

  set trn 1
  set sec 1
  section Elastic 1 $E $A $Iz $Iy $J $G

  geomTransf Corotational 1 0 0 1 

  element $Frame  1  1  2  $trn Legendre $sec 5
  element $Frame  2  2  3  $trn Legendre $sec 5
  element $Frame  3  3  4  $trn Legendre $sec 5
  element $Frame  4  4  5  $trn Legendre $sec 5
  element $Frame  5  5  6  $trn Legendre $sec 5
  element $Frame  6  6  7  $trn Legendre $sec 5
  element $Frame  7  7  8  $trn Legendre $sec 5
  element $Frame  8  8  9  $trn Legendre $sec 5
  element $Frame  9  9 10  $trn Legendre $sec 5
  element $Frame 10 10 11  $trn Legendre $sec 5


  pattern Plain 1 Linear {
    load 6 0.0 -1.0 0.0 0 0 0
  }

  system BandGeneral -det
  numberer RCM
  constraints Plain
  test NormDispIncr 1e-08 20 1
  algorithm Newton
#   integrator ArcLength 45 0 -det -exp 0.5 -reference point -j 6
  integrator MinUnbalDispNorm 100 5 0.01 5 -det
  analysis Static

  # set out [open a.out w+]
  # for {set i 0} { $i < 1000 } {incr i} {
  #   if {0 != [analyze 1]} {
  #       puts $i
  #       break
  #   }
  #   puts $out "[expr -1*[nodeDisp 6 2]] [getTime] "
  # }
}
# close $out