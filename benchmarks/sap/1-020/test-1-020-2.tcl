pragma openseespy
model  -ndm 3 -ndf 6
node 1 -120 0 0 
fix 1 -dof 2
fix 1 -dof 4
fix 1 -dof 6
node 2 -120 0 120 
fix 2 -dof 2
fix 2 -dof 4
fix 2 -dof 6
node 3 -120 0 240 
fix 3 -dof 2
fix 3 -dof 4
fix 3 -dof 6
node 4 120 0 0 
fix 4 -dof 2
fix 4 -dof 4
fix 4 -dof 6
node 5 120 0 120 
fix 5 -dof 2
fix 5 -dof 4
fix 5 -dof 6
node 6 120 0 240 
fix 6 -dof 2
fix 6 -dof 4
fix 6 -dof 6
node 7 0 0 120 
fix 7 -dof 2
fix 7 -dof 4
fix 7 -dof 6
node 8 0 0 240 
fix 8 -dof 2
fix 8 -dof 4
fix 8 -dof 6
fix 1 1 0 1 0 1 0 
fix 4 1 0 1 0 1 0 
mass 7 1.0364 0 0 0.0 0.0 0.0 
mass 8 0.5182 0 0 0.0 0.0 0.0 
nDMaterial ElasticIsotropic 1 10900 0.3 
nDMaterial ElasticIsotropic 2 3600 0.2 
nDMaterial ElasticIsotropic 3 3000 0.2 
nDMaterial ElasticIsotropic 4 3600 0.2 
nDMaterial ElasticIsotropic 5 29000 0.3 
section FrameElastic 1 -A 100000 -Ay 0 -Az 0 -Iz 2000 -Iy 1 -J 1 -E 3000 -G 1250
section FrameElastic 2 -A 100000 -Ay 0 -Az 0 -Iz 1000 -Iy 1 -J 1 -E 3000 -G 1250
geomTransf Linear 1 0.0 1.0 0.0 
element PrismFrame 1 1 2 -section 1 -transform 1 -mass 0.0 -shear 0
geomTransf Linear 2 0.0 1.0 0.0 
element PrismFrame 2 2 3 -section 2 -transform 2 -mass 0.0 -shear 0
geomTransf Linear 3 0.0 1.0 0.0 
element PrismFrame 3 4 5 -section 1 -transform 3 -mass 0.0 -shear 0
geomTransf Linear 4 0.0 1.0 0.0 
element PrismFrame 4 5 6 -section 2 -transform 4 -mass 0.0 -shear 0
geomTransf Linear 5 0.0 1.0 0.0 
element PrismFrame 5 2 7 -section 1 -transform 5 -mass 0.0 -shear 0
geomTransf Linear 6 0.0 1.0 0.0 
element PrismFrame 6 7 5 -section 1 -transform 6 -mass 0.0 -shear 0
geomTransf Linear 7 0.0 1.0 0.0 
element PrismFrame 7 3 8 -section 2 -transform 7 -mass 0.0 -shear 0
geomTransf Linear 8 0.0 1.0 0.0 
element PrismFrame 8 8 6 -section 2 -transform 8 -mass 0.0 -shear 0


numberer Plain

set lambdas [eigen 2 -fullGenLapack]

set references {1.562 0.5868}

set pi [expr acos(-1)]
foreach lambda $lambdas reference $references {
  set period [expr (2*$pi)/sqrt($lambda)]

  verify value $period $reference 1e-3
}

