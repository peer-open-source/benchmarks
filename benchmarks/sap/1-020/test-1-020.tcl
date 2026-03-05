pragma openseespy
set Element ForceFrame

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

section FrameElastic 1 -A 100000 -Ay 0 -Az 0 -Iz 2000 -Iy 1 -J 1 -E 3000 -G 1250
section FrameElastic 2 -A 100000 -Ay 0 -Az 0 -Iz 1000 -Iy 1 -J 1 -E 3000 -G 1250

# Columns
geomTransf Linear 1 0.0 1.0 0.0 
geomTransf Linear 2 0.0 1.0 0.0 
geomTransf Linear 3 0.0 1.0 0.0 
element $Element 1 1 2 -section 1 -transform 1 -mass 0.0 -shear 0
element $Element 2 2 3 -section 2 -transform 2 -mass 0.0 -shear 0
element $Element 3 4 5 -section 1 -transform 3 -mass 0.0 -shear 0
element $Element 4 5 6 -section 2 -transform 1 -mass 0.0 -shear 0

# Girders
#geomTransf Linear 4 0.0 1.0 0.0 
geomTransf Linear 4 0.0 1.0 0.0 
element $Element 5 2 7 -section 1 -transform 4 -mass 0.0 -shear 0
element $Element 6 7 5 -section 1 -transform 4 -mass 0.0 -shear 0
element $Element 7 3 8 -section 2 -transform 4 -mass 0.0 -shear 0
element $Element 8 8 6 -section 2 -transform 4 -mass 0.0 -shear 0


numberer Plain
constraints Transformation

set lambdas [eigen 2 -fullGenLapack]

set references {1.562 0.5868}

set pi [expr acos(-1)]
foreach lambda $lambdas reference $references {
  set period [expr (2*$pi)/sqrt($lambda)]
  puts $period

  verify value $period $reference 1e-3
}

