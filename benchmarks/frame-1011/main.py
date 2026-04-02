"""
Lateral buckling of a cantilever right-angle frame under end load.

Benchmark data
--------------
Units are N and mm.

Geometry:
    * two orthogonal legs of length L = 240 mm
    * rectangular section b x t = 30 mm x 0.6 mm

Material:
    * E = 71240 N/mm^2
    * nu = 0.31

Loading:
    * conservative in-plane tip load P in the global +x direction
    * small out-of-plane perturbation load P_s in the global +z direction

The benchmark description states that the perturbation is removed in a
neighborhood of the buckling load. The exact unloading function is not given in
text, so this script uses a piecewise-linear schedule that keeps P_s/P = 1e-3
up to a user-defined load factor and then ramps the perturbation to zero.
"""

import os
import sys
from dataclasses import dataclass
from typing import Any

import numpy as np
import matplotlib.pyplot as plt

import veux
from veux.motion import Motion

import xara

from xara.post import PlotConvergenceRate


@dataclass
class Geometry:
    node_tags: list[int]
    coords: np.ndarray
    fixed: int
    corner: int
    free: int


@dataclass
class SectionProps:
    A: float
    Iy: float
    Iz: float
    J: float
    G: float


@dataclass
class History:
    step: list[int]
    load: list[float]
    ux: list[float]
    uy: list[float]
    uz: list[float]


@dataclass
class Result:
    model: Any
    geometry: Geometry
    history: History
    motion: Any | None = None
    convergence: Any | None = None


def rectangular_section_properties(E: float, nu: float, b: float, t: float) -> SectionProps:
    """
    Section axes are chosen so that:
        * local y lies in the frame plane
        * local z is normal to the frame plane

    Therefore the large section dimension b lies along local y and the small
    thickness t lies along local z. Out-of-plane bending is then governed by Iy
    and is intentionally very weak.
    """
    G = E / (2.0 * (1.0 + nu))
    A = b * t
    Iy = b * t**3 / 12.0
    Iz = t * b**3 / 12.0

    # Saint-Venant torsion constant for a thin rectangle, t <= b.
    beta = t / b
    J = (b * t**3 / 3.0) * (1.0 - 0.63 * beta + 0.052 * beta**5)

    return SectionProps(A=A, Iy=Iy, Iz=Iz, J=J, G=G)


def create_model(
    ne_per_leg: int = 10,
    element: str = "ExactFrame",
    L: float = 240.0,
    b: float = 30.0,
    t: float = 0.6,
    E: float = 71240.0,
    nu: float = 0.31,
) -> tuple[Any, Geometry, SectionProps]:

    model = xara.Model(ndm=3, ndf=6)

    sec_tag = 1
    tr_tag = 1

    sec = rectangular_section_properties(E=E, nu=nu, b=b, t=t)

    model.section(
        "ElasticFrame",
        sec_tag,
        E=E,
        G=sec.G,
        A=sec.A,
        Ay=sec.A,
        Az=sec.A,
        Iy=sec.Iy,
        Iz=sec.Iz,
        J=sec.J,
    )

    # local z is out of the x-y frame plane.
    model.geomTransf("Corotational02", tr_tag, (0.0, 0.0, 1.0))

    coords: list[tuple[float, float, float]] = []

    # Horizontal leg: fixed end at (0, 0, 0), corner at (L, 0, 0).
    for x in np.linspace(0.0, L, ne_per_leg + 1):
        coords.append((float(x), 0.0, 0.0))

    corner_tag = ne_per_leg

    # Vertical leg: from the corner downward to the free end at (L, -L, 0).
    for y in np.linspace(-L / ne_per_leg, -L, ne_per_leg):
        coords.append((L, float(y), 0.0))

    for tag, xyz in enumerate(coords):
        model.node(tag, xyz)

    #
    # Elements
    #
    ele_tag = 1
    for i in range(ne_per_leg):
        model.element(
            element,
            ele_tag,
            (i, i + 1),
            section=sec_tag,
            transform=tr_tag
        )
        ele_tag += 1

    for i in range(ne_per_leg):
        ni = corner_tag + i
        nj = corner_tag + i + 1
        model.element(
            element,
            ele_tag,
            (ni, nj),
            section=sec_tag,
            transform=tr_tag
        )
        ele_tag += 1

    fixed_tag = 0
    free_tag = len(coords) - 1

    model.fix(fixed_tag, (1, 1, 1, 1, 1, 1))

    geometry = Geometry(
        node_tags=list(range(len(coords))),
        coords=np.asarray(coords, dtype=float),
        fixed=fixed_tag,
        corner=corner_tag,
        free=free_tag,
    )

    return model, geometry, sec


