model  -ndm 3 -ndf 6
node 1  0.0 0 0 
node 2 55.2 0 0 

fix 1 1 1 1 1 1 1 
fix 2 0 0 0 0 0 0 

set section 1
section ElasticFrame $section \
  -E  29000.0 \
  -G  11200.0 \
  -A  13.843100000000064 -Ay 13.843100000000064 -Az 13.843100000000064 \
  -Iy 473.65597600916794 -Iz 51.38797996416682 \
  -J 1.2779522608703928

set transform 1
geomTransf Linear 1 0 0 1 

set nip 5

element ForceFrame 1  1 2  $transform  "Legendre $section $nip"

pattern Plain 1 Linear {
  load 2 0 0 1 0 0 0 ;
}

integrator LoadControl 10 
analysis Static 
test Residual 1e-10 3 
analyze 1

verify value [nodeDisp 2 3] 0.044376733692 1e-6
