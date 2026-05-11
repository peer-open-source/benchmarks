"""
Self-contained distorted 5-element patch test for shell and plate elements.

The benchmark builds an enclosing five-element patch with an outer rectangular
boundary and a distorted inner quadrilateral. The patch topology is:

    E_top
E_left  E_center  E_right
    E_bottom

A representable linear kinematic field is prescribed:

    w(x, y)       = w0  + wx  x + wy  y
    theta_x(x, y) = tx0 + txx x + txy y
    theta_y(x, y) = ty0 + tyx x + tyy y

The recovered generalized strains are compared against the analytical values.
The interpolation used for strain recovery depends on the element:

    ASDShellQ4, ShellMITC4 : Q4 w and Q4 rotations
    ShellMITC9             : Q9 w and Q9 rotations
    HeterosisPlate         : Q8 w and Q9 rotations

The HeterosisPlate case is handled internally because its external OpenSees
connectivity uses 9 shell nodes, while the physical plate interpolation uses
Q8 transverse displacement and Q9 rotations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
import xara
from opensees.errors import XaraError

from _shell_0002_patch import (
    ELEMENT_ORDER,
    build_model,
    element_coordinates,
)


ABS_TOL = 1.0e-10

OUTPUT_DIR = Path(__file__).resolve().parent / "_outputs"

STRAIN_NAMES = (
    "kappa_xx",
    "kappa_yy",
    "kappa_xy",
    "gamma_xz",
    "gamma_yz",
)

GAUSS_2 = (
    -1.0 / np.sqrt(3.0),
    1.0 / np.sqrt(3.0),
)

GAUSS_3 = (
    -np.sqrt(3.0 / 5.0),
    0.0,
    np.sqrt(3.0 / 5.0),
)

GAUSS_POINTS_BY_ORDER = {
    1: tuple((xi, eta) for xi in GAUSS_2 for eta in GAUSS_2),
    2: tuple((xi, eta) for xi in GAUSS_3 for eta in GAUSS_3),
}


@dataclass(frozen=True)
class LinearPatchField:
    """Linear field exactly representable by all interpolations used here."""

    w0: float = 0.120
    wx: float = 0.170
    wy: float = -0.090

    tx0: float = 0.030
    txx: float = 0.041
    txy: float = -0.022

    ty0: float = -0.025
    tyx: float = 0.033
    tyy: float = 0.052

    def w(self, x: float, y: float) -> float:
        return self.w0 + self.wx * x + self.wy * y

    def theta_x(self, x: float, y: float) -> float:
        return self.tx0 + self.txx * x + self.txy * y

    def theta_y(self, x: float, y: float) -> float:
        return self.ty0 + self.tyx * x + self.tyy * y

    def expected_at(self, x: float, y: float) -> dict[str, float]:
        return {
            "kappa_xx": self.txx,
            "kappa_yy": self.tyy,
            "kappa_xy": self.txy + self.tyx,
            "gamma_xz": self.wx - self.theta_x(x, y),
            "gamma_yz": self.wy - self.theta_y(x, y),
        }


def is_heterosis_plate(element_name: str) -> bool:
    """Return true for the HeterosisPlate element."""
    return element_name.lower() == "heterosisplate"


def build_model_or_skip(element_name: str, mesh_order: int) -> xara.Model:
    """Build the patch model, skipping unavailable elements."""
    try:
        model = build_model(element_name, mesh_order)
    except XaraError as exc:
        if "unknown element type" in str(exc).lower():
            pytest.skip(f"{element_name} is not available in this OpenSees build.")
        raise

    assert len(model.getEleTags()) == 5
    return model


def q4_shape_values_and_derivatives(xi: float, eta: float) -> tuple[np.ndarray, np.ndarray]:
    """Return Q4 shape functions and derivatives in local-node order."""
    values = np.array(
        [
            0.25 * (1.0 - xi) * (1.0 - eta),
            0.25 * (1.0 + xi) * (1.0 - eta),
            0.25 * (1.0 + xi) * (1.0 + eta),
            0.25 * (1.0 - xi) * (1.0 + eta),
        ],
        dtype=float,
    )

    dxi = np.array(
        [
            -0.25 * (1.0 - eta),
            0.25 * (1.0 - eta),
            0.25 * (1.0 + eta),
            -0.25 * (1.0 + eta),
        ],
        dtype=float,
    )

    deta = np.array(
        [
            -0.25 * (1.0 - xi),
            -0.25 * (1.0 + xi),
            0.25 * (1.0 + xi),
            0.25 * (1.0 - xi),
        ],
        dtype=float,
    )

    return values, np.column_stack((dxi, deta))


def q8_shape_values_and_derivatives(xi: float, eta: float) -> tuple[np.ndarray, np.ndarray]:
    """Return Q8 serendipity shape functions and derivatives in local-node order."""
    values = np.array(
        [
            0.25 * (1.0 - xi) * (1.0 - eta) * (-xi - eta - 1.0),
            0.25 * (1.0 + xi) * (1.0 - eta) * (xi - eta - 1.0),
            0.25 * (1.0 + xi) * (1.0 + eta) * (xi + eta - 1.0),
            0.25 * (1.0 - xi) * (1.0 + eta) * (-xi + eta - 1.0),
            0.5 * (1.0 - xi**2) * (1.0 - eta),
            0.5 * (1.0 + xi) * (1.0 - eta**2),
            0.5 * (1.0 - xi**2) * (1.0 + eta),
            0.5 * (1.0 - xi) * (1.0 - eta**2),
        ],
        dtype=float,
    )

    dxi = np.array(
        [
            -0.5 * xi * eta + 0.5 * xi - 0.25 * eta**2 + 0.25 * eta,
            -0.5 * xi * eta + 0.5 * xi + 0.25 * eta**2 - 0.25 * eta,
            0.5 * xi * eta + 0.5 * xi + 0.25 * eta**2 + 0.25 * eta,
            0.5 * xi * eta + 0.5 * xi - 0.25 * eta**2 - 0.25 * eta,
            xi * eta - xi,
            0.5 - 0.5 * eta**2,
            -xi * eta - xi,
            0.5 * eta**2 - 0.5,
        ],
        dtype=float,
    )

    deta = np.array(
        [
            -0.25 * xi**2 - 0.5 * xi * eta + 0.25 * xi + 0.5 * eta,
            -0.25 * xi**2 + 0.5 * xi * eta - 0.25 * xi + 0.5 * eta,
            0.25 * xi**2 + 0.5 * xi * eta + 0.25 * xi + 0.5 * eta,
            0.25 * xi**2 - 0.5 * xi * eta - 0.25 * xi + 0.5 * eta,
            0.5 * xi**2 - 0.5,
            -xi * eta - eta,
            0.5 - 0.5 * xi**2,
            xi * eta - eta,
        ],
        dtype=float,
    )

    return values, np.column_stack((dxi, deta))


def q9_shape_values_and_derivatives(xi: float, eta: float) -> tuple[np.ndarray, np.ndarray]:
    """Return Q9 shape functions and derivatives in local-node order."""
    lx = np.array(
        [
            0.5 * xi * (xi - 1.0),
            1.0 - xi**2,
            0.5 * xi * (xi + 1.0),
        ],
        dtype=float,
    )
    ly = np.array(
        [
            0.5 * eta * (eta - 1.0),
            1.0 - eta**2,
            0.5 * eta * (eta + 1.0),
        ],
        dtype=float,
    )
    dlx = np.array([xi - 0.5, -2.0 * xi, xi + 0.5], dtype=float)
    dly = np.array([eta - 0.5, -2.0 * eta, eta + 0.5], dtype=float)

    pairs = (
        (0, 0),
        (2, 0),
        (2, 2),
        (0, 2),
        (1, 0),
        (2, 1),
        (1, 2),
        (0, 1),
        (1, 1),
    )

    values = np.array([lx[i] * ly[j] for i, j in pairs], dtype=float)
    dxi = np.array([dlx[i] * ly[j] for i, j in pairs], dtype=float)
    deta = np.array([lx[i] * dly[j] for i, j in pairs], dtype=float)

    return values, np.column_stack((dxi, deta))


def shape_values_and_derivatives(
    basis_name: str,
    xi: float,
    eta: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return shape functions and parent-coordinate derivatives."""
    if basis_name == "q4":
        return q4_shape_values_and_derivatives(xi, eta)

    if basis_name == "q8":
        return q8_shape_values_and_derivatives(xi, eta)

    if basis_name == "q9":
        return q9_shape_values_and_derivatives(xi, eta)

    raise ValueError(f"Unsupported interpolation basis: {basis_name}")


