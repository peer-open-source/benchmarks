# ===================================================
# User parameters
# ===================================================
# material parameters
set E 3000000000.0
set poiss 0.3
set rho 2100.0
set thickness 1.0
set G [expr $E/(2.0*(1.0+$poiss))]
# domain size
set Lx 260.0
set Ly 140.0
# mesh size
set hx 10.0
set hy 1.0
# time increment
set dt 0.01
# predominant frequency of the Ricker Wavelet
set freq 10.0
# total duration of the dynamic analysis
set duration 1.0

# builder
model Basic -ndm 2 -ndf 2

# time series
# we want to apply a Ricker Wavelet with predominant frequency = 10 Hz.
# It should be applied as velocity
set pi [expr acos(-1.0)]
set wl [expr sqrt(3.0/2.0)/$pi/$freq*10.0]
set ndiv [expr int($wl/$dt)]
set dt [expr $wl/$ndiv.0]
set ts_vals {}
for {set i 0} {$i < $ndiv} {incr i} {
    set ix [expr $i.0*$dt-$wl/2.0]
    set iy [expr $ix*exp(-$pi*$pi*$freq*$freq*$ix*$ix)]
    lappend ts_vals $iy
}
set tsX 1
timeSeries Path $tsX -dt $dt -values $ts_vals  -factor 9.806

# material
set matTag 1
nDMaterial ElasticIsotropic $matTag $E $poiss $rho

# Define nodes on a regular grid with sizes hx-hy.
# For a more clear visualization we set the size of the absorbing elements larger.
# (note: the size of this element does not influence the results. The only constraint is that it
# should have a non-zero size!)
set ndivx [expr int($Lx/$hx) + 2]; # add 2 layers of absorbing elements (left and right)
set ndivy [expr int($Ly/$hy) + 1]; # add 1 layer of absorbing elements (bottom)
set abs_h [expr $hx*2.0]
for {set j 0} {$j <= $ndivy} {incr j} {
    if {$j == 0} {set y [expr -$abs_h]} else {set y [expr ($j-1) * $hy]}
    for {set i 0} {$i <= [expr $ndivx]} {incr i} {
        if {$i == 0} {set x [expr -$abs_h]} elseif {$i == [expr $ndivx]} {set x [expr $Lx+$abs_h]} else {set x [expr ($i-1) * $hx]}
        node [expr $j*($ndivx+1)+$i+1] [expr $x-$Lx/2.0] $y
    }
}

# Define elements.
# Save absorbing elements tags in a list
set abs_elements {}
for {set j 0} {$j < $ndivy} {incr j} {
    # Yflag
    if {$j == 0} {set Yflag "B"} else {set Yflag ""}
    for {set i 0} {$i < [expr $ndivx]} {incr i} {
        # Tags
        set Etag [expr $j*($ndivx)+$i+1]
        set N1 [expr $j*($ndivx+1)+$i+1]
        set N2 [expr $N1+1]
        set N4 [expr ($j+1)*($ndivx+1)+$i+1]
        set N3 [expr $N4+1]
        # Xflag
        if {$i == 0} {set Xflag "L"} elseif {$i == [expr $ndivx-1]} {set Xflag "R"} else {set Xflag ""}
        set btype "$Xflag$Yflag"
        if {$btype != ""} {
            # absorbing element
            lappend abs_elements $Etag
            if {$Yflag != ""} {
                # bottom element
                element ASDAbsorbingBoundary2D $Etag $N1 $N2 $N3 $N4 $G $poiss $rho $thickness $btype -fx $tsX
            } else {
                # vertical element
                element ASDAbsorbingBoundary2D $Etag $N1 $N2 $N3 $N4 $G $poiss $rho $thickness $btype
            }
        } else {
            # soil element
            element quad $Etag $N1 $N2 $N3 $N4 $thickness PlaneStrain $matTag 0.0 0.0 0.0 [expr -9.806*$rho]
        }
    }
}

# Static analysis (or quasti static)
# The absorbing boundaries now are in STAGE 0, so they act as constraints
constraints Transformation
numberer RCM
system UmfPack
test NormUnbalance 0.0001 2 0
algorithm Newton
integrator LoadControl 1.0
analysis Static
set ok [analyze 1]
if {$ok != 0} {
    error "Gravity analysis failed"
}
loadConst -time 0.0
wipeAnalysis

# update absorbing elements to STAGE 1 (absorbing)
setParameter -val 1 -ele {*}$abs_elements stage

# recorders
set soil_base [expr 1*($ndivx+1)+int($ndivx/2)+1]
set soil_top [expr $ndivy*($ndivx+1)+int($ndivx/2)+1]

# Dynamic analysis
# The absorbing boundaries now are in STAGE 0, so they act as constraints
constraints Transformation
numberer RCM
system UmfPack
test NormUnbalance 0.0001 2 0
algorithm Newton
integrator TRBDF2
analysis Transient
set nsteps [expr int($duration/$dt)]
set dt [expr $duration/$nsteps.0]

verify value [analyze $nsteps $dt] 0

