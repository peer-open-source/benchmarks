# shell-0002: Distorted Five-Element Patch Test

This benchmark verifies generalized strain recovery on a distorted five-element shell/plate patch. The test is a kinematic patch test: a prescribed displacement and rotation field is evaluated through the element interpolation, and the recovered generalized strains are compared against the corresponding analytical strain field.

The benchmark is intended to detect mistakes in element connectivity, interpolation order, geometry mapping, local node ordering, and the mixed-interpolation treatment used by `HeterosisPlate`.

## Patch Geometry

The benchmark uses an enclosing five-element patch. The outer boundary is rectangular, and the center region is a distorted quadrilateral. The five patch regions are:

- `E_center`
- `E_bottom`
- `E_right`
- `E_top`
- `E_left`

The same patch geometry is shared by the pytest benchmark and the plotting utility through `_shell_0002_patch.py`.

![Distorted five-element patch](./_outputs/mesh_plots/HeterosisPlate_distorted_patch.png)

## Files

- `_shell_0002_patch.py`  
  Defines the shared patch geometry and Xara model-building utilities.

- `test_shell_0002.py`  
  Defines the pytest benchmark for exact generalized strain recovery.

- `plot_shell_0002_mesh.py`  
  Provides a standalone plotting utility for generating VEUx and Matplotlib visualizations of the patch.

## Elements Tested

The benchmark is parametrized over the following elements:

```python
ELEMENT_ORDER = {
    "ASDShellQ4": 1,
    "ShellMITC4": 1,
    "HeterosisPlate": 2,
    "ShellMITC9": 2,
}
```

The interpolation used for strain recovery depends on the element:

| Element | Transverse displacement interpolation | Rotation interpolation |
|---|---:|---:|
| `ASDShellQ4` | Q4 | Q4 |
| `ShellMITC4` | Q4 | Q4 |
| `ShellMITC9` | Q9 | Q9 |
| `HeterosisPlate` | Q8 | Q9 |

The `HeterosisPlate` case is handled inside the recovery logic because its external OpenSees connectivity uses 9 shell nodes, while the physical plate interpolation uses Q8 transverse displacement and Q9 rotations.

## Prescribed Kinematic Field

The benchmark prescribes a linear transverse displacement field and linear rotation fields:

```text
w(x, y)       = w0       + wx       x + wy       y
theta_x(x, y) = theta_x0 + theta_xx x + theta_xy y
theta_y(x, y) = theta_y0 + theta_yx x + theta_yy y
```

The current numerical values are:

```python
w0 = 0.120
wx = 0.170
wy = -0.090

theta_x0 = 0.030
theta_xx = 0.041
theta_xy = -0.022

theta_y0 = -0.025
theta_yx = 0.033
theta_yy = 0.052
```

This field is exactly representable by Q4, Q8, and Q9 interpolation. Therefore, if the connectivity, geometry mapping, and strain recovery logic are correct, the numerical strain field should match the analytical strain field to machine precision.

## Strain Components Compared

At each sampling point, the benchmark recovers and compares the following generalized strain components:

```text
kappa_xx = theta_x,x
kappa_yy = theta_y,y
kappa_xy = theta_x,y + theta_y,x
gamma_xz = w,x - theta_x
gamma_yz = w,y - theta_y
```

The analytical values are obtained directly from the prescribed field:

```text
kappa_xx = theta_xx
kappa_yy = theta_yy
kappa_xy = theta_xy + theta_yx
gamma_xz = wx - theta_x(x, y)
gamma_yz = wy - theta_y(x, y)
```

The bending strain components are constant because the prescribed rotation fields are linear. The transverse shear strain components vary linearly because they include the rotation fields themselves.

## What the Test Verifies

The benchmark verifies that:

- The prescribed kinematic field is reproduced exactly by the selected interpolation basis.
- Shape-function derivatives are correctly transformed from parent coordinates to physical coordinates.
- The physical point associated with the transverse displacement interpolation matches the physical point associated with the rotation interpolation.
- The `HeterosisPlate` Q8/Q9 split is handled correctly.
- Distorted-element geometry does not break exact recovery of a representable field.

This is not a load-response benchmark. No equilibrium solution is being checked. The test is focused on interpolation and kinematic strain recovery.

## Sampling Points

The sampling points depend on the element order:

- Order 1 elements use 2 by 2 Gauss sampling.
- Order 2 elements use 3 by 3 Gauss sampling.

For each element, strains are sampled at all corresponding points and compared against the analytical values.

## Running the Test

From the `shell-0002` folder:

```bash
python -m pytest test_shell_0002.py -v -rs
```

Expected collection:

```text
test_distorted_patch_exact_strain_recovery[ASDShellQ4-1]
test_distorted_patch_exact_strain_recovery[HeterosisPlate-2]
test_distorted_patch_exact_strain_recovery[ShellMITC4-1]
test_distorted_patch_exact_strain_recovery[ShellMITC9-2]
test_distorted_patch_output_files_saved[ASDShellQ4-1]
test_distorted_patch_output_files_saved[HeterosisPlate-2]
test_distorted_patch_output_files_saved[ShellMITC4-1]
test_distorted_patch_output_files_saved[ShellMITC9-2]
```

The benchmark runs eight cases by default: two tests for each of the four element types.

## Diagnostic Outputs

The pytest diagnostics are written under:

```text
_outputs/patch_diagnostics/
```

The plotting utility writes patch figures under:

```text
_outputs/mesh_plots/
```

To regenerate the patch visualization:

```bash
python plot_shell_0002_mesh.py
```

By default, the plotting script creates both:

```text
_outputs/mesh_plots/HeterosisPlate_distorted_patch.html
_outputs/mesh_plots/HeterosisPlate_distorted_patch.png
```

The Matplotlib figure is intended for documentation and topology inspection. The VEUx figure is intended for interactive visualization.

## Notes on Interpretation

A passing result indicates that the selected interpolation basis can exactly recover the generalized strains of the prescribed representable field on the distorted patch.

A failure may indicate one of the following issues:

- Incorrect local node ordering.
- Incorrect Q8/Q9 treatment for `HeterosisPlate`.
- Incorrect parent-to-physical derivative transformation.
- Incompatible displacement and rotation geometry mappings.
- An unintended change in the shared patch geometry.
- An unavailable or changed element implementation in the active OpenSees/Xara build.

## References

[1] O. C. Zienkiewicz, R. L. Taylor, and S. Govindjee, *The Finite Element Method: Its Basis and Fundamentals*. Elsevier, 8th ed., Nov. 2024.

[2] T. J. R. Hughes, *The Finite Element Method: Linear Static and Dynamic Finite Element Analysis*. Englewood Cliffs, New Jersey: Prentice-Hall, 1987.