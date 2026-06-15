# shell-0001: Clamped Circular Plate, Center Point Load

This benchmark compares nodal transverse displacement along a radial profile to the closed-form Reissner–Mindlin solution for a **clamped circular plate** under a **center point load**. Results are reported in **Hughes-normalized** form so that the reference profile is well scaled away from the load singularity.

The benchmark is intended to catch issues in shell/plate bending response, symmetry and clamp boundary handling, center-load application on a mapped quarter-disk mesh, and the mixed interpolation used by `HeterosisPlate` (where displacement sampling must respect connectivity).

## Model Geometry

The finite element model uses **quarter symmetry** of a circular disk of radius `RADIUS`. The patch is built with `xara.Model.surface` on a mapped **Q9** control-point layout (`quarter_disk_points` in `test_shell_0001.py`): one element block with `MESH_SUBDIVISIONS_PER_DIRECTION` by `MESH_SUBDIVISIONS_PER_DIRECTION` subdivisions.

- Symmetry is enforced on the straight edges meeting at the plate center.
- The **clamped** condition is applied on the **outer circular arc**.
- A **quarter** of the total point load is applied at the center node so that the symmetric model represents a total center load `P_TOTAL`.

## Files

- `test_shell_0001.py`  
  Defines the model, boundary conditions, reference solution, and pytest benchmarks.

## Elements Tested

The benchmark is parametrized over the following elements (MITC4/ASDShellQ4 and MITC9 use the same `ELEMENT_ORDER` convention as `shell-0002`):

```python
ELEMENT_ORDER = {
    "ASDShellQ4": 1,
    "ShellMITC4": 1,
    "HeterosisPlate": 2,
    "ShellMITC9": 2,
}
```

The interpolation used for the underlying shell formulation follows the same pattern as in `shell-0002`:

| Element | Transverse displacement interpolation | Rotation interpolation |
|---|---:|---:|
| `ASDShellQ4` | Q4 | Q4 |
| `ShellMITC4` | Q4 | Q4 |
| `ShellMITC9` | Q9 | Q9 |
| `HeterosisPlate` | Q8 | Q9 |

The `HeterosisPlate` case is exercised in a dedicated test because the ninth connectivity node carries the Q9 rotation field but not the Q8 transverse displacement field; nodal samples at **rotation-only** nodes are excluded from the displacement profile comparison.

## Material, Thickness, and Load Parameters

The numerical values in the test module are:

```python
RADIUS = 5.0
THICKNESS = 2.0
E_MOD = 10.92e5
NU = 0.3
KAPPA = 5.0 / 6.0

P_TOTAL = 1.0
P_QUARTER = -P_TOTAL / 4.0
```

Flexural rigidity is $D = E t^3 / (12(1-\nu^2))$. Mindlin transverse shear stiffness uses $\kappa G t$ with $G = E / (2(1+\nu))$.

## Reference Solution

Transverse deflection (positive downward in the closed form used by the test) combines the **Kirchhoff** clamped-plate term with a **logarithmic shear correction** in the Reissner–Mindlin framework; see `reissner_clamped_center_load_w` in `test_shell_0001.py`.

Nodal results are compared after **Hughes normalization**:

$$
w_{\mathrm{norm}} = w_{\mathrm{down}} \left(\frac{16\pi D\, }{P_{\mathrm{total}}\, R^2}\right)
$$

where $w_{\mathrm{down}}$ is the magnitude of downward displacement extracted from the model.

## What the Test Verifies

After a linear static analysis (`xara.StaticAnalysis` with `system="Umfpack"`), the benchmark checks that:

- Nodal transverse displacement along radii in the annulus $0.05 < r/R < 0.95$ matches the analytical profile within tolerances.
- Each sample satisfies either a **relative** or **absolute** error bound (whichever is easier to satisfy where the reference is small).
- `HeterosisPlate` results ignore nodes that are not part of the Q8 transverse displacement connectivity.

This is an **equilibrium / BVP** check, not a pure kinematic patch test.

## Error Tolerances and Sampling

Pointwise checks use:

```python
MAX_POINTWISE_REL_ERROR = 5.0e-2
MAX_POINTWISE_ABS_ERROR = 1.0e-2
REFERENCE_VALUE_FLOOR = 5.0e-2
```

Relative error divides the absolute error by $\max(|y_{\mathrm{ref}}|,\ r_{\mathrm{floor}})$ with $r_{\mathrm{floor}}$ equal to the scalar `REFERENCE_VALUE_FLOOR` in the test module, avoiding blow-ups near zero reference values.

## Running the Test

From the `shell-0001` folder:

```bash
python -m pytest test_shell_0001.py -v -rs
```

Expected collection (three parametrized cases plus one Heterosis-specific test):

```text
test_hughes_clamped_plate_pointwise_error[ASDShellQ4-1]
test_hughes_clamped_plate_pointwise_error[ShellMITC4-1]
test_hughes_clamped_plate_pointwise_error[ShellMITC9-2]
test_hughes_clamped_plate_pointwise_error_heterosis
```

The parametrized test **excludes** `HeterosisPlate`; that element is covered only by `test_hughes_clamped_plate_pointwise_error_heterosis`, which applies connectivity-aware displacement sampling.

If an element type is not compiled into the active OpenSees/Xara build, the corresponding case is **skipped** when an “unknown element type” error is raised during model construction.

## Notes on Interpretation

A passing result indicates that the mesh density and element formulation are adequate for this classical plate benchmark under the stated tolerances.

A failure may indicate:

- A problem in the potentially new plate/shell element tested (current suite is expected to pass).
- For `HeterosisPlate` or similar elements, incorrect handling of rotation-only nodes when sampling $w$.
- An unavailable or changed element implementation in the active OpenSees/Xara build.

## References

[1] T. J. R. Hughes, *The Finite Element Method: Linear Static and Dynamic Finite Element Analysis*. Englewood Cliffs, New Jersey: Prentice-Hall, 1987.

[2] O. C. Zienkiewicz, R. L. Taylor, and S. Govindjee, *The Finite Element Method: Its Basis and Fundamentals*. Elsevier, 8th ed., Nov. 2024.
