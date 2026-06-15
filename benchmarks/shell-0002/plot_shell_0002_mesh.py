"""
Standalone patch-plot utility for benchmark shell-0002.

This script uses the shared distorted-patch geometry from
``_shell_0002_patch.py``. Therefore, the plotting utility and the pytest
benchmark always use the same patch definition.

Default behavior
----------------
Both plotting engines are used by default. Running the script without flags
generates:

    1. an interactive VEUx/Plotly HTML file
    2. a static Matplotlib PNG file

For example:

    python plot_shell_0002_mesh.py

renders the default HeterosisPlate patch with both engines.

Important plotting convention
-----------------------------
This script plots the patch topology, not the element interpolation topology.
Therefore, it does not distinguish Q4, Q8, Q9, midside nodes, or center nodes.
The same five-region patch is used by all element types in the benchmark.

To avoid misleading visual overlap:

    - shared patch edges are drawn only once in Matplotlib
    - VEUx receives one quadrilateral panel per patch region
    - no artificial triangular subdivision is used
    - no repeated finite-element nodes are plotted

Examples
--------
Render the default HeterosisPlate patch with both engines:

    python plot_shell_0002_mesh.py

Render a specific element label with both engines:

    python plot_shell_0002_mesh.py --element ShellMITC9

Render all element labels with both engines:

    python plot_shell_0002_mesh.py --all

Render only the VEUx HTML file:

    python plot_shell_0002_mesh.py --renderer veux

Render only the Matplotlib PNG file:

    python plot_shell_0002_mesh.py --renderer matplotlib
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from opensees.errors import XaraError

from _shell_0002_patch import (
    ELEMENT_ORDER,
    PATCH_BLOCKS,
    build_model,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "_outputs" / "mesh_plots"


def default_veux_path(element_name: str, canvas: str) -> Path:
    """Return the default VEUx output path."""
    suffix_by_canvas = {
        "plotly": ".html",
        "gltf": ".glb",
    }

    return OUTPUT_DIR / f"{element_name}_distorted_patch{suffix_by_canvas[canvas]}"


def default_matplotlib_path(element_name: str) -> Path:
    """Return the default Matplotlib output path."""
    return OUTPUT_DIR / f"{element_name}_distorted_patch.png"


def coordinate_key(point: tuple[float, float], decimals: int = 12) -> tuple[float, float]:
    """Return a stable key for identifying repeated patch coordinates."""
    return (round(float(point[0]), decimals), round(float(point[1]), decimals))


def unique_patch_nodes() -> dict[tuple[float, float], int]:
    """Return unique patch coordinates mapped to visualization node tags."""
    coordinate_to_tag: dict[tuple[float, float], int] = {}

    for corners in PATCH_BLOCKS.values():
        for point in corners:
            key = coordinate_key(point)

            if key not in coordinate_to_tag:
                coordinate_to_tag[key] = len(coordinate_to_tag) + 1

    return coordinate_to_tag


def unique_patch_edges() -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """
    Return unique patch edges.

    Adjacent regions share edges. The edge key is orientation-independent so
    each shared edge is drawn only once.
    """
    edge_by_key: dict[
        tuple[tuple[float, float], tuple[float, float]],
        tuple[tuple[float, float], tuple[float, float]],
    ] = {}

    for corners in PATCH_BLOCKS.values():
        ordered_points = [coordinate_key(point) for point in corners]

        for start, end in zip(
            ordered_points,
            ordered_points[1:] + ordered_points[:1],
            strict=True,
        ):
            edge_key = tuple(sorted((start, end)))

            if edge_key not in edge_by_key:
                edge_by_key[edge_key] = (start, end)

    return list(edge_by_key.values())


def patch_region_centroid(corners: list[tuple[float, float]]) -> np.ndarray:
    """Return the centroid of a patch region."""
    coordinates = np.asarray(corners, dtype=float)
    return coordinates.mean(axis=0)


def patch_label(region_name: str) -> str:
    """Return a formatted label for a patch region."""
    return rf"$E_{{\mathrm{{{region_name}}}}}$"


def verify_element_available(element_name: str) -> int:
    """
    Build the requested Xara model to verify that the element is available.

    The returned model is not used for plotting. The plot is based on
    PATCH_BLOCKS so the displayed geometry stays identical for all elements.
    """
    mesh_order = ELEMENT_ORDER[element_name]

    try:
        build_model(element_name, mesh_order)
    except XaraError as exc:
        if "unknown element type" in str(exc).lower():
            raise RuntimeError(
                f"{element_name} is not available in this OpenSees build."
            ) from exc
        raise

    return mesh_order


def veux_patch_model() -> dict[str, Any]:
    """
    Convert PATCH_BLOCKS into a VEUx-friendly quadrilateral surface model.

    This model is for visualization only. It contains one four-node
    quadrilateral panel per patch region.
    """
    coordinate_to_tag = unique_patch_nodes()

    nodes = []
    for coordinate, tag in sorted(
        coordinate_to_tag.items(),
        key=lambda item: item[1],
    ):
        x, y = coordinate
        nodes.append(
            {
                "name": tag,
                "crd": [float(x), float(y), 0.0],
            }
        )

    elements = []
    for element_tag, corners in enumerate(PATCH_BLOCKS.values(), start=1):
        nodes_for_region = [
            coordinate_to_tag[coordinate_key(point)]
            for point in corners
        ]

        elements.append(
            {
                "name": element_tag,
                "type": "ShellMITC4",
                "nodes": nodes_for_region,
            }
        )

    return {
        "StructuralAnalysisModel": {
            "properties": {
                "sections": [],
                "nDMaterials": [],
                "uniaxialMaterials": [],
                "crdTransformations": [],
                "patterns": [],
                "parameters": [],
            },
            "geometry": {
                "nodes": nodes,
                "elements": elements,
                "constraints": [],
            },
        }
    }


def save_veux_artist(artist: Any, output_path: Path) -> None:
    """Save a VEUx artist."""
    if not hasattr(artist, "save"):
        raise RuntimeError("The VEUx artist does not expose a save() method.")

    artist.save(str(output_path))


def serve_veux_artist(artist: Any) -> None:
    """Serve a VEUx artist locally."""
    import veux

    veux.serve(artist)


def render_with_veux(
    output_path: Path,
    canvas: str,
    serve: bool,
) -> Path:
    """Render the five-region patch with VEUx."""
    import veux

    output_path.parent.mkdir(parents=True, exist_ok=True)

    artist = veux.render(
        veux_patch_model(),
        canvas=canvas,
        vertical=3,
    )

    save_veux_artist(artist, output_path)

    if serve:
        serve_veux_artist(artist)

    return output_path


def render_with_matplotlib(
    element_name: str,
    output_path: Path,
    show_region_labels: bool,
) -> Path:
    """
    Render the five-region patch with Matplotlib.

    The plot uses unique patch edges, so shared internal boundaries are not
    drawn repeatedly.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(5.2, 4.6))

    for start, end in unique_patch_edges():
        x_values = [start[0], end[0]]
        y_values = [start[1], end[1]]

        ax.plot(
            x_values,
            y_values,
            color="black",
            linewidth=1.1,
        )

    if show_region_labels:
        for region_name, corners in PATCH_BLOCKS.items():
            centroid = patch_region_centroid(corners)
            ax.text(
                centroid[0],
                centroid[1],
                patch_label(region_name),
                ha="center",
                va="center",
                fontsize=8,
            )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x (unitless)", fontsize=9)
    ax.set_ylabel("y (unitless)", fontsize=9)
    ax.set_title(
        f"{element_name}: distorted 5-element patch",
        fontsize=10,
    )

    ax.grid(True, linewidth=0.35, alpha=0.25)
    ax.tick_params(labelsize=8)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    return output_path