def apply_benchmark_loading(
    model: Any,
    free_tag: int,
    perturb_ratio: float = 1.0e-4,
    perturbation_window: tuple[float, float] = (1.05, 1.10),
) -> None:
    """
    Main load pattern:
        P = lambda in global +x at the free end.

    Perturbation pattern:
        P_s = perturb_ratio * P up to perturbation_window[0], then linearly
        unloaded to zero by perturbation_window[1].
    """
    lam_on, lam_off = perturbation_window
    if not (0.0 < lam_on < lam_off):
        raise ValueError("perturbation_window must satisfy 0 < start < end")

    # Main conservative in-plane load.
    model.pattern("Plain", 1, "Linear")
    model.load(free_tag, 1,0,0, 0,0,0, pattern=1)

    # Small out-of-plane perturbation used to select the buckling branch.

    # model.timeSeries(
    #     "Path",
    #     2,
    #     time=[0.0, lam_on, lam_off, 10.0],
    #     values=[0.0, perturb_ratio * lam_on, 0.0, 0.0],
    # )
    model.pattern("Plain", 2, "Constant")#, fact=perturb_ratio)
    model.load(free_tag, 0.0, 0.0, perturb_ratio, 0.0, 0.0, 0.0, pattern=2)



def plot_response(history: History) -> tuple[Any, Any]:
    fig, ax = plt.subplots()
    ax.set_xlabel("Lateral tip displacement, $w_z$ [mm]")
    ax.set_ylabel("End load, $P$ [N]")
    ax.axvline(0.0, color="black", linewidth=1.0)
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.plot(history.ux, history.load)
    ax.plot(history.uz, history.load)
    ax.set_xlim(left=0.0)
    ax.set_ylim(bottom=0.0)
    fig.tight_layout()
    print(history.uz)
    return fig, ax





def analyze(
    ne_per_leg,
    element: str = "ExactFrame",
    n_steps: int = 25,
    u_maxx: float = 60.0,
    perturb_ratio: float = 1.0e-8,
    perturbation_window: tuple[float, float] = (0.0, 1.10),
    post: list[Any] | None = None,
    show_plots: bool = True,
    render: bool = True,
) -> Result:

    model, geometry, _ = create_model(
        ne_per_leg=ne_per_leg,
        element=element,
    )

    apply_benchmark_loading(
        model,
        free_tag=geometry.free,
        perturb_ratio=perturb_ratio,
        perturbation_window=perturbation_window,
    )

    artist = None
    motion = None
    if render:
        artist = veux.create_artist(model, model_config=dict(extrude_outline="square"))
        artist.draw_nodes(size=10)
        artist.draw_sections()
        artist.draw_axes(extrude=True)
        motion = Motion(artist)

    model.constraints("Transformation")
    model.numberer("RCM")
    model.system("BandGeneral")
    model.integrator("DisplacementControl", geometry.free, 1, u_maxx / n_steps)
    model.test("Energy", 1.0e-12, 400, 2)
    model.algorithm("Newton")
    model.analysis("Static")

    history = History(step=[], load=[], ux=[], uy=[], uz=[])

    speed = 1.0 / max(n_steps, 1)
    for step in range(1, n_steps + 1):
        print(model.state.time)
        ok = model.analyze(1)
        if ok != 0:
            last = history.uz[-1] if history.uz else 0.0
            print(
                f"Analysis failed at step {step} with load factor {model.getTime():.6g} "
                f"and lateral tip displacement {last:.6g}",
                file=sys.stderr,
            )
            break
        
        if model.state.time > perturbation_window[1]:
            model.remove("loadPattern", 2)
            print(f"Perturbation removed at load factor {model.getTime():.6g}")

        if motion is not None:
            motion.advance(time=step * speed)
            motion.draw_sections(rotation=model.nodeRotation, position=model.nodeDisp)

        history.step.append(step)
        history.load.append(model.getTime())
        history.ux.append(model.nodeDisp(geometry.free, 1))
        history.uy.append(model.nodeDisp(geometry.free, 2))
        history.uz.append(model.nodeDisp(geometry.free, 3))

        if post is not None:
            for p in post:
                p.update(model)


    convergence = None
    if post:
        convergence = post[-1]
        if hasattr(convergence, "draw"):
            convergence.draw()
        if hasattr(convergence, "finalize"):
            convergence.finalize()

    if show_plots:
        plot_response(history)
        plt.show()

    if motion is not None and artist is not None:
        motion.add_to(artist.canvas)
        if len(sys.argv) > 1:
            artist.save(sys.argv[1])
        else:
            veux.serve(artist)

    return Result(
        model=model,
        geometry=geometry,
        history=history,
        motion=motion,
        convergence=convergence,
    )


if __name__ == "__main__":
    element = os.environ.get("Element", "ExactFrame")

    perturbation_window_env = os.environ.get("PERTURB_WINDOW", "1.05,1.10")
    lam_on_str, lam_off_str = perturbation_window_env.split(",", maxsplit=1)

    post = None
    if PlotConvergenceRate is not None:
        post = [PlotConvergenceRate(ci=None, x_mode="step", n_ex_start=0)]

    analyze(
        element=element,
        ne_per_leg=10,
        n_steps=500, #25*60, #
        u_maxx=60.0,
        perturb_ratio=1e-4,
        perturbation_window=(1.0, 1.09),
        post=post,
        show_plots=True,
        render=veux is not None,
    )
