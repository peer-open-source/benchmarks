foreach element {ForceFrame PrismFrame CubicFrame} {
  verify about $element
  wipe
  model  -ndm 3 -ndf 6
  section ElasticFrame 1 \
    -E 29000.0 \
    -G 11200.0 \
    -A 13.843100000000064 \
    -Ay 13.843100000000064 \
    -Az 13.843100000000064 \
    -Iy 473.65597600916794 \
    -Iz 51.38797996416682 \
    -J 1.2779522608847174

  geomTransf Linear 1 0 0 1 

  node 0 0.0 0 0 
  node 1 55.2 0 0 
  fix 0 1 1 1 1 1 1 

  element $element 1 0 1 -section 1 -transform 1 -shear 1

  pattern Plain 1 Linear {
    load 1 0 0 10.0 0 0 0 ;
  }

  integrator LoadControl 1
  analysis Static 
  test Residual 1e-10 3 
  analyze 1 

  verify value [nodeDisp 1 3] 0.044376733692 1e-6
}