def basis_node_count(basis_name: str) -> int:
    """Return the number of local nodes used by an interpolation basis."""
    return {
        "q4": 4,
        "q8": 8,
        "q9": 9,
    }[basis_name]


def interpolation_bases(element_name: str, mesh_order: int) -> tuple[str, str]:
    """Return the transverse-displacement and rotation interpolation bases."""
    if is_heterosis_plate(element_name):
        return "q8", "q9"

    if mesh_order == 1:
        return "q4", "q4"

    if mesh_order == 2:
        return "q9", "q9"

    raise ValueError(f"Unsupported mesh order: {mesh_order}")


def sample_points(mesh_order: int) -> tuple[tuple[float, float], ...]:
    """Return sampling points for the requested element order."""
    return GAUSS_POINTS_BY_ORDER[mesh_order]


def shape_gradients_xy(
    natural_derivatives: np.ndarray,
    coordinates: np.ndarray,
) -> np.ndarray:
    """Transform shape-function derivatives from parent to physical coordinates."""
    x = coordinates[:, 0]
    y = coordinates[:, 1]

    jacobian = np.array(
        [
            [
                natural_derivatives[:, 0] @ x,
                natural_derivatives[:, 1] @ x,
            ],
            [
                natural_derivatives[:, 0] @ y,
                natural_derivatives[:, 1] @ y,
            ],
        ],
        dtype=float,
    )

    return natural_derivatives @ np.linalg.inv(jacobian)


