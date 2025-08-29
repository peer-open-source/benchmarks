
model Basic -ndm 3 -ndf 6

node 1  0.0               0.0  0.0 
node 2  9.801714032956060 0.0  0.4815273327803071 
node 3 19.509032201612835 0.0  1.9214719596769570
node 4 29.028467725446234 0.0  4.3059664267791180
node 5 38.268343236508976 0.0  7.6120467488713260
node 6 47.139673682599760 0.0 11.8078735651644950
node 7 55.557023301960214 0.0 16.8530387697454780
node 8 63.439328416364546 0.0 22.6989546637263000
node 9 70.710678118654740 0.0 29.2893218813452400
fix 1 1 1 1 1 1 1 


geomTransf Corotational02 1 0.0 1.0 0.0

section Elastic 1 1e3 10e3 833.33 833.33 500 1666.6667
# section ElasticFrame 1 \
#   -E   1000.0 \
#   -A  10000.0 \
#   -Ay 10000.0 \
#   -Az 10000.0 \
#   -Iz   833.3333333333334 \
#   -Iy   833.3333333333334 \
#   -G 500.0 \
#   -J 1666.6666666666667

element ForceFrame 1 1 2 -section 1 -transform 1 -shear 0
element ForceFrame 2 2 3 -section 1 -transform 1 -shear 0
element ForceFrame 3 3 4 -section 1 -transform 1 -shear 0
element ForceFrame 4 4 5 -section 1 -transform 1 -shear 0
element ForceFrame 5 5 6 -section 1 -transform 1 -shear 0
element ForceFrame 6 6 7 -section 1 -transform 1 -shear 0
element ForceFrame 7 7 8 -section 1 -transform 1 -shear 0
element ForceFrame 8 8 9 -section 1 -transform 1 -shear 0


pattern Plain 1 Linear {
  load 9  0.0 600.0 0.0 0 0 0 ;
}

system BandGeneral 
numberer RCM 
constraints Plain 
algorithm Newton
test NormUnbalance 1e-6 60 0
analysis Static 

integrator LoadControl 0.5 
verify value [analyze 1] 0

puts "[numIter] [getTime]"

integrator LoadControl 0.25
verify value [analyze 1] 0
puts "[numIter] [getTime]"

integrator LoadControl 0.25
verify value [analyze 1] 0
puts "[numIter] [getTime]"

puts "[nodeDisp 9 1] [nodeDisp 9 2] [nodeDisp 9 3]" 

