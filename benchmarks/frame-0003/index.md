---
title: "0003 - Simple span with distributed loading"
Downloads:
  2D:
  - test-legacy-2d.tcl
  3D:
  - test-legacy-3d.tcl
description: Simply supported beam with distributed loads
---


$$
\theta_{yj} = -d_1 - d_2
$$

$$
d_1 =  a L  N L / (EA)
\qquad
d_2 =  w_x  L^2 /(2EA)
$$

$$
u^{(i)}_x = a L  N L / (EA) + w_x  L^2 /(2EA)
$$

----

$$
V_y = P_y (1-a/L)
$$

$$
d_1 =  \frac{-V_y}{6 EI_z L} (a^2 L - 2 a L^2)
\qquad\text{and}\qquad
d_2 = \frac{w_y L^3}{24 EI_z}
$$


```tcl
\theta_zi  =   d_1 + d_2  [nodeDisp 1 6]
```


$$
d_1  =  \frac{-V_y}{6 EI_z L} (a^2 L + a L^2)
$$


$$
\theta_z^{(j)}  =   d_1 - d_2 
\qquad
[nodeDisp\; 2\; 6]
$$

$$
d_1  =  V_z/(6 EI_y L) (a^2 L - 2 a L^2)
\qquad
d_2  =  -w_z L^3/(24 EI_y)
$$

$$
\theta_{y}^{(i)}  =  d_1 -w_z L^3/(24 EI_y)
\qquad
[nodeDisp \; 1 \;  5]
$$

$$
d_1  =  \frac{-V_z}{6 EI_y L} (a^2 L + a L^2)
$$

$$
\theta_y^{(j)}  =  -d_1 - d_2 
\qquad
[nodeDisp\; 2\; 5]
$$
