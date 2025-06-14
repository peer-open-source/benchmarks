---
title: "0010 - Column Buckling"
meta:
  title: "A nonlinear buckling simulation of a column with varied boundary conditions and finite element formulations"
tags: ["Frame"]
#render: ./model.glb
description: >-
  This example performs a nonlinear buckling analysis of a column under axial load,
  using various element formulations and end conditions.
downloads:
  Python: ["buckling.py"]
  Tcl:    ["buckling.tcl"]
---


## Problem

| # | Name           | Left Support | Right Support     |
| - | -------------- | ------------ | ----------------- |
| 1 | **cantilever** | Fixed        | Free              |
| 2 | **propped**    | Fixed        | Roller            |
| 3 | **encastre**   | Fixed        | Fixed             |
| 4 | **simple**     | Pin          | Roller            |
| 5 | **guided**     | Fixed        | Orthogonal Roller |


This example analyzes a column subject to axial loading until buckling occurs.
Different element types, shear deformation settings, and boundary conditions are compared
by computing the critical load and comparing it to the theoretical Euler load which is given by:

\[
P_{\mathrm{euler}} = \frac{\pi^2 EI}{L^2}
\]


Loosely speaking, buckling happens when there are multiple shapes that a structure can deform into that will be in equilibrium with it's applied loads. 
This implies that at the time of buckling, there are multiple independent displacement increments $\bm{u}$ which will be mapped to the same resisting load by the tangent $\bm{K}$. 
In other words, the buckling load is that at which $\bm{K}$ becomes singular. 
If we consider $\bm{K}$ as a function of the load factor $\bm{\lambda}$, this condition can be expressed as the nonlinear root-finding problem:

$$
\operatorname{det}\bm{K}(\lambda) = 0
$$

For many classical models, the dependence of $\bm{K}$ on $\lambda$ is linear, and in this case the problem is equivalent to a generalized eigenvalue problem which is computationally much more tractable. However, even if $\bm{K}$ is nonlinear in $\lambda$, one may still investigate the *linearized buckling problem*, where an eigenvalue problem is obtained by learizing $\bm{K}(\lambda)$:

$$
\bm{K}(\lambda) \approx \bm{K}(0) + \bm{K}^{\prime}(0) \lambda
$$

where $\bm{K}^{\prime}$ is the derivative of $\bm{K}$ with respect to $\lambda$.


## Model

We define a function `create_column` that constructs the finite element model of the column
based on options like element type, shear deformation flag, and spatial dimension:

{{< tabs tabTotal="2" >}}
{{% tab name="Python" %}}
```python
def create_column(boundary="pin-pin", elem_data=None, ndm=2):
    if elem_data is None:
        elem_data = {}

    elem_type  = elem_data.get("type",      "forceBeamColumnCBDI")
    geom_type  = elem_data.get("transform", "Corotational")
    use_shear  = elem_data.get("shear",     False)
    kinematics = elem_data.get("order",     0)

    E  = 29000.0
    G  = 11200.0
    A  = 112.0
    I  = 110.0
    Ay = 3/6*A
    Az = 3/6*A
    L  = 60.0
    ne = 10
    nIP = 5

    model = ops.Model(ndm=ndm)

    for i in range(1, ne+2):
        y = (i-1)/float(ne)*L
        location = (0.0, y, 0.0) if ndm == 3 else (0.0, y)
        model.node(i, location)
        model.mass(i, *[1.0]*model.getNDF())

    fix_node(model, 1, boundary.split("-")[0])
    fix_node(model, ne+1, boundary.split("-")[1])
```
{{% /tab %}}
{{< /tabs >}}

The section is defined as an `ElasticFrame` and assigned to each element in the column:

{{< tabs tabTotal="2" >}}
{{% tab name="Python" %}}
```python
    sec_tag = 1
    properties = [E, A, I]
    if ndm == 3:
        properties += [2*I, "-J", 100*I, "-G", G]
    if use_shear:
        properties += ["-Ay", Ay, "-G", G]
        if ndm == 3:
            properties += ["-Az", Az]
    model.section("ElasticFrame", sec_tag, *properties)

    geo_tag = 1
    vector = (0, 0, 1) if ndm == 3 else ()
    model.geomTransf(geom_type, geo_tag, *vector)

    for i in range(1, ne+1):
        model.element(elem_type, i, (i, i+1),
                      section=sec_tag,
                      transform=geo_tag,
                      order=kinematics,
                      shear=int(use_shear))
```
{{% /tab %}}
{{< /tabs >}}

The axial load is applied at the top node, using the Euler buckling expression as a reference:

{{< tabs tabTotal="2" >}}
{{% tab name="Python" %}}
```python
    if use_shear:
        phi = 12*E*I/(Ay*G*L**2)
        lam = buckle_factor(boundary, phi)
        kL = L/lam
        euler_load = E*I/kL**2 / (1 + lam**2*phi/12)
    else:
        kL = L / buckle_factor(boundary)
        euler_load = E*I/kL**2

    model.pattern("Plain", 1, "Linear")
    load = (0.0, -euler_load, 0.0) if ndm == 2 else (0.0, -euler_load, 0.0, 0, 0, 0)
    model.load(ne+1, *load, pattern=1)

    return model, euler_load
```
{{% /tab %}}
{{< /tabs >}}

## Buckling Analysis

