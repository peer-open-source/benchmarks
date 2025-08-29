---
title: Plane encastre bending
description: A plane beam is subjected to a uniformly distributed load.
thumbnail: img/beam_solution.png
---


Consider the equilibrium differential equations for a 2D Timoshenko beam:

$$
\begin{gathered}
 A G k_s\left( u_y'+\theta\right) - EI \theta'' =0 \\
-A G k_s\left(u_y''+ \theta'\right)=\bar{w}
\end{gathered}
$$

This is a coupled ODE for the displacement $u_y(x)$ and cross-section rotation $\theta(x)$. 
The boundary conditions for this problem are

$$
u_y(0)=0, \quad \theta(0)=0, \quad u_y(L)=0 \quad \theta(L)=0
$$

and the solution is:

$$
u_y(x)=\frac{q_0 L^4}{24 E I^{}} \frac{x^2}{L^2}\left(1-\frac{x}{L}\right)^2-\frac{1}{k_s G A}\frac{q_0 L^2}{24} \left(1-12 \frac{x}{L}+12 \frac{x^2}{L^2}\right) + \frac{1}{G A k_s L^2} \frac{q_0 L^4}{24}
$$

This is plotted below along with the results of the finite element analysis with 4 and 9-node quadrilaterals:

![Beam with a hole.](img/beam_solution.png)

The properties used are:

```
E = 4000.0*ksi
nu = 0.25
L = 240.0*inch
d = 24.0*inch
thick = 1.0*inch
load = -20.0*kip
G = E / (2 * (1 + nu))
A = thick*d
k = 5/6
w = load/L
I = thick*d**3/12
```