def field_values(
    coordinates: np.ndarray,
    field: LinearPatchField,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return nodal values of w, theta_x, and theta_y."""
    w_values = np.array([field.w(x, y) for x, y in coordinates], dtype=float)
    theta_x_values = np.array([field.theta_x(x, y) for x, y in coordinates], dtype=float)
    theta_y_values = np.array([field.theta_y(x, y) for x, y in coordinates], dtype=float)

    return w_values, theta_x_values, theta_y_values


def recover_strains_at_point(
    xi: float,
    eta: float,
    coordinates_w: np.ndarray,
    coordinates_rotation: np.ndarray,
    w_values: np.ndarray,
    theta_x_values: np.ndarray,
    theta_y_values: np.ndarray,
    w_basis: str,
    rotation_basis: str,
) -> tuple[dict[str, float], tuple[float, float]]:
    """Recover generalized strains at one parent-coordinate point."""
    n_w, dn_w_parent = shape_values_and_derivatives(w_basis, xi, eta)
    n_rotation, dn_rotation_parent = shape_values_and_derivatives(
        rotation_basis,
        xi,
        eta,
    )

    dn_w_xy = shape_gradients_xy(dn_w_parent, coordinates_w)
    dn_rotation_xy = shape_gradients_xy(dn_rotation_parent, coordinates_rotation)

    xy_w = n_w @ coordinates_w
    xy_rotation = n_rotation @ coordinates_rotation

    np.testing.assert_allclose(
        xy_w,
        xy_rotation,
        atol=1.0e-12,
        err_msg="Displacement and rotation geometries are incompatible.",
    )

    w_x = dn_w_xy[:, 0] @ w_values
    w_y = dn_w_xy[:, 1] @ w_values

    theta_x = n_rotation @ theta_x_values
    theta_y = n_rotation @ theta_y_values

    theta_x_x = dn_rotation_xy[:, 0] @ theta_x_values
    theta_x_y = dn_rotation_xy[:, 1] @ theta_x_values
    theta_y_x = dn_rotation_xy[:, 0] @ theta_y_values
    theta_y_y = dn_rotation_xy[:, 1] @ theta_y_values

    strains = {
        "kappa_xx": theta_x_x,
        "kappa_yy": theta_y_y,
        "kappa_xy": theta_x_y + theta_y_x,
        "gamma_xz": w_x - theta_x,
        "gamma_yz": w_y - theta_y,
    }

    return strains, (float(xy_rotation[0]), float(xy_rotation[1]))


def sample_generalized_strains(
    model: xara.Model,
    element_name: str,
    mesh_order: int,
    field: LinearPatchField,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Recover generalized strains from the element interpolation."""
    w_basis, rotation_basis = interpolation_bases(element_name, mesh_order)

    sampled = {name: [] for name in STRAIN_NAMES}
    expected = {name: [] for name in STRAIN_NAMES}

    for element_tag in model.getEleTags():
        _, coordinates = element_coordinates(model, element_tag)

        w_node_count = basis_node_count(w_basis)
        rotation_node_count = basis_node_count(rotation_basis)

        coordinates_w = coordinates[:w_node_count]
        coordinates_rotation = coordinates[:rotation_node_count]

        w_values, _, _ = field_values(coordinates_w, field)
        _, theta_x_values, theta_y_values = field_values(coordinates_rotation, field)

        for xi, eta in sample_points(mesh_order):
            sampled_values, physical_point = recover_strains_at_point(
                xi=xi,
                eta=eta,
                coordinates_w=coordinates_w,
                coordinates_rotation=coordinates_rotation,
                w_values=w_values,
                theta_x_values=theta_x_values,
                theta_y_values=theta_y_values,
                w_basis=w_basis,
                rotation_basis=rotation_basis,
            )

            expected_values = field.expected_at(*physical_point)

            for name in STRAIN_NAMES:
                sampled[name].append(sampled_values[name])
                expected[name].append(expected_values[name])

    return (
        {name: np.asarray(values, dtype=float) for name, values in sampled.items()},
        {name: np.asarray(values, dtype=float) for name, values in expected.items()},
    )


def assert_exact_strain_recovery(element_name: str, mesh_order: int) -> None:
    """Verify exact generalized-strain recovery for one element type."""
    model = build_model_or_skip(element_name, mesh_order)
    field = LinearPatchField()

    sampled, expected = sample_generalized_strains(
        model=model,
        element_name=element_name,
        mesh_order=mesh_order,
        field=field,
    )

    for name in STRAIN_NAMES:
        np.testing.assert_allclose(
            sampled[name],
            expected[name],
            atol=ABS_TOL,
            err_msg=(
                f"{element_name} (order={mesh_order}) failed the distorted "
                f"patch strain-recovery test for {name}."
            ),
        )


def plot_patch_geometry(
    model: xara.Model,
    element_name: str,
    output_directory: Path,
) -> Path:
    """Write a geometry plot for manual inspection."""
    output_directory.mkdir(parents=True, exist_ok=True)
    path = output_directory / f"{element_name}_distorted_patch_geometry.png"

    fig, ax = plt.subplots(figsize=(7.0, 6.0))

    for element_tag in model.getEleTags():
        connectivity, coordinates = element_coordinates(model, element_tag)

        corner_coordinates = coordinates[[0, 1, 2, 3, 0], :]
        ax.plot(corner_coordinates[:, 0], corner_coordinates[:, 1], linewidth=1.5)
        ax.scatter(coordinates[:, 0], coordinates[:, 1], s=16)

        centroid = coordinates[:4].mean(axis=0)
        ax.text(
            centroid[0],
            centroid[1],
            str(element_tag),
            ha="center",
            va="center",
        )

        for node_tag, xy in zip(connectivity, coordinates, strict=True):
            ax.text(
                xy[0],
                xy[1],
                str(node_tag),
                fontsize=7,
                ha="left",
                va="bottom",
            )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"{element_name} distorted five-element patch")
    ax.grid(True, linewidth=0.4, alpha=0.5)

    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)

    return path


