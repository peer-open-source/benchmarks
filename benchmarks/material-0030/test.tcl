
package require OpenSeesRT


model basic -ndm 1 -ndf 1

set fy  50e3
set E   29e6
set b   0.04
set R0  19
set cR1 0.9240
set cR2 0.1500
set Ccd 0.5



# Create a 1d wrapper named "a"
# dmg::wrap 1d "a" "pos" "neg" -Ccd $Ccd

uniaxialMaterial Steel02 2 $fy $E $b $R0 $cR1 $cR2

#                                     w m
uniaxialMaterial UniaxialDamage 1 2 -damage {
  dmg::evol "pos" mbeta {4.2 1.0} -Cd0 3.0 -Cd1 125 -Cwc 0.12  -E $E -fy $fy -Ccd $Ccd
  dmg::evol "neg" mbeta {4.2 1.0} -Cd0 3.0 -Cd1 125 -Cwc 0.12  -E $E -fy $fy -Ccd $Ccd
}

set n 300
invoke UniaxialMaterial 1 {
  foreach i [linspace 0 10 $n] A [linspace 0.2 6.0 $n] {
    set strain [expr $A*$fy/$E*sin($i*3.142)]
    strain $strain -commit
    set stress [expr [stress]/$fy]
#   puts "$strain\t$stress" ; # \t[tangent]"
  }
}

verify value $stress  0.45147360340537612 ; # at strain=-0.0010397840306423003


