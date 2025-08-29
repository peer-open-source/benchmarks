#!/usr/bin/env python3
#
# Lee’s frame – classic large-rotation benchmark
#   geometry and reference load values from NAFEMS NL7 / Lee et al. (1971)
#
import os
import xara
import numpy as np
import veux
from veux.motion import Motion
from xsection.library import Channel, Rectangle


class LeesFrame:
    """
    Single column + single girder (right-angle frame).

    Column base pinned, far end of girder pinned.
    Load acts vertically downward at the column-girder joint.
    """

    def __init__(
        self,
        height: float,
        span: float,
        element: str,
        section: dict,
        divisions: int = 4,
        transform: str = "Corotational02",
        shear: bool = True,
    ):
        self.height = height
        self.span = span
        self.element = element
        self.section = section
        self.divisions = divisions          # elements per member
        self.transform = transform
        self.use_shear = shear

    def create_model(self, file=None):
        if file is not None:
            file = open(file, "w+")

        model = xara.Model(ndm=3, ndf=6, echo_file=file)

        #
        # --- nodes ------------------------------------------------------ #
        #
        # node 1: column base
        # node 2: beam-column joint (load point)
        # node 3: girder far end
        #
        h = self.height
        L = self.span

        coords = {
            1: (0.0,   0.0, 0.0),
            2: (0.0,     h, 0.0),
            3: (  L,     h, 0.0),
        }
        for tag, loc in coords.items():
            model.node(tag, loc)

        #
        # --- boundary conditions
        #     pinned = fix all translations, free rotations
        #
        model.fix(1, (1,1,1,  0,1,0))   # column base
        model.fix(2, (0,0,1,  0,0,0))   # joint
        model.fix(3, (1,1,1,  1,0,0))   # girder far end

        #
        # --- section & transformation ---------------------------------- #
        #
        sec_tag = 1
        props = []
        for k, v in self.section.items():
            props.extend(["-" + k, v])
        model.section("ElasticFrame", sec_tag, *props)

        geo_tag = 1
        model.geomTransf(self.transform, geo_tag, 0, 0, 1)

        #
        # --- discretise members ---------------------------------------- #
        #
        ne = self.divisions
        n_internal = ne - 1
        elem_id = 1
        next_node = 4

        # column (1 → 2)
        dy = h / ne
        last = 1
        for k in range(1, ne):
            y = k * dy
            model.node(next_node, (0.0, y, 0.0))
            model.element(
                self.element,
                elem_id,
                (last, next_node),
                section=sec_tag,
                transform=geo_tag,
                shear=int(self.use_shear),
            )
            last = next_node
            next_node += 1
            elem_id += 1
        model.element(
            self.element,
            elem_id,
            (last, 2),
            section=sec_tag,
            transform=geo_tag,
            shear=int(self.use_shear),
        )
        elem_id += 1

        # girder (2 → 3)
        dx = L / ne
        last = 2
        for k in range(1, ne):
            x = k * dx
            model.node(next_node, (x, h, 0.0))
            model.element(
                self.element,
                elem_id,
                (last, next_node),
                section=sec_tag,
                transform=geo_tag,
                shear=int(self.use_shear),
            )
            last = next_node
            next_node += 1
            elem_id += 1
        model.element(
            self.element,
            elem_id,
            (last, 3),
            section=sec_tag,
            transform=geo_tag,
            shear=int(self.use_shear),
        )

        return model


# ---------------------------------------------------------------------- #
# driver
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    #
    # material & section
    #
    E = 71_740.0         # MPa   (same order as NAFEMS NL7)
    G = 27_590.0         # MPa
    b, a = 0.03, 0.02    # 30 × 20 mm rectangular section
    A = b * a
    I = (b * a**3) / 12        # strong axis (≈ 2 · 10⁻⁸ m⁴)
    J = 2.8*I # 2e-8           # torsion (placeholder)

    #
    # geometry
    #
    height = 1.2      # m
    span   = 1.2      # m

    frame = LeesFrame(
        height   = height,
        span     = span,
        element  = os.environ.get("Element", "ExactFrame"),
        section  = dict(E=E, G=G, A=A, J=J, Iy=I, Iz=I, Ay=A, Az=A),
        divisions= 5,          # 5 elements per member (matches NL7 mesh)
        transform= "Corotational02",
        shear    = True,
    )

    model = frame.create_model()

    #
    # reference load: NL7 uses PL²/EI = 31.887 at peak
    #
    Pref = 31.887 * E * I / (span ** 2)      # N
    steps = 20

    model.test("EnergyIncr", 1e-8, 50, 1)
    model.pattern(
        "Plain",
        1,
        "Linear",
        load={
            8: (0.0, -Pref/steps, 0.0, 0.0, 0.0, 0.0),
        },
    )
    model.integrator("MinUnbalDispNorm", 1, 4, 1/100, 1) #, det=True)
#   model.integrator("ArcLength", 0.1, det=True)
    model.system("Umfpack", det=True)
    model.analysis("Static")

    #
    # post-processing
    #
    artist = veux.create_artist(model, model_config=dict(extrude_outline=Rectangle(b,a)))
    artist.draw_axes()
    artist.draw_outlines()
#   veux.serve(artist)
    motion = Motion(artist)

    uy = []
    lam = []
    speed = 0.1
#   for _ in range(steps*3):
    n = 0
    while -model.nodeDisp(8,2)/span < 0.77 and n < 2000:
        n += 1
        motion.advance(time=model.getTime()/speed)
        motion.draw_sections(rotation=model.nodeRotation,
                             position=model.nodeDisp)
        uy.append(-model.nodeDisp(8, 2) / span)      # normalised vertical disp.
        lam.append(model.getLoadFactor(1))

        if model.analyze(1) != 0:
            break


    motion.add_to(artist.canvas)
    veux.serve(artist)

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot(uy, lam, ".-")
    ax.set_xlabel(r"Normalised vertical displacement $w/L$")
    ax.set_ylabel(r"Load factor $\lambda$")
    ax.set_title("Lee's frame – equilibrium path")
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.axhline(0, color='black', linestyle='-', linewidth=1)


    fig, ax = plt.subplots()
    ax.plot(lam)
    plt.show()


