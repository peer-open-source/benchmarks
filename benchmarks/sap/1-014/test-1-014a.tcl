#pragma openseespy
model  -ndm 3 -ndf 6
node 1 0 0 0 
fix 1 -dof 1
fix 1 -dof 4
node 2 96 0 0 
fix 2 -dof 1
fix 2 -dof 4
fix 1 0 1 1 0 1 1 

section FrameElastic 1 -A 216 -Ay 180 -Az 180 -Iz 5832 -Iy 2592 -J 6085.12013626099 -E 3600 -G 1500
nodeCoord 1 
nodeCoord 2 
geomTransf Linear 1 0.0 0.0 1.0 
element PrismFrame 1 1 2 -section 1 -transform 1 -mass 4.968e-05


set lambdas [eigen 2 -fullGenLapack]

set references {0.054547 0.036364}

set pi [expr acos(-1)]
foreach lambda $lambdas reference $references {
  set period [expr (2*$pi)/sqrt($lambda)]

  verify value $period $reference 1e-6
}

