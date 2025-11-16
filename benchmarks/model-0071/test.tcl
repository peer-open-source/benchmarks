# 2D problem with 2 DOFs on both the constrained node and the retained nodes
# The embedding domain is a 1x1 triangle, and the constrained node is placed at its centroid.
# Here we apply a random displacement on each retained node,
# and the displacement of the constrained node should be the weighted average
# of the displacements at the 3 retained nodes, with an equal weight = 1/3.

model basic -ndm 2 -ndf 2

# define the embedding domain (a piece of a soild domain)
node 1 0.0 0.0
node 2 1.0 0.0
node 3 0.0 1.0

# define the embedded node
node 4 [expr 1.0/3.0] [expr 1.0/3.0]

# define constraint element
element ASDEmbeddedNodeElement 1   4   1 2 3   -K 1.0e6

# apply random imposed displacement in range 0.1-1.0
set U1 [list [expr 0.1 + 0.9*rand()] [expr 0.1 + 0.9*rand()]]
set U2 [list [expr 0.1 + 0.9*rand()] [expr 0.1 + 0.9*rand()]]
set U3 [list [expr 0.1 + 0.9*rand()] [expr 0.1 + 0.9*rand()]]

# puts "Applying random X displacement:\nU1: $U1\nU2: $U2\nU3: $U3\n\n"
#
timeSeries Constant 1
pattern Plain 1 1 {
   for {set i 1} {$i < 3} {incr i} {
      sp 1 $i [lindex $U1 [expr $i - 1]]
      sp 2 $i [lindex $U2 [expr $i - 1]]
      sp 3 $i [lindex $U3 [expr $i - 1]]
   }
}

# run analysis
constraints Transformation
numberer Plain
system FullGeneral
test NormUnbalance 1e-08 10 1
algorithm Linear
integrator LoadControl 1.0
analysis Static
analyze 1

# compute expected solution
set UCref [list [expr ([lindex $U1 0] + [lindex $U2 0] + [lindex $U3 0] )/3.0] [expr ([lindex $U1 1] + [lindex $U2 1] + [lindex $U3 1] )/3.0]]
puts "Expected displacement at constrained node is (U1+U2+U3)/3:\n$UCref\n\n"

# read results
set UC [list {*}[nodeDisp 4]]
puts "Obtained displacement at constrained node is UC:\n$UC\n\n"

# check error
set ER [list [expr abs([lindex $UC 0] - [lindex $UCref 0])/[lindex $UCref 0]] [expr abs([lindex $UC 1] - [lindex $UCref 1])/[lindex $UCref 1]]]
puts "Relative error is abs(UC-UCref)/UCref:\n$ER\n\n"
foreach value $ER {
  verify value $value 0.0 1e-14
}

