#!/usr/bin/env python3
#
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
        x = self.span/np.sqrt(2)
        z = x/800

        coords = {
            1: ( x ,   0.0, 0.0),
            2: (0.0,    x ,  z ),
        }
        for tag, loc in coords.items():
            model.node(tag, loc)

        #
        # --- boundary conditions
        #     pinned = fix all translations, free rotations
        #
        model.fix(1, (0,1,1,  1,1,0))   # column base
        model.fix(2, (1,0,0,  0,0,1))   # joint

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
        dy = x / ne
        dz = z / ne
        last = 1
        for k in range(1, ne):
            model.node(next_node, (x-k*dy, k*dy, k*dz))
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


        return model


# ---------------------------------------------------------------------- #
# driver
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    #
    # material & section
    #
    E = 71_240.0         # MPa
    G = 27_191.0         # MPa
    b, a = 0.30, 0.06    #
    A = b * a
    Iy = (b * a**3) / 12        # weak axis
    Iz = (a * b**3) / 12        # strong
    shape = Rectangle(b,a)
    J = shape._analysis.torsion_constant()
    print(f"{J = }")

    #
    # geometry
    #
    height = 2.4      # m
    span   = 2.4      # m

    frame = LeesFrame(
        height   = height,
        span     = span,
        element  = os.environ.get("Element", "ExactFrame"),
        section  = dict(E=E, G=G, A=A, J=J, Iy=Iy, Iz=Iz, Ay=A, Az=A),
        divisions=  9,
        transform= "Corotational02",
        shear    = True,
    )

    model = frame.create_model()

    #
    # reference load: NL7 uses PL²/EI = 31.887 at peak
    #
    steps = 200

    tol = 1e-16
    model.test("EnergyIncr", tol, 10, 1)
    model.algorithm("NewtonLineSearch")

#   model.pattern("Plain", 2, "Constant",
#                 load={2: [0, 0, 0, 0, 0, 0]})
    model.pattern(
        "Plain",
        1,
        "Linear",
        load={
            1: (0.0, 0.0, 0.0, 0.0, 0.0, -1./steps),
        },
    )
    model.integrator("MinUnbalDispNorm", 1, 5, 1/20, 1)
#   model.integrator("ArcLength", 0.5, det=True)
    model.system("Umfpack")
    model.analysis("Static")

    #
    # post-processing
    #
    artist = veux.create_artist(model, model_config=dict(extrude_outline=shape))
    artist.draw_axes()
    artist.draw_origin()
    artist.draw_outlines()
#   veux.serve(artist)
    motion = Motion(artist)

    uy = []
    lam = []
    speed = 0.1
    n = 0
    for _ in range(steps*80):
#   while -model.nodeDisp(8,2)/span < 0.77 and n < 2000:
        n += 1
        motion.advance(time=model.getTime()/speed)
        try:
            motion.draw_sections(rotation=model.nodeRotation,
                                 position=model.nodeDisp)
        except Exception as e:
            raise e
            print("Bad rotation")
            break
        uy.append(-model.nodeDisp(2, 3) / span)      # normalised vertical disp.
        lam.append(model.getLoadFactor(1))

        if model.analyze(1) != 0:
            if tol >= 1e-8:
                break
            tol *= 5
            model.test("EnergyIncr", tol, 10, 1)
        elif tol > 1e-10:
            tol /= 10

    print(f"time = {model.getTime()}")


    motion.add_to(artist.canvas)
    veux.serve(artist)

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot(uy, lam, "-")
    ax.set_xlabel(r"Normalised vertical displacement $w/L$")
    ax.set_ylabel(r"Load factor $\lambda$")
    ax.set_title("Lee's frame – equilibrium path")
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.axhline(0, color='black', linestyle='-', linewidth=1)


    fig, ax = plt.subplots()
    ax.plot(lam)
    plt.show()


