foreach element {EulerFrame ForceFrame PrismFrame} {
  verify about $element

  wipe
  model  -ndm 3 -ndf 6
  section ElasticFrame 1 \
    -E  29000.0 \
    -G  11200.0 \
    -A   13.843100000000064 \
    -Ay  13.843100000000064 \
    -Az  13.843100000000064 \
    -Iy 473.65597600916794 \
    -Iz  51.38797996416682 \
    -J    1.2779522608846037

  node 0  0.0 0 0 
  node 1 55.2 0 0 
  fix  0 1 1 1 1 1 1 

  geomTransf Linear 1 0 0 1 

  element $element 1 0 1 -section 1 -transform 1 -shear 0

  pattern Plain 1 Linear {
    load 1  0 0 10 0 0 0 ;
  }
  integrator LoadControl 1
  analysis Static 
  test Residual 1e-10 3 
  analyze 1 
  verify value [nodeDisp 1 3] 0.040816424636 1e-6
}
