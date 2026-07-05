
set i 1
set j 2
set n 5
set t 9; # geometric transformation
set s 2; # section tag
set m 0.3; # mass per length
set imax 10; # max iterations
set itol 1e-8; # tolerance
set GaussName Lobatto;

model basic -ndm 3 -ndf 6



node 1  0.0 0.0 0.0
node 2 10.0 0.0 0.0

geomTransf Linear $t 0 0 1 
section Elastic $s 3000.0 300.0 1000.0 500.0 200.0 100.0

set tag 0
foreach case {a b c d e x} {
  incr tag
  switch $case {
    a {
      element forceBeamColumn $tag $i $j $t $GaussName $s $n
    }
    a2 {
      element forceBeamColumn $tag $i $j $t "$GaussName $s $n"
    }
    b  {
      element forceBeamColumn $tag $i $j $n $s $t -mass $m -iter $imax $itol -integration $GaussName
    }
  }
}


if 0 {
    element ForceFrame 1 $i $j $t $s -mass $m -iter $imax $itol -gauss $GaussName -n $n
}

print -json
