---
title: 3-DOF eigenvalues
description: "checking eigen results of smallest and largest values"
---

3 springs in series, $K = 30,20,10$, $M = 11.1,22.2,33.3$

results as computed by matlab: 0.139300647653736 1.05865310768512 4.9582024008173

using following 3 commands:

```matlab
  format longG
  K = [[50 -20 0];[-20 30 -10];[0 -10 10]]
  M = [[11.1 0 0];[0 22.2 0];[0 0 33.3]]
  eig(K,M)
```

puts "Small 3 dof 2 spring model: checking eigen results of smallest and largest values"