A nonlinear static analysis is performed to determine the limit load. The first
eigenvalue of the tangent stiffness matrix is tracked and interpolated to find the
load factor at which it reaches zero.

{{< tabs tabTotal="2" >}}
{{% tab name="Python" %}}
```python
def buckling_analysis(model, peak_load):
    load_step = 0.01
    PeakLoadRatio = 1.5

    model.system('UmfPack')
    model.test("EnergyIncr", 1e-8, 20, 9)
    model.algorithm("Newton")
    model.integrator("LoadControl", load_step)
    model.analysis("Static")

    lam_0 = model.getTime()
    eig_0 = model.eigen("-fullGenLapack", 1)[0]

    limit_load = None
    for i in range(1, int(PeakLoadRatio/load_step)+1):
        if model.analyze(1) != 0:
            break
        lam = model.getTime()
        eig = model.eigen("-fullGenLapack", 1)[0]
        if eig <= 0.0:
            lam_i = lam_0 + (lam - lam_0)*eig_0/(eig_0-eig)
            limit_load = lam_i * peak_load
            break
        lam_0 = lam
        eig_0 = eig

    return limit_load
```
{{% /tab %}}
{{< /tabs >}}

## Results

### Euler

| Boundary    | Critical Load |
|-------------|---------------|
| pin-pin     |   8745.57 |
| fix-roll    |   8745.57 |
| fix-fix     |  34982.26 |
| fix-pin     |  17891.23 |
| fix-free    |   2186.39 |
| pin-roll    |   2186.39 |

PrismFrame

|  Boundary   |   Computed    |   Error   |
|-------------|---------------|-----------|
|  pin-pin    |    8841.80    |  1.100 %  |
|  fix-roll   |    8841.80    |  1.100 %  |
|  fix-fix    |   36559.09    |  4.507 %  |
|  fix-pin    |   18296.87    |  2.267 %  |
|  fix-free   |    2192.37    |  0.273 %  |
|  pin-roll   |    2192.37    |  0.273 %  |

ForceFrame 

|  Boundary   |  Computed  |   Error  |
|-------------|------------|----------|
|  pin-pin    |   8841.80  |  1.100 % |
|  fix-roll   |   8841.80  |  1.100 % |
|  fix-fix    |  36559.09  |  4.507 % |
|  fix-pin    |  18296.87  |  2.267 % |
|  fix-free   |   2192.37  |  0.273 % |
|  pin-roll   |   2192.37  |  0.273 % |

### Shear

When shear deformations are included things become more complicated:

$$
\begin{gathered}
\lambda=\sqrt{\frac{P L^2}{E I\left[1-P /\left(k_{\mathrm{s}} G A\right)\right]}}=\sqrt{\frac{P L^2}{\chi E I}} \\
\chi=1-P /\left(k_{\mathrm{s}} G A\right) \\
P=\chi \lambda^2 E I / L^2 .
\end{gathered}
$$

$$
\begin{gathered}
\chi=\frac{1}{1+\lambda^2 E I /\left(k_{\mathrm{s}} G A L^2\right)}=\frac{1}{1+\lambda^2 \varphi / 12} \\
P=\frac{\lambda^2 E I / L^2}{1+\lambda^2 \varphi / 12} .
\end{gathered}
$$

$$
\tan \lambda_{\text {cr }}=\chi \lambda_{\text {cr }}=\frac{\lambda_{\text {cr }}}{1+\lambda_{\text {cr }} 2 \varphi / 12}
$$

{{< nav id="shear" type="tabs" >}}
{{< nav-item header="Prism" show="true" >}}

| Boundary  |  Computed  |   Error   |
|-----------|------------|-----------|
| pin-pin   |   8718.89  |  1.085 %  |
| fix-roll  |   8718.88  |  1.085 %  |
| fix-fix   |  34545.22  |  4.259 %  |
| fix-pin   |  17727.65  |  2.192 %  |
| fix-free  |   2184.73  |  0.272 %  |
| pin-roll  |   2184.73  |  0.273 %  |

{{< /nav-item >}}
{{< nav-item header="Force" >}}

| Boundary  |  Computed  |   Error   |
|-----------|------------|-----------|
| pin-pin   |   8718.89  |  1.085 %  |
| fix-roll  |   8718.88  |  1.085 %  |
| fix-fix   |  34545.22  |  4.259 %  |
| fix-pin   |  17727.65  |  2.192 %  |
| fix-free  |   2184.73  |  0.272 %  |
| pin-roll  |   2184.73  |  0.273 %  |

{{< /nav-item >}}
{{< nav-item header="Exact" >}}

| Boundary  |  Computed  |   Error   |
|-----------|------------|-----------|
| pin-pin   |   8792.02  |  1.933 %  |
| fix-roll  |   8792.01  |  1.933 %  |
| fix-fix   |  35773.31  |  7.965 %  |
| fix-pin   |  18068.91  |  4.159 %  |
| fix-free  |   2189.24  |  0.480 %  |
| pin-roll  |   2189.25  |  0.480 %  |

{{< /nav-item >}}
{{< /nav >}}



| Boundary  | Critical Load |
|-----------|------------|
| pin-pin   |   8625.30
| fix-roll  |   8625.30
| fix-fix   |  33134.20
| fix-pin   |  17347.40
| fix-free  |   2178.80
| pin-roll  |   2178.80

The full script is:

{{< fold "buckling.py" >}}