def plot_strain_errors(
    sampled: dict[str, np.ndarray],
    expected: dict[str, np.ndarray],
    element_name: str,
    output_directory: Path,
) -> Path:
    """Write a diagnostic plot of absolute strain-recovery errors."""
    output_directory.mkdir(parents=True, exist_ok=True)
    path = output_directory / f"{element_name}_distorted_patch_strain_errors.png"

    fig, ax = plt.subplots(figsize=(7.0, 4.5))

    for name in STRAIN_NAMES:
        error = np.abs(sampled[name] - expected[name])
        ax.plot(
            np.arange(error.size),
            error,
            marker="o",
            linestyle="none",
            label=name,
        )

    ax.set_yscale("log")
    ax.set_xlabel("sample index")
    ax.set_ylabel("absolute error")
    ax.set_title(f"{element_name} distorted patch strain-recovery errors")
    ax.grid(True, which="both", linewidth=0.4, alpha=0.5)
    ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)

    return path


def write_strain_report(
    sampled: dict[str, np.ndarray],
    expected: dict[str, np.ndarray],
    element_name: str,
    mesh_order: int,
    geometry_plot_path: Path,
    error_plot_path: Path,
    output_directory: Path,
) -> Path:
    """Write a compact strain-recovery report."""
    output_directory.mkdir(parents=True, exist_ok=True)
    path = output_directory / f"{element_name}_distorted_patch_strain_report.txt"

    lines = [
        f"{element_name} distorted five-element patch test",
        "",
        f"Element order: {mesh_order}",
        f"Geometry plot: {geometry_plot_path}",
        f"Error plot:    {error_plot_path}",
        "",
        "Maximum absolute errors:",
    ]

    for name in STRAIN_NAMES:
        error = np.abs(sampled[name] - expected[name])
        lines.append(f"  {name:10s}: {error.max():.16e}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def save_diagnostics(element_name: str, mesh_order: int) -> None:
    """Save geometry, strain-error plot, and text report."""
    model = build_model_or_skip(element_name, mesh_order)
    field = LinearPatchField()

    sampled, expected = sample_generalized_strains(
        model=model,
        element_name=element_name,
        mesh_order=mesh_order,
        field=field,
    )

    output_directory = OUTPUT_DIR / "patch_diagnostics"

    geometry_plot_path = plot_patch_geometry(
        model=model,
        element_name=element_name,
        output_directory=output_directory,
    )
    error_plot_path = plot_strain_errors(
        sampled=sampled,
        expected=expected,
        element_name=element_name,
        output_directory=output_directory,
    )
    report_path = write_strain_report(
        sampled=sampled,
        expected=expected,
        element_name=element_name,
        mesh_order=mesh_order,
        geometry_plot_path=geometry_plot_path,
        error_plot_path=error_plot_path,
        output_directory=output_directory,
    )

    assert geometry_plot_path.exists()
    assert error_plot_path.exists()
    assert report_path.exists()


@pytest.mark.parametrize("element_name,mesh_order", sorted(ELEMENT_ORDER.items()))
def test_distorted_patch_exact_strain_recovery(
    element_name: str,
    mesh_order: int,
) -> None:
    """Verify exact generalized-strain recovery on the distorted patch."""
    assert_exact_strain_recovery(element_name, mesh_order)


@pytest.mark.parametrize("element_name,mesh_order", sorted(ELEMENT_ORDER.items()))
def test_distorted_patch_output_files_saved(
    element_name: str,
    mesh_order: int,
) -> None:
    """Save geometry, strain-error plot, and text report for manual inspection."""
    save_diagnostics(element_name, mesh_order)