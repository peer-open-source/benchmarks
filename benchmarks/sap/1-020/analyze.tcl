

numberer Plain

set lambdas [eigen 2 -fullGenLapack]

set references {1.562 0.5868}

set pi [expr acos(-1)]
foreach lambda $lambdas reference $references {
  set period [expr (2*$pi)/sqrt($lambda)]

  verify value $period $reference 1e-4
}
