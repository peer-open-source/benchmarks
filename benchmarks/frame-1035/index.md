---
title: Flexural buckling
thumbnail: img/e45.png
---


## Observations

- **Solver**
   - `FullGenLapack` works well for few number of elements. With `20` elements, the solver oscillates between higher modes.
   - `Arpack` with `mode=1` is smooth but roughly matches `SymBandLapack`
   - `Arpack` with `mode=3` is noisy, but is closer to `FullGenLapack`
   - In all cases, the critical load is very similar

- **Wagner Term**


- **Stiffness Symmetry**
  - The stiffness using the corotational formulation **is not** symmetric, even at equilibrium.
  - The stiffness using the geometrically exact formulation **is nearly** symmetric.
