# Problem from Section 9.9.2 of [1]
#
# [1] M. A. Crisfield, Non-linear finite element analysis of solids and structures. 
#     Volume 1: Essentials, Repr. Chichester: Wiley, 2001.
#
if {![llength [info commands verify]]} {
  proc verify {cmd {value ""} {reference ""} {tolerance 1e-12} {about ""}} {
      if {$cmd == "error"} {
          if {$reference == 0} {
            set check [expr abs($value)]
          } else {
            set check [expr abs(($value - $reference)/$reference)]
          }
          if {$check > $tolerance} {
            puts  "   \033\[31mFAIL\033\[0m: | $value - $reference | = $check > $tolerance"
            error "$about"
          } else {
            puts  "   \033\[32mPASS\033\[0m   $value  $check $about"
          }

      } elseif {$cmd == "value"} {
          set check [expr abs($value - $reference)]
          if {abs($value - $reference) > $tolerance} {
            puts  "   \033\[31mFAIL\033\[0m($about): | $value - $reference | = $check > $tolerance"
            error "$about"
          } else {
            puts  "    \033\[32mPASS\033\[0m  $value $check $about"
          }
      } else {
        # "about"
        puts "  $value"
      }
  }
}

proc Setup {TestName Tol} {
    wipe
    set E 0.5e8
    set A 1.0
    set material 1

    model basic -ndm 2 -ndf 2

    node 1 0     0
    node 2 2500 25

    fix 1 1 1
    fix 2 1 0

    uniaxialMaterial Elastic $material $E

    element corotTruss 1 1 2  $A $material
    pattern Plain 1 Linear {
      load 2 0 -1
    }

    system FullGeneral
    numberer Plain
    constraints Plain
    integrator LoadControl 1.9;

    algorithm NewtonLineSearch \
      -type InitialInterpolated \
      -tol 0.8 -minEta 0.01 -maxEta 25 \
      -pFlag 1

    # test NormDispIncr 1.0e-6 10 1
    # test Residual 1.0e-3 10 1
    # test RelativeNormUnbalance 1.0e-3 10 1
    test $TestName $Tol 10 1
    # test RelativeEnergyIncr 1.0e-6 10 1
    analysis Static
}


Setup NormDispIncr 1.0e-2
analyze 1

set relative_residuals [testNorms]
puts ${relative_residuals}

verify value [nodeDisp 2 2] -1.0097631086926619 1e-8


Setup EnergyIncr 1e-5
analyze 1

set relative_residuals [testNorms]
puts ${relative_residuals}

verify value [nodeDisp 2 2] -1.0097631086926619 1e-8




Setup RelativeNormUnbalance 1.0e-3
analyze 1

set relative_residuals [testNorms]
puts ${relative_residuals}
verify value [nodeDisp 2 2] -1.0097631086926619 1e-8
analyze 5