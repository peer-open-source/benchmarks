---
title: 3D Plasticity
description: Test of J2 plasticity using a mixed brick element.
---

All the results are obtained using a three-dimensional finite element, based on a mixed approach (Simo et al. [1985b]) and implemented into the Finite Element Analysis Program (FEAP) (Zienkiewicz \& Taylor [1989, 1991]).

The tests are performed on a cubic specimen of side length equal to 10 , with boundary and loading conditions set to produce the appropriate stress/strain state.
The sample is modeled with only one element and the material properties are:

$$
\begin{array}{ccc}
E=100, & v=0.3, & \sigma_{y, 0}^u=15 \\
H_{\text {kin }}^u=100, & H_{n I}^u=10, & H_{\text {iso }}^u=0
\end{array}
$$

for the NLK model, and:

$$
\begin{gathered}
E=100, \quad v=0.3, \quad \sigma_{y, 0}^u=15 \\
\beta^u=10, \quad \delta^u=50, \quad H_{\text {kin }}^u=0, \quad H_{\text {iso }}^u=0
\end{gathered}
$$