def plot_patch(
    element_name: str,
    renderer: str,
    canvas: str,
    output_path: Path | None,
    serve: bool,
    show_region_labels: bool,
) -> list[Path]:
    """
    Plot the shared distorted patch.

    When both renderers are requested, the optional output path is ignored so
    that each renderer can use its own default file extension.
    """
    mesh_order = verify_element_available(element_name)

    print(
        f"Rendering shared patch for element label: "
        f"{element_name} (mesh order {mesh_order})"
    )
    print("Displayed patch geometry is identical for all element types.")

    written_paths: list[Path] = []

    if renderer in {"both", "veux"}:
        veux_path = output_path if renderer == "veux" else None
        path = render_with_veux(
            output_path=veux_path or default_veux_path(element_name, canvas),
            canvas=canvas,
            serve=serve,
        )
        written_paths.append(path)
        print(f"Wrote VEUx patch plot: {path}")

    if renderer in {"both", "matplotlib"}:
        matplotlib_path = output_path if renderer == "matplotlib" else None
        path = render_with_matplotlib(
            element_name=element_name,
            output_path=matplotlib_path or default_matplotlib_path(element_name),
            show_region_labels=show_region_labels,
        )
        written_paths.append(path)
        print(f"Wrote Matplotlib patch plot: {path}")

    return written_paths


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate patch plots for the shell-0002 distorted patch.",
    )

    element_group = parser.add_mutually_exclusive_group()
    element_group.add_argument(
        "--element",
        choices=sorted(ELEMENT_ORDER),
        default="HeterosisPlate",
        help="Element label to render. Defaults to HeterosisPlate.",
    )
    element_group.add_argument(
        "--all",
        action="store_true",
        help="Render plots for all element labels.",
    )

    parser.add_argument(
        "--renderer",
        choices=("both", "veux", "matplotlib"),
        default="both",
        help=(
            "Renderer to use. Defaults to both, which writes one VEUx HTML "
            "file and one Matplotlib PNG file."
        ),
    )
    parser.add_argument(
        "--canvas",
        choices=("plotly", "gltf"),
        default="plotly",
        help="VEUx canvas. Defaults to plotly.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "Output path for single-renderer mode. Ignored when "
            "--renderer both or --all is used."
        ),
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve the VEUx rendering locally after writing the output file.",
    )
    parser.add_argument(
        "--no-region-labels",
        action="store_true",
        help="Hide patch-region labels in the Matplotlib plot.",
    )

    return parser.parse_args()


def main() -> None:
    """Run the patch-plot utility."""
    args = parse_arguments()

    element_names = sorted(ELEMENT_ORDER) if args.all else [args.element]

    for element_name in element_names:
        output_path = None if args.all else args.out

        plot_patch(
            element_name=element_name,
            renderer=args.renderer,
            canvas=args.canvas,
            output_path=output_path,
            serve=args.serve,
            show_region_labels=not args.no_region_labels,
        )


if __name__ == "__main__":
    main()